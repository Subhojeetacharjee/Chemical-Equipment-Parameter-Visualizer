/**
 * OTP Input Component
 * 
 * A modern 6-digit OTP input with auto-focus and paste support.
 */
import React, { useRef, useState, useEffect } from 'react';

const OTPInput = ({
  length = 6,
  value = '',
  onChange,
  error,
  disabled = false,
}) => {
  const [otp, setOtp] = useState(new Array(length).fill(''));
  const inputRefs = useRef([]);

  // Sync with external value
  useEffect(() => {
    if (value) {
      const otpArray = value.split('').slice(0, length);
      while (otpArray.length < length) {
        otpArray.push('');
      }
      setOtp(otpArray);
    }
  }, [value, length]);

  const handleChange = (e, index) => {
    const val = e.target.value;
    
    // Only allow digits
    if (!/^\d*$/.test(val)) return;
    
    const newOtp = [...otp];
    
    // Handle paste
    if (val.length > 1) {
      const pastedValue = val.slice(0, length - index);
      for (let i = 0; i < pastedValue.length; i++) {
        if (index + i < length) {
          newOtp[index + i] = pastedValue[i];
        }
      }
      setOtp(newOtp);
      onChange(newOtp.join(''));
      
      // Focus on the next empty input or last input
      const nextIndex = Math.min(index + pastedValue.length, length - 1);
      inputRefs.current[nextIndex]?.focus();
      return;
    }
    
    newOtp[index] = val;
    setOtp(newOtp);
    onChange(newOtp.join(''));
    
    // Auto-focus next input
    if (val && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (e, index) => {
    // Handle backspace
    if (e.key === 'Backspace') {
      if (!otp[index] && index > 0) {
        inputRefs.current[index - 1]?.focus();
      }
      const newOtp = [...otp];
      newOtp[index] = '';
      setOtp(newOtp);
      onChange(newOtp.join(''));
    }
    
    // Handle arrow keys
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
    if (e.key === 'ArrowRight' && index < length - 1) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, length);
    
    if (pastedData) {
      const newOtp = [...otp];
      for (let i = 0; i < pastedData.length; i++) {
        newOtp[i] = pastedData[i];
      }
      setOtp(newOtp);
      onChange(newOtp.join(''));
      
      // Focus on the last filled input
      const lastFilledIndex = Math.min(pastedData.length - 1, length - 1);
      inputRefs.current[lastFilledIndex]?.focus();
    }
  };

  return (
    <div>
      <div className="flex justify-center gap-2 sm:gap-3">
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={(ref) => (inputRefs.current[index] = ref)}
            type="text"
            inputMode="numeric"
            maxLength={length}
            value={digit}
            onChange={(e) => handleChange(e, index)}
            onKeyDown={(e) => handleKeyDown(e, index)}
            onPaste={handlePaste}
            disabled={disabled}
            className={`
              w-12 h-14 sm:w-14 sm:h-16
              text-center text-2xl font-bold
              border-2 rounded-xl
              transition-all duration-200
              focus:outline-none focus:ring-4
              ${error 
                ? 'border-red-400 focus:border-red-500 focus:ring-red-200' 
                : 'border-gray-200 focus:border-primary-500 focus:ring-primary-200'
              }
              ${digit ? 'border-primary-400 bg-primary-50' : 'bg-white'}
              disabled:bg-gray-100 disabled:cursor-not-allowed
            `}
          />
        ))}
      </div>
      {error && (
        <p className="mt-3 text-sm text-red-500 text-center flex items-center justify-center gap-1">
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
};

export default OTPInput;
