from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, LoginSerializer,
    ResendOTPSerializer, UserProfileSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import User
from .utils import generate_otp, get_otp_expiry



# ------------------------Register User & Generate OTP-------------------------
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        otp = generate_otp()
        otp_expiry = get_otp_expiry()

        user = serializer.save(
            otp=otp,
            otp_expiry=otp_expiry,
            is_verified=False
        )

        return Response(
            {
                "message": "User registered successfully. Verify OTP.",
                "email": user.email,
                "otp": otp
            },
            status=status.HTTP_201_CREATED
        )


# -----------------------------Verify OTP------------------------------
class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_blocked:
            return Response(
                {"error": "Account is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_otp_valid():
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp != otp:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP is valid → verify account
        user.is_verified = True
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response(
            {"message": "Account verified successfully"},
            status=status.HTTP_200_OK
        )


# -----------------------------Resend OTP------------------------------
class ResendOTPView(APIView):
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_blocked:
            return Response(
                {"error": "Account is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_verified:
            return Response(
                {"message": "Account is already verified"},
                status=status.HTTP_200_OK
            )

        # Generate new OTP
        otp = generate_otp()
        otp_expiry = get_otp_expiry()

        user.otp = otp
        user.otp_expiry = otp_expiry
        user.save()


        return Response(
            {
                "message": "OTP sent successfully",
                "otp": otp
            },
            status=status.HTTP_200_OK
        )


# ----------------------------------Login (JWT)------------------------------
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(email=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_verified:
            return Response(
                {"error": "Account not verified"},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.is_blocked:
            return Response(
                {"error": "Account is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        print(refresh)

        response =  Response(
            {
                # "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            },
            status=status.HTTP_200_OK
        )

        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        return response


# -----------------------------User Profile------------------------------
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# -----------------------------Change Password------------------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']

        if not user.check_password(old_password):
            return Response(
                {"error": "Incorrect old password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )


# -----------------------------Forgot Password------------------------------
class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:

            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_blocked:
            return Response(
                {"error": "Account is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )


        otp = generate_otp()
        otp_expiry = get_otp_expiry()

        user.otp = otp
        user.otp_expiry = otp_expiry
        user.save()


        return Response(
            {
                "message": "OTP sent to email",
                "otp": otp
            },
            status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_blocked:
            return Response(
                {"error": "Account is blocked"},
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_otp_valid():
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.otp != otp:
             return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # OTP is valid, reset password
        user.set_password(new_password)
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK
        )
# -----------------------------Logout------------------------------

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )

        response = Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK
        )

        # Delete refresh token cookie
        response.delete_cookie('refresh_token')

        return response
