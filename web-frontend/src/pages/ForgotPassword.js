/**
 * Forgot Password Page
 * 
 * Two-step password reset flow:
 * Step 1: Enter email to receive OTP
 * Step 2: Enter OTP and new password
 */
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import AuthLayout from '../components/auth/AuthLayout';
import AuthCard from '../components/auth/AuthCard';
import Input from '../components/auth/Input';
import Button from '../components/auth/Button';
import OTPInput from '../components/auth/OTPInput';

const ForgotPassword = () => {
  const navigate = useNavigate();
  const { requestPasswordReset, resetPassword, resendOTP } = useAuth();
  
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [passwords, setPasswords] = useState({
    new_password: '',
    confirm_new_password: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);

  const validateStep1 = () => {
    const newErrors = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Please enter a valid email';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const validateStep2 = () => {
    const newErrors = {};
    
    if (!otp || otp.length !== 6) {
      newErrors.otp = 'Please enter the 6-digit code';
    }
    
    if (!passwords.new_password) {
      newErrors.new_password = 'New password is required';
    } else if (passwords.new_password.length < 8) {
      newErrors.new_password = 'Password must be at least 8 characters';
    }
    
    if (!passwords.confirm_new_password) {
      newErrors.confirm_new_password = 'Please confirm your password';
    } else if (passwords.new_password !== passwords.confirm_new_password) {
      newErrors.confirm_new_password = 'Passwords do not match';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswords((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => ({ ...prev, [name]: '' }));
    }
  };

  const handleOTPChange = (value) => {
    setOtp(value);
    if (errors.otp) {
      setErrors((prev) => ({ ...prev, otp: '' }));
    }
  };

  const handleStep1Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep1()) return;
    
    setIsLoading(true);
    
    try {
      await requestPasswordReset(email);
      toast.success('If an account exists, you will receive a reset code.');
      setStep(2);
      startResendCooldown();
    } catch (error) {
      // Always show success message to prevent email enumeration
      toast.success('If an account exists, you will receive a reset code.');
      setStep(2);
      startResendCooldown();
    } finally {
      setIsLoading(false);
    }
  };

  const handleStep2Submit = async (e) => {
    e.preventDefault();
    
    if (!validateStep2()) return;
    
    setIsLoading(true);
    
    try {
      const response = await resetPassword({
        email,
        otp,
        new_password: passwords.new_password,
        confirm_new_password: passwords.confirm_new_password,
      });
      
      if (response.success) {
        toast.success('Password reset successfully! Please log in.');
        navigate('/login', { replace: true });
      }
    } catch (error) {
      const errorData = error.response?.data;
      
      if (errorData?.message) {
        setErrors({ otp: errorData.message });
      } else if (errorData?.errors) {
        const fieldErrors = {};
        Object.entries(errorData.errors).forEach(([key, value]) => {
          fieldErrors[key] = Array.isArray(value) ? value[0] : value;
        });
        setErrors(fieldErrors);
      } else {
        toast.error('Password reset failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const startResendCooldown = () => {
    setResendCooldown(60);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  };

  const handleResendOTP = async () => {
    if (resendCooldown > 0) return;
    
    try {
      await resendOTP(email, 'password_reset');
      toast.success('New reset code sent!');
      startResendCooldown();
    } catch (error) {
      toast.error('Failed to resend code. Please try again.');
    }
  };

  return (
    <AuthLayout>
      <AuthCard>
        {/* Step 1: Enter Email */}
        {step === 1 && (
          <>
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                </svg>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Forgot Password?
              </h1>
              <p className="mt-2 text-gray-600">
                No worries! Enter your email and we'll send you a reset code.
              </p>
            </div>

            <form onSubmit={handleStep1Submit} className="space-y-5">
              <Input
                label="Email Address"
                type="email"
                name="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (errors.email) {
                    setErrors((prev) => ({ ...prev, email: '' }));
                  }
                }}
                error={errors.email}
                autoComplete="email"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                  </svg>
                }
              />

              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
              >
                Send Reset Code
              </Button>
            </form>

            <div className="mt-6 text-center">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-800"
              >
                ← Back to login
              </Link>
            </div>
          </>
        )}

        {/* Step 2: Enter OTP and New Password */}
        {step === 2 && (
          <>
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-gradient-to-br from-primary-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                Reset Password
              </h1>
              <p className="mt-2 text-gray-600">
                Enter the code sent to
              </p>
              <p className="font-semibold text-primary-600">
                {email}
              </p>
            </div>

            <form onSubmit={handleStep2Submit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3 text-center">
                  Verification Code
                </label>
                <OTPInput
                  value={otp}
                  onChange={handleOTPChange}
                  error={errors.otp}
                />
              </div>

              <Input
                label="New Password"
                type="password"
                name="new_password"
                placeholder="Min. 8 characters"
                value={passwords.new_password}
                onChange={handlePasswordChange}
                error={errors.new_password}
                autoComplete="new-password"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                  </svg>
                }
              />

              <Input
                label="Confirm New Password"
                type="password"
                name="confirm_new_password"
                placeholder="••••••••"
                value={passwords.confirm_new_password}
                onChange={handlePasswordChange}
                error={errors.confirm_new_password}
                autoComplete="new-password"
                icon={
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                }
              />

              <Button
                type="submit"
                fullWidth
                loading={isLoading}
                size="lg"
              >
                Reset Password
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-600 mb-2">
                Didn't receive the code?
              </p>
              <button
                type="button"
                onClick={handleResendOTP}
                disabled={resendCooldown > 0}
                className={`font-semibold ${
                  resendCooldown > 0
                    ? 'text-gray-400 cursor-not-allowed'
                    : 'text-primary-600 hover:text-primary-700'
                }`}
              >
                {resendCooldown > 0
                  ? `Resend in ${resendCooldown}s`
                  : 'Resend Code'}
              </button>
            </div>

            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="text-gray-500 hover:text-gray-700 text-sm"
              >
                ← Change email
              </button>
            </div>
          </>
        )}
      </AuthCard>
    </AuthLayout>
  );
};

export default ForgotPassword;
