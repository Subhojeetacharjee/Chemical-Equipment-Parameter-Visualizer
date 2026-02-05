"""
OTP Service for generating and sending OTP codes via SendGrid Web API.

This service handles:
- OTP generation (cryptographically secure 6-digit codes)
- Email sending via SendGrid Web API (more reliable than SMTP)
- OTP verification logic
- Comprehensive error handling and logging
"""
import os
import ssl
import logging
from django.conf import settings

# Fix for Windows SSL certificate verification issues
# Use truststore for system's native certificate store (Windows, macOS, Linux)
try:
    import truststore
    truststore.inject_into_ssl()
    logging.getLogger(__name__).info("Using system's native certificate store via truststore")
except ImportError:
    # Fallback to certifi if truststore not available
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
    os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# SendGrid Web API - more reliable than SMTP, bypasses SSL certificate issues
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent

from api.models import EmailOTP

logger = logging.getLogger(__name__)


def send_email_via_sendgrid(to_email, subject, plain_content, html_content):
    """
    Send email using SendGrid Web API.
    
    This is more reliable than SMTP as it:
    - Bypasses SSL certificate verification issues
    - Has better error messages
    - Is faster and more scalable
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        plain_content: Plain text version of the email
        html_content: HTML version of the email
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    try:
        # Get API key from environment or settings
        api_key = os.environ.get('SENDGRID_API_KEY') or getattr(settings, 'EMAIL_HOST_PASSWORD', '')
        
        if not api_key:
            logger.error("SendGrid API key not configured")
            return False, "Email service not configured. Please contact support."
        
        # Get sender email
        from_email = os.environ.get('DEFAULT_FROM_EMAIL') or getattr(settings, 'DEFAULT_FROM_EMAIL', '')
        
        if not from_email:
            logger.error("Sender email not configured")
            return False, "Email service not configured. Please contact support."
        
        # Create the email message
        message = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", plain_content),
            html_content=HtmlContent(html_content)
        )
        
        # Send the email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        # Check response status
        if response.status_code in [200, 201, 202]:
            logger.info(f"Email sent successfully to {to_email}. Status: {response.status_code}")
            return True, None
        else:
            logger.error(f"SendGrid returned status {response.status_code}: {response.body}")
            return False, f"Email service returned error code {response.status_code}"
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"SendGrid API error sending to {to_email}: {error_message}")
        
        # Parse common SendGrid errors for user-friendly messages
        if "401" in error_message or "Unauthorized" in error_message:
            return False, "Email service authentication failed. Please contact support."
        elif "403" in error_message or "Forbidden" in error_message:
            return False, "Email sender not verified. Please contact support."
        elif "429" in error_message:
            return False, "Too many email requests. Please try again in a few minutes."
        elif "timeout" in error_message.lower():
            return False, "Email service timeout. Please try again."
        else:
            return False, "Failed to send email. Please try again later."


class OTPService:
    """
    Service class for OTP operations.
    
    Handles OTP generation, email sending, and verification.
    Uses SendGrid Web API for reliable email delivery.
    """
    
    @staticmethod
    def generate_and_send_signup_otp(email):
        """
        Generate and send OTP for signup verification.
        
        Args:
            email: Email address to send OTP to
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Generate OTP first
            otp = EmailOTP.generate_otp(email=email, otp_type='signup')
            
            if not otp:
                logger.error(f"Failed to generate OTP for {email}")
                return False, "Failed to generate verification code. Please try again."
            
            # Prepare email content
            expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
            
            subject = "Verify Your Email - Chemical Equipment Visualizer"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #2563eb;">Email Verification</h2>
                    <p>Thank you for registering with Chemical Equipment Parameter Visualizer!</p>
                    <p>Your verification code is:</p>
                    <div style="background-color: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #1f2937;">{otp.otp_code}</span>
                    </div>
                    <p>This code will expire in <strong>{expiry_minutes} minutes</strong>.</p>
                    <p style="color: #6b7280; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="color: #9ca3af; font-size: 12px;">Chemical Equipment Parameter Visualizer</p>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
