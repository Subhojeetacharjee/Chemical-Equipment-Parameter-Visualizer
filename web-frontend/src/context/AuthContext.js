/**
 * Authentication Context
 * 
 * Provides authentication state and methods throughout the app.
 * Wrap your app with <AuthProvider> to use authentication features.
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService from '../services/authApi';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from localStorage
  useEffect(() => {
    const initializeAuth = () => {
      const storedUser = authService.getUser();
      const hasToken = authService.isAuthenticated();
      
      if (hasToken && storedUser) {
        setUser(storedUser);
        setIsAuthenticated(true);
      }
      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  /**
   * Login user and store tokens
   */
  const login = useCallback(async (email, password) => {
    const response = await authService.login({ email, password });
    
    if (response.success) {
      authService.storeTokens(response.tokens);
      authService.storeUser(response.user);
      setUser(response.user);
      setIsAuthenticated(true);
    }
    
    return response;
  }, []);

  /**
   * Register new user
   */
  const register = useCallback(async (data) => {
    const response = await authService.register(data);
    return response;
  }, []);

  /**
   * Verify signup OTP
   */
  const verifySignupOTP = useCallback(async (email, otp) => {
    const response = await authService.verifySignupOTP({ email, otp });
    
    if (response.success) {
      authService.storeTokens(response.tokens);
      authService.storeUser(response.user);
      setUser(response.user);
      setIsAuthenticated(true);
    }
    
    return response;
  }, []);

  /**
   * Request password reset
   */
  const requestPasswordReset = useCallback(async (email) => {
    const response = await authService.requestPasswordReset({ email });
    return response;
  }, []);

  /**
   * Reset password with OTP
   */
  const resetPassword = useCallback(async (data) => {
    const response = await authService.resetPassword(data);
    return response;
  }, []);

  /**
   * Resend OTP
   */
  const resendOTP = useCallback(async (email, otpType) => {
    const response = await authService.resendOTP({ email, otp_type: otpType });
    return response;
  }, []);

  /**
   * Logout user
   */
  const logout = useCallback(() => {
    authService.clearTokens();
    setUser(null);
    setIsAuthenticated(false);
  }, []);

  const value = {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    verifySignupOTP,
    requestPasswordReset,
    resetPassword,
    resendOTP,
    logout,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
