// Authentication Types

export interface AuthTokens {
  access: string;
  refresh: string;
  expiresAt?: number; // Optional timestamp for token expiry
}

export interface AuthUser {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  avatar?: string;
  role: 'user' | 'admin' | 'moderator';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
  is_staff?: boolean;
  is_superuser?: boolean;
}

export interface LoginPayload {
  login: string;
  password: string;
  rememberMe: boolean;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  acceptTerms: boolean;
}

export interface AuthResponse {
  access: string;
  refresh: string;
}

// Alias types for backward compatibility
export type LoginFormData = LoginPayload;
export type RegisterFormData = RegisterPayload;
export type User = AuthUser;
export type ForgotPasswordFormData = { email: string };
export type ResetPasswordFormData = { token: string; password: string; confirmPassword: string };

export interface SocialLoginProvider {
  name: 'google' | 'facebook' | 'github';
  displayName: string;
  icon: string;
  color: string;
}

// Auth Error class for proper error handling
export class AuthError extends Error {
  constructor(
    public code: string,
    public message: string,
    public field?: string
  ) {
    super(message);
    this.name = 'AuthError';
  }
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: AuthError | null;
}
