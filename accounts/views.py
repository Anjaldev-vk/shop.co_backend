from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings

from .serializers import (
    RegisterSerializer, VerifyOTPSerializer, LoginSerializer,
    ResendOTPSerializer, UserProfileSerializer, ChangePasswordSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import User
from .utils import generate_otp, get_otp_expiry, send_otp_email


# ------------------------ Register ------------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

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

        send_otp_email(user.email, otp, "Account Verification")

        return Response(
            {"message": "User registered successfully. OTP sent to email."},
            status=status.HTTP_201_CREATED
        )


# ------------------------ Verify OTP ------------------------
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_blocked:
            return Response({"error": "Account is blocked"}, status=403)

        if not user.is_otp_valid():
            return Response({"error": "OTP expired"}, status=400)

        if user.otp != otp:
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_verified = True
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response({"message": "Account verified successfully"}, status=200)


# ------------------------ Resend OTP ------------------------
class ResendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_blocked:
            return Response({"error": "Account is blocked"}, status=403)

        if user.is_verified:
            return Response({"message": "Account already verified"}, status=200)

        otp = generate_otp()
        user.otp = otp
        user.otp_expiry = get_otp_expiry()
        user.save()

        send_otp_email(user.email, otp, "OTP Resend")

        return Response({"message": "OTP sent to email"}, status=200)


# ------------------------ Login ------------------------
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"]
        )

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_verified:
            return Response({"error": "Account not verified"}, status=403)

        if user.is_blocked:
            return Response({"error": "Account is blocked"}, status=403)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response({
            "access": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
            },
        }, status=200)

        # Secure Refresh Cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )

        return response


# ------------------------ User Profile ------------------------
class UserProfileView(RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ------------------------ Change Password ------------------------
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"error": "Incorrect old password"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response({"message": "Password changed successfully"}, status=200)


# ------------------------ Forgot Password ------------------------
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_blocked:
            return Response({"error": "Account is blocked"}, status=403)

        otp = generate_otp()
        user.otp = otp
        user.otp_expiry = get_otp_expiry()
        user.save()

        send_otp_email(user.email, otp, "Password Reset")

        return Response({"message": "OTP sent to email"}, status=200)


# ------------------------ Reset Password ------------------------
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        if user.is_blocked:
            return Response({"error": "Account is blocked"}, status=403)

        if not user.is_otp_valid():
            return Response({"error": "OTP expired"}, status=400)

        if user.otp != serializer.validated_data["otp"]:
            return Response({"error": "Invalid OTP"}, status=400)

        user.set_password(serializer.validated_data["new_password"])
        user.otp = None
        user.otp_expiry = None
        user.save()

        return Response({"message": "Password reset successfully"}, status=200)


# ------------------------ Logout ------------------------
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response({"message": "Logged out successfully"}, status=200)

        response.delete_cookie(
            key="refresh_token",
            path="/",
            samesite="None",
        )

        return response


# ------------------------ Refresh Token ------------------------
class CookieTokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response({"error": "Refresh token missing"}, status=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            response = Response({"access": access_token}, status=200)

            # rotate refresh token
            if settings.SIMPLE_JWT["ROTATE_REFRESH_TOKENS"]:
                response.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    secure=True,
                    samesite="None",
                    path="/",
                )

            return response

        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=401)