Email Verification

Thank you for registering with Chemical Equipment Parameter Visualizer!

Your verification code is: {otp.otp_code}

This code will expire in {expiry_minutes} minutes.

If you didn't request this code, please ignore this email.

---
Chemical Equipment Parameter Visualizer
            """
            
            # Send email via SendGrid Web API
            success, error = send_email_via_sendgrid(
                to_email=email,
                subject=subject,
                plain_content=plain_content,
                html_content=html_content
            )
            
            if success:
                logger.info(f"Signup OTP sent successfully to {email}")
                return True, "Verification code sent to your email."
            else:
                logger.error(f"Failed to send signup OTP to {email}: {error}")
                return False, error or "Failed to send verification email. Please try again."
            
        except Exception as e:
            logger.exception(f"Unexpected error sending signup OTP to {email}: {str(e)}")
            return False, "An unexpected error occurred. Please try again."
    
    @staticmethod
    def generate_and_send_password_reset_otp(email, user):
        """
        Generate and send OTP for password reset.
        
        Args:
            email: Email address to send OTP to
            user: User instance requesting password reset
            
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Generate OTP
            otp = EmailOTP.generate_otp(email=email, otp_type='password_reset', user=user)
            
            if not otp:
                logger.error(f"Failed to generate password reset OTP for {email}")
                return False, "Failed to generate reset code. Please try again."
            
            # Prepare email content
            expiry_minutes = getattr(settings, 'OTP_EXPIRY_MINUTES', 10)
            
            subject = "Password Reset - Chemical Equipment Visualizer"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #dc2626;">Password Reset Request</h2>
                    <p>We received a request to reset your password for Chemical Equipment Parameter Visualizer.</p>
                    <p>Your password reset code is:</p>
                    <div style="background-color: #fef2f2; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0; border: 1px solid #fecaca;">
                        <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #991b1b;">{otp.otp_code}</span>
                    </div>
                    <p>This code will expire in <strong>{expiry_minutes} minutes</strong>.</p>
                    <p style="color: #dc2626; font-size: 14px;"><strong>⚠️ If you didn't request this password reset, please ignore this email and ensure your account is secure.</strong></p>
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 20px 0;">
                    <p style="color: #9ca3af; font-size: 12px;">Chemical Equipment Parameter Visualizer</p>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
Password Reset Request

We received a request to reset your password for Chemical Equipment Parameter Visualizer.

Your password reset code is: {otp.otp_code}

This code will expire in {expiry_minutes} minutes.

WARNING: If you didn't request this password reset, please ignore this email and ensure your account is secure.

---
Chemical Equipment Parameter Visualizer
            """
            
            # Send email via SendGrid Web API
            success, error = send_email_via_sendgrid(
                to_email=email,
                subject=subject,
                plain_content=plain_content,
                html_content=html_content
            )
            
            if success:
                logger.info(f"Password reset OTP sent successfully to {email}")
                return True, "Password reset code sent to your email."
            else:
                logger.error(f"Failed to send password reset OTP to {email}: {error}")
                return False, error or "Failed to send password reset email. Please try again."
            
        except Exception as e:
            logger.exception(f"Unexpected error sending password reset OTP to {email}: {str(e)}")
            return False, "An unexpected error occurred. Please try again."
    
    @staticmethod
    def verify_signup_otp(email, otp_code):
        """
        Verify signup OTP.
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            
        Returns:
            tuple: (is_valid: bool, otp_instance: EmailOTP or None, error_message: str or None)
        """
        return EmailOTP.verify_otp(email=email, otp_code=otp_code, otp_type='signup')
    
    @staticmethod
    def verify_password_reset_otp(email, otp_code):
        """
        Verify password reset OTP.
        
        Args:
            email: Email address
            otp_code: OTP code to verify
            
        Returns:
            tuple: (is_valid: bool, otp_instance: EmailOTP or None, error_message: str or None)
        """
        return EmailOTP.verify_otp(email=email, otp_code=otp_code, otp_type='password_reset')
