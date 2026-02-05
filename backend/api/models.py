"""
Models for Chemical Equipment Parameter Visualizer.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import json
import secrets


class EmailOTP(models.Model):
    """
    Model to store OTP codes for email verification and password reset.
    
    Supports two types of OTPs:
    - 'signup': For verifying email during account registration
    - 'password_reset': For password reset flow
    """
    
    OTP_TYPE_CHOICES = [
        ('signup', 'Signup Verification'),
        ('password_reset', 'Password Reset'),
    ]
    
    email = models.EmailField(help_text="Email address for OTP verification")
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='otps',
        help_text="Associated user (null for signup OTPs before user is activated)"
    )
    otp_code = models.CharField(max_length=6, help_text="6-digit OTP code")
    otp_type = models.CharField(
        max_length=20, 
        choices=OTP_TYPE_CHOICES,
        help_text="Type of OTP (signup or password_reset)"
    )
    expires_at = models.DateTimeField(help_text="OTP expiration timestamp")
    is_used = models.BooleanField(default=False, help_text="Whether OTP has been used")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Email OTP"
        verbose_name_plural = "Email OTPs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'otp_type', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.email} ({self.otp_type}) - {'Used' if self.is_used else 'Active'}"
    
    @classmethod
    def generate_otp(cls, email, otp_type, user=None):
        """
        Generate a new OTP for the given email and type.
        
        Args:
            email: Email address to send OTP to
            otp_type: Type of OTP ('signup' or 'password_reset')
            user: Optional user instance (for password reset)
        
        Returns:
            EmailOTP instance with the generated OTP
        """
        # Invalidate any existing unused OTPs for this email and type
        cls.objects.filter(
            email=email, 
            otp_type=otp_type, 
            is_used=False
        ).update(is_used=True)
        
        # Generate cryptographically secure 6-digit OTP
        otp_code = ''.join([str(secrets.randbelow(10)) for _ in range(settings.OTP_LENGTH)])
        
        # Calculate expiry time
        expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
        expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        
        # Create new OTP record
        otp = cls.objects.create(
            email=email,
            user=user,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=expires_at
        )
        
        return otp
    
    def is_valid(self):
        """Check if OTP is valid (not expired and not used)."""
        return not self.is_used and timezone.now() < self.expires_at
    
    def mark_as_used(self):
        """Mark OTP as used."""
        self.is_used = True
        self.save(update_fields=['is_used'])
    
    @classmethod
    def verify_otp(cls, email, otp_code, otp_type):
        """
        Verify an OTP for given email and type.
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            otp_type: Type of OTP
        
        Returns:
            tuple: (is_valid: bool, otp_instance: EmailOTP or None, error_message: str or None)
        """
        try:
            otp = cls.objects.filter(
                email=email,
                otp_code=otp_code,
                otp_type=otp_type,
                is_used=False
            ).latest('created_at')
            
            if not otp.is_valid():
                return False, None, "OTP has expired. Please request a new one."
            
            return True, otp, None
            
        except cls.DoesNotExist:
            return False, None, "Invalid OTP. Please check and try again."


class Dataset(models.Model):
    """Model to store uploaded CSV datasets."""
    
    name = models.CharField(max_length=255, help_text="Name of the uploaded file")
    uploaded_at = models.DateTimeField(default=timezone.now)
    total_equipment = models.IntegerField(default=0)
    avg_flowrate = models.FloatField(default=0.0)
    avg_pressure = models.FloatField(default=0.0)
    avg_temperature = models.FloatField(default=0.0)
    type_distribution = models.TextField(default='{}', help_text="JSON string of equipment type distribution")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_type_distribution(self):
        """Return type distribution as dictionary."""
        try:
            return json.loads(self.type_distribution)
        except json.JSONDecodeError:
            return {}
    
    def set_type_distribution(self, distribution_dict):
        """Set type distribution from dictionary."""
        self.type_distribution = json.dumps(distribution_dict)


class Equipment(models.Model):
    """Model to store individual equipment records."""
    
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    name = models.CharField(max_length=255, help_text="Equipment name")
    equipment_type = models.CharField(max_length=100, help_text="Type of equipment")
    flowrate = models.FloatField(help_text="Flowrate value")
    pressure = models.FloatField(help_text="Pressure value")
    temperature = models.FloatField(help_text="Temperature value")
    
    class Meta:
        verbose_name_plural = "Equipment"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"
