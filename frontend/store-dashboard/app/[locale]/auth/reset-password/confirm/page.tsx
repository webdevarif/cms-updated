'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { resetPasswordSchema, type ResetPasswordFormData } from '@/schemas/auth.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent } from '@/components/ui/field';
import { Heading, Paragraph, Text } from '@/components/ui/typography';
import { authApi } from '@/lib/auth';

const ResetPasswordConfirmPage = () => {
  const t = useTranslations();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState<ResetPasswordFormData>({
    token: '',
    password: '',
    confirmPassword: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Get token and uid from URL params
  useEffect(() => {
    const uid = searchParams.get('uid');
    const token = searchParams.get('token');

    if (uid && token) {
      setFormData(prev => ({ ...prev, token: `${uid}:${token}` }));
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    try {
      // Validate form data
      const validatedData = resetPasswordSchema.parse(formData);

      // Parse token back to uid and token
      const [uid, token] = validatedData.token.split(':');

      // Call reset password confirm API
      await authApi.resetPasswordConfirm(uid, token, validatedData.password, validatedData.confirmPassword);

      setIsSuccess(true);

      // Redirect to login after a short delay
      setTimeout(() => {
        router.push('/auth/login');
      }, 3000);
    } catch (error: unknown) {
      if (error instanceof Error && 'errors' in error) {
        // Zod validation errors
        const validationError = error as { errors: Array<{ path: string[]; message: string }> };
        const fieldErrors: Record<string, string> = {};
        validationError.errors.forEach((err) => {
          fieldErrors[err.path[0]] = err.message;
        });
        setErrors(fieldErrors);
      } else {
        // API error
        const apiError = error as { message?: string };
        setErrors({ general: apiError.message || t('auth.resetPasswordConfirm.error') });
      }
    } finally {
      setIsLoading(false);
    }
  };

  if (isSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <Heading variant="h2" className="mb-4">
              {t('auth.resetPasswordConfirm.success')}
            </Heading>
            <Paragraph className="mb-6">
              {t('auth.resetPasswordConfirm.redirectMessage')}
            </Paragraph>
            <Link href="/auth/login">
              <Button>
                {t('auth.backToLogin')}
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <Heading variant="h2" className="mb-2">
            {t('auth.resetPasswordConfirm.title')}
          </Heading>
          <Paragraph color="muted">
            {t('auth.resetPasswordConfirm.subtitle')}
          </Paragraph>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <Field>
            <Label>{t('auth.resetPasswordConfirm.newPassword')}</Label>
            <FieldContent>
              <Input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder={t('auth.resetPasswordConfirm.newPasswordPlaceholder')}
                disabled={isLoading}
                required
              />
            </FieldContent>
            {errors.password && (
              <Text variant="p4" color="error" className="mt-1">
                {errors.password}
              </Text>
            )}
          </Field>

          <Field>
            <Label>{t('auth.resetPasswordConfirm.confirmPassword')}</Label>
            <FieldContent>
              <Input
                type="password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder={t('auth.resetPasswordConfirm.confirmPasswordPlaceholder')}
                disabled={isLoading}
                required
              />
            </FieldContent>
            {errors.confirmPassword && (
              <Text variant="p4" color="error" className="mt-1">
                {errors.confirmPassword}
              </Text>
            )}
          </Field>

          {errors.general && (
            <div className="rounded-md bg-red-50 dark:bg-red-900/10 p-4">
              <Text variant="p4" color="error">
                {errors.general}
              </Text>
            </div>
          )}

          <Button
            type="submit"
            className="w-full"
            disabled={isLoading || !formData.token}
          >
            {isLoading ? t('common.loading') : t('auth.resetPasswordConfirm.resetPassword')}
          </Button>

          <div className="text-center">
            <Link href="/auth/login" className="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400">
              {t('auth.backToLogin')}
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ResetPasswordConfirmPage;
