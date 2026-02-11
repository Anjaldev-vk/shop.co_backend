from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, LoginView,
    ResendOTPView, UserProfileView, ChangePasswordView,
    PasswordResetRequestView, PasswordResetConfirmView, LogoutView, CookieTokenRefreshView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),

    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
