'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { forgotPasswordSchema, type ForgotPasswordFormData } from '@/schemas/auth.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent } from '@/components/ui/field';
import { Heading, Paragraph, Text } from '@/components/ui/typography';
import { authApi } from '@/lib/auth';

const ResetPasswordRequestPage = () => {
  const t = useTranslations();
  const [formData, setFormData] = useState<ForgotPasswordFormData>({
    email: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    try {
      // Validate form data
      const validatedData = forgotPasswordSchema.parse(formData);

      // Call reset password API
      await authApi.resetPassword(validatedData.email);

      setIsSuccess(true);
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
        setErrors({ general: apiError.message || t('auth.resetPassword.error') });
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
              {t('auth.resetPassword.checkEmail')}
            </Heading>
            <Paragraph className="mb-6">
              {t('auth.resetPassword.emailSent')}
            </Paragraph>
            <Link href="/auth/login">
              <Button variant="outline">
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
            {t('auth.resetPassword.title')}
          </Heading>
          <Paragraph color="muted">
            {t('auth.resetPassword.subtitle')}
          </Paragraph>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <Field>
            <Label>{t('auth.email')}</Label>
            <FieldContent>
              <Input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder={t('auth.emailPlaceholder')}
                disabled={isLoading}
                required
              />
            </FieldContent>
            {errors.email && (
              <Text variant="p4" color="error" className="mt-1">
                {errors.email}
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
            disabled={isLoading}
          >
            {isLoading ? t('common.loading') : t('auth.resetPassword.sendResetLink')}
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

export default ResetPasswordRequestPage;
