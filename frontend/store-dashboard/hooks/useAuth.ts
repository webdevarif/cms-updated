'use client';

import useSWR, { useSWRConfig } from 'swr';
import { useCallback, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/auth';
import { tokenUtils } from '@/handles/auth.handles';
import { ROUTES } from '@/lib/routes';
import { AuthUser, LoginPayload, RegisterPayload } from '@/types/auth.types';

// Auth hooks
export function useAuth() {
  const { data, error, isLoading, mutate } = useSWR<AuthUser>(
    ROUTES.API.AUTH.ME,
    () => authApi.getCurrentUser(),
    {
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
      shouldRetryOnError: false,
      dedupingInterval: 300000, // 5 minutes (increased from 1 minute)
      errorRetryCount: 0,
      refreshInterval: 0, // Disable automatic refresh
    }
  );

  const isAuthenticated = !!data && !!tokenUtils.getTokens().token;

  return {
    user: data,
    error,
    isLoading,
    isAuthenticated,
    mutate,
  };
}

export function useLogin() {
  const { mutate } = useSWRConfig();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const login = useCallback(async (credentials: LoginPayload): Promise<{ access: string; refresh: string }> => {
    setIsLoading(true);
    try {
      const tokens = await authApi.login(credentials);
      tokenUtils.setTokens(tokens.access, tokens.refresh);
      await mutate(ROUTES.API.AUTH.ME);
      router.push(ROUTES.DASHBOARD);
      return tokens;
    } catch (error) {
      throw error; // Just rethrow, let the form handle UI
    } finally {
      setIsLoading(false);
    }
  }, [mutate, router]);

  return { login, isLoading };
}

export function useRegister() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const register = useCallback(async (userData: RegisterPayload): Promise<void> => {
    setIsLoading(true);
    try {
      await authApi.register(userData);
      router.push(ROUTES.AUTH.LOGIN);
    } catch (error) {
      console.error('Register error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  return { register, isLoading };
}

export function useLogout() {
  const { mutate } = useSWRConfig();
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      // No backend logout endpoint for Djoser
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      tokenUtils.clearTokens();
      await mutate(ROUTES.API.AUTH.ME, null, false);
      router.push(ROUTES.AUTH.LOGIN);
      setIsLoading(false);
    }
  }, [mutate, router]);

  return { logout, isLoading };
}

// Password reset hooks
export function useForgotPassword() {
  const [isLoading, setIsLoading] = useState(false);

  const forgotPassword = useCallback(async (email: string): Promise<{ message: string }> => {
    setIsLoading(true);
    try {
      return await authApi.resetPassword(email);
    } catch (error) {
      console.error('Forgot password error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { forgotPassword, isLoading };
}

export function useResetPassword() {
  const [isLoading, setIsLoading] = useState(false);

  const resetPasswordConfirm = useCallback(async (uid: string, token: string, newPassword: string, reNewPassword: string): Promise<{ message: string }> => {
    setIsLoading(true);
    try {
      return await authApi.resetPasswordConfirm(uid, token, newPassword, reNewPassword);
    } catch (error) {
      console.error('Reset password confirm error:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { resetPasswordConfirm, isLoading };
}

// Re-export for backward compatibility
export type { AuthUser, LoginPayload, RegisterPayload, AuthResponse, ForgotPasswordFormData, ResetPasswordFormData } from '@/types/auth.types';
