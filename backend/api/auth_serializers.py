"""
Authentication Serializers for OTP-based authentication.

Provides serializers for:
- User registration with email verification
- OTP verification for signup
- Login with email and password
- Password reset request and completion
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.core.validators import EmailValidator


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    
    Creates an inactive user and triggers OTP email for verification.
    """
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator()],
        help_text="Valid email address for account"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="Password (minimum 8 characters)"
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirm password"
    )
    name = serializers.CharField(
        required=False,
        max_length=150,
        allow_blank=True,
        help_text="Optional full name"
    )
    
    def validate_email(self, value):
        """Ensure email is unique (case-insensitive)."""
        email = value.lower().strip()
        if User.objects.filter(email__iexact=email).exists():
            # Check if user is inactive (unverified)
            user = User.objects.filter(email__iexact=email).first()
            if user and not user.is_active:
                # Allow re-registration for unverified accounts
                return email
            raise serializers.ValidationError("An account with this email already exists.")
        return email
    
    def validate_password(self, value):
        """Validate password strength using Django's validators."""
        validate_password(value)
        return value
    
    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return data
    
    def create(self, validated_data):
        """Create inactive user for email verification."""
        email = validated_data['email'].lower().strip()
        name = validated_data.get('name', '').strip()
        
        # Check if user already exists but is inactive
        existing_user = User.objects.filter(email__iexact=email).first()
        if existing_user and not existing_user.is_active:
            # Update existing inactive user
            existing_user.set_password(validated_data['password'])
            if name:
                name_parts = name.split(' ', 1)
                existing_user.first_name = name_parts[0]
                existing_user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            existing_user.save()
            return existing_user
        
        # Create new inactive user
        username = email  # Use email as username
        
        # Parse name into first/last
        first_name = ''
        last_name = ''
        if name:
            name_parts = name.split(' ', 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name,
            is_active=False  # User must verify email first
        )
        
        return user


class VerifySignupOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying signup OTP.
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address used during registration"
    )
    otp = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()
    
    def validate_otp(self, value):
        """Ensure OTP is numeric."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Password"
    )
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()
    
    def validate(self, data):
        """Authenticate user."""
        email = data['email']
        password = data['password']
        
        # Find user by email
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'email': "No account found with this email address."
            })
        
        # Check if user is active (email verified)
        if not user.is_active:
            raise serializers.ValidationError({
                'email': "Please verify your email address before logging in."
            })
        
        # Authenticate
        authenticated_user = authenticate(username=user.username, password=password)
        if not authenticated_user:
            raise serializers.ValidationError({
                'password': "Invalid password."
            })
        
        data['user'] = authenticated_user
        return data


class RequestPasswordResetSerializer(serializers.Serializer):
    """
    Serializer for requesting password reset.
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address for password reset"
    )
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()


class VerifyResetOTPSerializer(serializers.Serializer):
    """
    Serializer for verifying password reset OTP.
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    otp = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit OTP code"
    )
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()
    
    def validate_otp(self, value):
        """Ensure OTP is numeric."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password with OTP verification.
    """
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    otp = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        help_text="6-digit OTP code"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        help_text="New password (minimum 8 characters)"
    )
    confirm_new_password = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Confirm new password"
    )
    
    def validate_email(self, value):
        """Normalize email."""
        return value.lower().strip()
    
    def validate_otp(self, value):
        """Ensure OTP is numeric."""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits.")
        return value
    
    def validate_new_password(self, value):
        """Validate password strength."""
        validate_password(value)
        return value
    
    def validate(self, data):
        """Ensure passwords match."""
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({
                'confirm_new_password': "Passwords do not match."
            })
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user information in responses.
    """
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'first_name', 'last_name', 'date_joined']
        read_only_fields = fields
    
    def get_name(self, obj):
        """Get full name."""
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name if full_name else obj.email.split('@')[0]
