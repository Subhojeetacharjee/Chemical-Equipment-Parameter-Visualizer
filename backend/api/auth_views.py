"""
Authentication Views for OTP-based authentication.

Provides API endpoints for:
- User registration with email verification (POST /api/auth/register/)
- OTP verification for signup (POST /api/auth/verify-signup-otp/)
- Login with email and password (POST /api/auth/login/)
- Password reset request (POST /api/auth/request-password-reset/)
- Password reset OTP verification (POST /api/auth/verify-reset-otp/)
- Password reset completion (POST /api/auth/reset-password/)
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import logging

from .auth_serializers import (
    RegisterSerializer,
    VerifySignupOTPSerializer,
    LoginSerializer,
    RequestPasswordResetSerializer,
    VerifyResetOTPSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)
from .services.otp_service import OTPService

logger = logging.getLogger(__name__)


class OTPRateThrottle(AnonRateThrottle):
    """
    Custom throttle for OTP-related endpoints.
    Limits to 5 requests per minute per IP to prevent abuse.
    """
    rate = '5/minute'


def get_tokens_for_user(user):
    """
    Generate JWT tokens for authenticated user.
    
    Args:
        user: Django User instance
        
    Returns:
        dict with 'access' and 'refresh' tokens
    """
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


# =============================================================================
# SIGNUP ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def register(request):
    """
    Register a new user account.
    
    Creates an inactive user and sends OTP for email verification.
    
    Request Body:
        - email (required): Valid email address
        - password (required): Password (min 8 chars)
        - confirm_password (required): Must match password
        - name (optional): Full name
    
    Response (201):
        - message: Success message
        - otp_required: True (indicates OTP verification needed)
        - email: The email address to verify
    
    Errors:
        - 400: Validation errors
        - 429: Rate limit exceeded
    """
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create inactive user
    user = serializer.save()
    
    # Send verification OTP
    success, message = OTPService.generate_and_send_signup_otp(user.email)
    
    if not success:
        logger.error(f"Failed to send signup OTP for {user.email}")
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    logger.info(f"User registered: {user.email} (pending verification)")
    
    return Response({
        'success': True,
        'message': 'Account created successfully. Please check your email for verification code.',
        'otp_required': True,
        'email': user.email
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_signup_otp(request):
    """
    Verify signup OTP and activate user account.
    
    Request Body:
        - email (required): Email address used during registration
        - otp (required): 6-digit OTP code
    
    Response (200):
        - message: Success message
        - user: User details
        - tokens: JWT access and refresh tokens
    
    Errors:
        - 400: Invalid OTP or validation errors
        - 404: User not found
    """
    serializer = VerifySignupOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    
    # Verify OTP
    is_valid, otp_instance, error_message = OTPService.verify_signup_otp(email, otp_code)
    
    if not is_valid:
        return Response({
            'success': False,
            'message': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find and activate user
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found. Please register again.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Activate user
    user.is_active = True
    user.save(update_fields=['is_active'])
    
    # Mark OTP as used
    otp_instance.mark_as_used()
    
    # Generate tokens
    tokens = get_tokens_for_user(user)
    
    logger.info(f"User verified and activated: {user.email}")
    
    return Response({
        'success': True,
        'message': 'Email verified successfully. Your account is now active.',
        'user': UserSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_200_OK)


# =============================================================================
# LOGIN ENDPOINT
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login with email and password.
    
    Only allows login if account is active (email verified).
    
    Request Body:
        - email (required): Email address
        - password (required): Password
    
    Response (200):
        - message: Success message
        - user: User details
        - tokens: JWT access and refresh tokens
    
    Errors:
        - 400: Invalid credentials or unverified email
    """
    serializer = LoginSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    
    # Generate tokens
    tokens = get_tokens_for_user(user)
    
    logger.info(f"User logged in: {user.email}")
    
    return Response({
        'success': True,
        'message': 'Login successful.',
        'user': UserSerializer(user).data,
        'tokens': tokens
    }, status=status.HTTP_200_OK)


