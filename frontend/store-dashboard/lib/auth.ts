import { apiMethods } from '@/lib/api-client';
import { ROUTES } from '@/lib/routes';
import { AuthUser, LoginPayload, RegisterPayload } from '@/types/auth.types';
import { AxiosError } from 'axios';

// Ensure fresh token - hardened version
export const ensureFreshToken = async (): Promise<string | null> => {
  const { tokenUtils } = await import('@/handles/auth.handles');
  const { token, refreshToken } = tokenUtils.getTokens();

  // If no refresh token, clear tokens and redirect to login
  if (!refreshToken) {
    console.warn('No refresh token available, clearing tokens and redirecting to login');
    tokenUtils.clearTokens();
    if (typeof window !== 'undefined') {
      window.location.href = ROUTES.AUTH.LOGIN;
    }
    return null;
  }

  // Check if access token is still valid
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const expiryTime = payload.exp * 1000;
      const timeUntilExpiry = expiryTime - Date.now();

      // If access token is still valid for more than 30 seconds, return it
      if (timeUntilExpiry > 30000) {
        return token;
      }
    } catch {
      console.warn('Could not decode access token, proceeding with refresh');
    }
  }

  // Need to refresh the token
  try {
    const refreshResponse = await refreshTokenFn(refreshToken);
    tokenUtils.setTokens(refreshResponse.access, refreshResponse.refresh);
    console.log('Token refreshed successfully');
    return refreshResponse.access;
  } catch (error: unknown) {
    console.error('Token refresh failed:', error);

    // If refresh token is invalid (401/403), clear tokens and redirect
    if (error && typeof error === 'object' && 'response' in error &&
        error.response && typeof error.response === 'object' &&
        'status' in error.response &&
        (error.response.status === 401 || error.response.status === 403)) {
      console.warn('Refresh token invalid, clearing tokens and redirecting to login');
      tokenUtils.clearTokens();
      if (typeof window !== 'undefined') {
        window.location.href = ROUTES.AUTH.LOGIN;
      }
      return null;
    }

    // For other errors, clear tokens but don't redirect (might be network issue)
    tokenUtils.clearTokens();
    throw error;
  }
};

// Internal refresh function
const refreshTokenFn = async (refreshToken: string): Promise<{ access: string; refresh: string }> => {
  // Use externalApiClient to avoid triggering request interceptor and causing circular dependency
  const { externalApiClient } = await import('@/lib/api-client');
  const response = await externalApiClient.post<{ access: string; refresh: string }>(
    ROUTES.API.AUTH.REFRESH,
    { refresh: refreshToken }
  );
  return response.data;
};

// Thin wrapper functions for authentication API calls
export const authApi = {
  // Get current user information
  getCurrentUser: (): Promise<AuthUser> => {
    return apiMethods.get<AuthUser>(ROUTES.API.AUTH.ME);
  },

  // Login user - maps 'login' field to 'email' for Djoser compatibility
  login: (credentials: LoginPayload): Promise<{ access: string; refresh: string }> => {
    const mappedCredentials = { email: credentials.login, password: credentials.password };
    console.log('Login request payload:', { ...mappedCredentials, password: '[HIDDEN]' });
    console.log('Login endpoint:', ROUTES.API.AUTH.LOGIN);
    return apiMethods.post<{ access: string; refresh: string }>(ROUTES.API.AUTH.LOGIN, mappedCredentials, { withAuth: false })
      .then(response => {
        console.log('Login response:', { access: '[TOKEN]', refresh: '[TOKEN]' });
        return response;
      })
      .catch((error: AxiosError) => {
        const status = error.response?.status;
        const data = error.response?.data;
        const url = error.config?.url;
        console.error('Login failed with details:', {
          status,
          data,
          url,
          message: error.message,
        });
        console.error('Raw error object:', error);
        console.error('Request config:', {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data ? JSON.parse(error.config.data) : undefined,
        });

        // Normalize 401 errors for form recognition
        if (status === 401) {
          const errorData = data as { detail?: string } | undefined;
          throw {
            isAuthError: true,
            status: 401,
            message:
              errorData?.detail ||
              'Incorrect username or password',
          };
        }

        // For other errors, rethrow the original AxiosError
        throw error;
      });
  },

  // Register new user - transforms payload to Djoser snake_case and does not expect tokens in response
  register: (userData: RegisterPayload): Promise<void> => {
    const mappedData = {
      email: userData.email,
      username: userData.username,
      password: userData.password,
      re_password: userData.confirmPassword,
      first_name: userData.firstName,
      last_name: userData.lastName,
    };
    return apiMethods.post(ROUTES.API.AUTH.REGISTER, mappedData, { withAuth: false }).then(() => {}); // Treat as successful if 201, no data expected
  },

  // Refresh access token
  refreshToken: (refreshToken: string): Promise<{ access: string; refresh: string }> => {
    return apiMethods.post<{ access: string; refresh: string }>(ROUTES.API.AUTH.REFRESH, {
      refresh: refreshToken,
    });
  },

  // Logout user (client-side only, server handles token invalidation)
  logout: (): Promise<void> => {
    return Promise.resolve();
  },

  // Forgot password (request reset email)
  resetPassword: (email: string): Promise<{ message: string }> => {
    return apiMethods.post<{ message: string }>(ROUTES.API.AUTH.RESET_PASSWORD, {
      email,
    }, { withAuth: false });
  },

  // Reset password confirm (set new password)
  resetPasswordConfirm: (uid: string, token: string, newPassword: string, reNewPassword: string): Promise<{ message: string }> => {
    return apiMethods.post<{ message: string }>(ROUTES.API.AUTH.RESET_PASSWORD_CONFIRM, {
      uid,
      token,
      new_password: newPassword,
      re_new_password: reNewPassword,
    }, { withAuth: false });
  },
};
