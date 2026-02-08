import { LoginFormData, RegisterFormData, ForgotPasswordFormData, ResetPasswordFormData } from '@/schemas/auth.schemas';
import { AuthResponse, User, AuthError } from '@/types/auth.types';
import { ROUTES } from '@/lib/routes';
import { NextRequest } from 'next/server';

// Authentication API Handles

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Generic API handler
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('API Error Response:', data);
      // Handle different error response formats
      let errorMessage = 'An error occurred';

      if (data.non_field_errors && Array.isArray(data.non_field_errors) && data.non_field_errors.length > 0) {
        errorMessage = data.non_field_errors[0];
      } else if (data.message) {
        errorMessage = data.message;
      } else if (data.detail) {
        errorMessage = data.detail;
      } else if (data.error) {
        errorMessage = data.error;
      }

      throw new AuthError(
        data.code || 'UNKNOWN_ERROR',
        errorMessage,
        data.field
      );
    }

    return data;
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }

    // Network or other errors
    throw new AuthError(
      'NETWORK_ERROR',
      'Network error occurred. Please try again.',
      undefined
    );
  }
}

// LEGACY: These handlers use fetch and are being phased out in favor of lib/auth.ts + api-client.
// Do not add new handlers here. Prefer using authApi in lib/auth.ts and hooks/useAuth.ts.

// Login handler
export async function handleLogin(credentials: LoginFormData): Promise<AuthResponse> {
  return apiRequest<AuthResponse>(ROUTES.API.AUTH.LOGIN, {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

// Register handler
export async function handleRegister(userData: Omit<RegisterFormData, 'acceptTerms'>): Promise<AuthResponse> {
  return apiRequest<AuthResponse>(ROUTES.API.AUTH.REGISTER, {
    method: 'POST',
    body: JSON.stringify(userData),
  });
}

// Forgot password handler
export async function handleForgotPassword(email: ForgotPasswordFormData): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(ROUTES.API.AUTH.FORGET_PASSWORD, {
    method: 'POST',
    body: JSON.stringify(email),
  });
}

// Reset password handler
export async function handleResetPassword(resetData: ResetPasswordFormData): Promise<AuthResponse> {
  return apiRequest<AuthResponse>(ROUTES.API.AUTH.RESET_PASSWORD, {
    method: 'POST',
    body: JSON.stringify(resetData),
  });
}

// Logout handler
export async function handleLogout(): Promise<{ message: string }> {
  const token = localStorage.getItem('access_token');

  return apiRequest<{ message: string }>(ROUTES.API.AUTH.LOGOUT, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

// Refresh token handler
export async function handleRefreshToken(): Promise<AuthResponse> {
  const refreshToken = localStorage.getItem('refresh_token');

  return apiRequest<AuthResponse>(ROUTES.API.AUTH.REFRESH, {
    method: 'POST',
    body: JSON.stringify({ refresh: refreshToken }),
  });
}

// Get current user handler
export async function handleGetCurrentUser(): Promise<User> {
  const token = localStorage.getItem('access_token');

  return apiRequest<User>(ROUTES.API.AUTH.ME, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

// Social login handlers
export async function handleSocialLogin(provider: string, token: string): Promise<AuthResponse> {
  return apiRequest<AuthResponse>(`/public/accounts/oauth/${provider}`, {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}

// Google OAuth handler
export async function handleGoogleLogin(): Promise<void> {
  const googleAuthUrl = `${API_BASE_URL}/public/accounts/oauth/google`;
  window.location.href = googleAuthUrl;
}

// Facebook OAuth handler
export async function handleFacebookLogin(): Promise<void> {
  const facebookAuthUrl = `${API_BASE_URL}/public/accounts/oauth/facebook`;
  window.location.href = facebookAuthUrl;
}

// GitHub OAuth handler
export async function handleGithubLogin(): Promise<void> {
  const githubAuthUrl = `${API_BASE_URL}/public/accounts/oauth/github`;
  window.location.href = githubAuthUrl;
}

// Verify email handler
export async function handleVerifyEmail(token: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/auth/verify-email', {
    method: 'POST',
    body: JSON.stringify({ token }),
  });
}

// Resend verification email handler
export async function handleResendVerificationEmail(email: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/auth/resend-verification', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

// Change password handler
export async function handleChangePassword(passwords: { currentPassword: string; newPassword: string }): Promise<{ message: string }> {
  const token = localStorage.getItem('auth_token');

  return apiRequest<{ message: string }>('/auth/change-password', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(passwords),
  });
}

// Update profile handler
export async function handleUpdateProfile(profileData: { firstName: string; lastName: string; avatar?: string }): Promise<User> {
  const token = localStorage.getItem('auth_token');

  return apiRequest<User>('/auth/update-profile', {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(profileData),
  });
}

// Delete account handler
export async function handleDeleteAccount(): Promise<{ message: string }> {
  const token = localStorage.getItem('auth_token');

  return apiRequest<{ message: string }>('/auth/delete-account', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
}

// Utility functions for token management
export const tokenUtils = {
  setTokens: (token: string, refreshToken: string) => {
    // Store in localStorage for client-side access
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', token);
      localStorage.setItem('refresh_token', refreshToken);

      // Set cookies for server-side access (middleware)
      const now = new Date();
      const accessExpiry = new Date(now.getTime() + 24 * 60 * 60 * 1000); // 24 hours
      const refreshExpiry = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000); // 7 days

      document.cookie = `access_token=${token}; path=/; expires=${accessExpiry.toUTCString()}; SameSite=Lax${process.env.NODE_ENV === 'production' ? '; Secure' : ''}`;
      document.cookie = `refresh_token=${refreshToken}; path=/; expires=${refreshExpiry.toUTCString()}; SameSite=Lax${process.env.NODE_ENV === 'production' ? '; Secure' : ''}`;
    }
  },

  getTokens: () => {
    if (typeof window === 'undefined') {
      return { token: null, refreshToken: null };
    }
    return {
      token: localStorage.getItem('access_token'),
      refreshToken: localStorage.getItem('refresh_token'),
    };
  },

  clearTokens: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');

      // Clear cookies
      document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
      document.cookie = 'refresh_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    }
  },

  isTokenExpired: (token: string | null): boolean => {
    if (!token) return true;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Date.now() / 1000;
      return payload.exp < now;
    } catch {
      return true;
    }
  },

  // Get token from cookies (server-side)
  getTokenFromCookie: (request?: NextRequest | { cookies?: { get: (name: string) => { value?: string } | null } | null }): string | null => {
    if (typeof window !== 'undefined') {
      // Client-side: get from document cookie
      const match = document.cookie.match(/(^|;) ?access_token=([^;]*)/);
      return match ? match[2] : null;
    } else if (request?.cookies) {
      // Server-side: get from request cookies
      const cookie = request.cookies.get('access_token');
      return cookie?.value || null;
    }
    return null;
  },
};

// Export error class for use in components
export { AuthError };
