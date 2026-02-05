/**
 * Authentication API Service
 * 
 * This module handles all authentication-related API calls.
 * 
 * CONFIGURATION:
 * - Set REACT_APP_API_URL in your .env file to point to your Django backend
 * - Default: http://localhost:8000/api
 * - Production example: https://your-backend.onrender.com/api
 */
import axios from 'axios';

// Base URL configuration - change this to your deployed backend URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
authApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token refresh on 401 errors
authApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (refreshToken) {
          // You can implement token refresh here if needed
          // For now, we'll just clear tokens and redirect to login
        }
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

/**
 * Authentication API methods
 */
export const authService = {
  /**
   * Register a new user
   * @param {Object} data - { email, password, confirm_password, name? }
   * @returns {Promise} Response with otp_required flag
   */
  register: async (data) => {
    const response = await authApi.post('/auth/register/', data);
    return response.data;
  },

  /**
   * Verify signup OTP and activate account
   * @param {Object} data - { email, otp }
   * @returns {Promise} Response with user and tokens
   */
  verifySignupOTP: async (data) => {
    const response = await authApi.post('/auth/verify-signup-otp/', data);
    return response.data;
  },

  /**
   * Login with email and password
   * @param {Object} data - { email, password }
   * @returns {Promise} Response with user and tokens
   */
  login: async (data) => {
    const response = await authApi.post('/auth/login/', data);
    return response.data;
  },

  /**
   * Request password reset OTP
   * @param {Object} data - { email }
   * @returns {Promise} Response with success message
   */
  requestPasswordReset: async (data) => {
    const response = await authApi.post('/auth/request-password-reset/', data);
    return response.data;
  },

  /**
   * Verify password reset OTP
   * @param {Object} data - { email, otp }
   * @returns {Promise} Response with valid flag
   */
  verifyResetOTP: async (data) => {
    const response = await authApi.post('/auth/verify-reset-otp/', data);
    return response.data;
  },

  /**
   * Reset password with OTP
   * @param {Object} data - { email, otp, new_password, confirm_new_password }
   * @returns {Promise} Response with success message
   */
  resetPassword: async (data) => {
    const response = await authApi.post('/auth/reset-password/', data);
    return response.data;
  },

  /**
   * Resend OTP
   * @param {Object} data - { email, otp_type: 'signup' | 'password_reset' }
   * @returns {Promise} Response with success message
   */
  resendOTP: async (data) => {
    const response = await authApi.post('/auth/resend-otp/', data);
    return response.data;
  },

  /**
   * Store authentication tokens
   * @param {Object} tokens - { access, refresh }
   */
  storeTokens: (tokens) => {
    localStorage.setItem('accessToken', tokens.access);
    localStorage.setItem('refreshToken', tokens.refresh);
  },

  /**
   * Clear authentication tokens
   */
  clearTokens: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
  },

  /**
   * Check if user is authenticated
   * @returns {boolean}
   */
  isAuthenticated: () => {
    return !!localStorage.getItem('accessToken');
  },

  /**
   * Get stored user data
   * @returns {Object|null}
   */
  getUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  /**
   * Store user data
   * @param {Object} user
   */
  storeUser: (user) => {
    localStorage.setItem('user', JSON.stringify(user));
  },
};

export default authService;
