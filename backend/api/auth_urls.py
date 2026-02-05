"""
URL configuration for Authentication API endpoints.

All routes are prefixed with /api/auth/ when included in the main urlpatterns.

Endpoints:
    POST /api/auth/register/              - Register new user (sends OTP)
    POST /api/auth/verify-signup-otp/     - Verify signup OTP and activate account
    POST /api/auth/login/                 - Login with email/password
    POST /api/auth/request-password-reset/ - Request password reset OTP
    POST /api/auth/verify-reset-otp/      - Verify password reset OTP
    POST /api/auth/reset-password/        - Reset password with OTP
    POST /api/auth/resend-otp/            - Resend OTP (for signup or password reset)
"""
from django.urls import path
from . import auth_views

app_name = 'auth'

urlpatterns = [
    # Signup flow
    path('register/', auth_views.register, name='register'),
    path('verify-signup-otp/', auth_views.verify_signup_otp, name='verify-signup-otp'),
    
    # Login
    path('login/', auth_views.login, name='login'),
    
    # Password reset flow
    path('request-password-reset/', auth_views.request_password_reset, name='request-password-reset'),
    path('verify-reset-otp/', auth_views.verify_reset_otp, name='verify-reset-otp'),
    path('reset-password/', auth_views.reset_password, name='reset-password'),
    
    # Utility
    path('resend-otp/', auth_views.resend_otp, name='resend-otp'),
]