# =============================================================================
# PASSWORD RESET ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def request_password_reset(request):
    """
    Request password reset OTP.
    
    Sends OTP to email if user exists. Always returns success to prevent
    email enumeration attacks.
    
    Request Body:
        - email (required): Email address
    
    Response (200):
        - message: Generic success message (always)
    """
    serializer = RequestPasswordResetSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Generic success message to prevent email enumeration
    generic_message = "If an account exists with this email, you will receive a password reset code."
    
    # Check if user exists
    try:
        user = User.objects.get(email__iexact=email, is_active=True)
        
        # Send password reset OTP
        success, _ = OTPService.generate_and_send_password_reset_otp(email, user)
        
        if success:
            logger.info(f"Password reset OTP sent to: {email}")
        else:
            logger.error(f"Failed to send password reset OTP to: {email}")
            
    except User.DoesNotExist:
        # Don't reveal that user doesn't exist
        logger.info(f"Password reset requested for non-existent email: {email}")
    
    return Response({
        'success': True,
        'message': generic_message
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def verify_reset_otp(request):
    """
    Verify password reset OTP.
    
    This endpoint is optional - you can also directly call reset-password
    which will verify the OTP as part of the reset process.
    
    Request Body:
        - email (required): Email address
        - otp (required): 6-digit OTP code
    
    Response (200):
        - message: Success message
        - valid: True if OTP is valid
    
    Errors:
        - 400: Invalid OTP
    """
    serializer = VerifyResetOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    
    # Verify OTP (but don't mark as used yet)
    is_valid, otp_instance, error_message = OTPService.verify_password_reset_otp(email, otp_code)
    
    if not is_valid:
        return Response({
            'success': False,
            'message': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': True,
        'message': 'OTP verified successfully. You can now reset your password.',
        'valid': True
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def reset_password(request):
    """
    Reset password with OTP verification.
    
    Verifies OTP and updates the user's password.
    
    Request Body:
        - email (required): Email address
        - otp (required): 6-digit OTP code
        - new_password (required): New password (min 8 chars)
        - confirm_new_password (required): Must match new_password
    
    Response (200):
        - message: Success message
    
    Errors:
        - 400: Invalid OTP or validation errors
        - 404: User not found
    """
    serializer = ResetPasswordSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    otp_code = serializer.validated_data['otp']
    new_password = serializer.validated_data['new_password']
    
    # Verify OTP
    is_valid, otp_instance, error_message = OTPService.verify_password_reset_otp(email, otp_code)
    
    if not is_valid:
        return Response({
            'success': False,
            'message': error_message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Find user
    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({
            'success': False,
            'message': 'User not found.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Update password
    user.set_password(new_password)
    user.save(update_fields=['password'])
    
    # Mark OTP as used
    otp_instance.mark_as_used()
    
    logger.info(f"Password reset successful for: {email}")
    
    return Response({
        'success': True,
        'message': 'Password reset successfully. You can now login with your new password.'
    }, status=status.HTTP_200_OK)


# =============================================================================
# UTILITY ENDPOINTS
# =============================================================================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([OTPRateThrottle])
def resend_otp(request):
    """
    Resend OTP for signup verification.
    
    Request Body:
        - email (required): Email address
        - otp_type (required): 'signup' or 'password_reset'
    
    Response (200):
        - message: Success message
    """
    email = request.data.get('email', '').lower().strip()
    otp_type = request.data.get('otp_type', 'signup')
    
    if not email:
        return Response({
            'success': False,
            'message': 'Email is required.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if otp_type == 'signup':
        # For signup, check if user exists and is inactive
        try:
            user = User.objects.get(email__iexact=email, is_active=False)
            success, message = OTPService.generate_and_send_signup_otp(email)
        except User.DoesNotExist:
            # Don't reveal user status
            success, message = True, "If the email is registered and pending verification, you will receive a new code."
            
    elif otp_type == 'password_reset':
        # For password reset, check if user exists and is active
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
            success, message = OTPService.generate_and_send_password_reset_otp(email, user)
        except User.DoesNotExist:
            success, message = True, "If an account exists with this email, you will receive a new code."
    else:
        return Response({
            'success': False,
            'message': 'Invalid OTP type. Use "signup" or "password_reset".'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'success': success,
        'message': message
    }, status=status.HTTP_200_OK if success else status.HTTP_500_INTERNAL_SERVER_ERROR)
