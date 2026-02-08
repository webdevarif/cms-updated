"use client";
import React, { useState, useTransition } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from '@/i18n/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent, FieldGroup } from '@/components/ui/field';
import { FiEye, FiEyeOff, FiGoogle, FiFacebook, FiGithub } from '@/lib/icons';
import { registerSchema, RegisterFormData } from '@/schemas/auth.schemas';
import { handleGoogleLogin, handleFacebookLogin, handleGithubLogin, AuthError } from '@/handles/auth.handles';
import { showToast } from '@/lib/toast';
import { routeHelpers } from '@/lib/routes';
import { useRegister } from '@/hooks/useAuth';
import { Checkbox } from '@/components/ui/checkbox';

const RegisterForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showPasswordConfirm, setShowPasswordConfirm] = useState(false);
  const [isSocialLoading, setIsSocialLoading] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const router = useRouter();
  const { register: registerUser } = useRegister();

  console.log('RegisterForm component mounted');

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    watch,
    setValue,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      firstName: '',
      lastName: '',
      acceptTerms: false,
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    console.log('🚀 Registration submission started:', data);

    try {
      console.log('📝 Showing loading toast...');
      const loadingToast = showToast.loading('Creating your account...');

      // Remove acceptTerms from API call as it's only for validation
      const registrationData = {
        username: data.username,
        email: data.email,
        password: data.password,
        confirmPassword: data.confirmPassword,
        firstName: data.firstName,
        lastName: data.lastName,
      };

      console.log('📤 Sending registration data:', registrationData);

      const response = await registerUser(registrationData);

      console.log('✅ Registration successful:', response);

      showToast.dismiss(loadingToast);
      showToast.success('Account created successfully! Welcome aboard!');

      // Redirect to dashboard after successful registration
      startTransition(() => {
        console.log('🔄 Starting transition to dashboard...');
        setTimeout(() => {
          console.log('🎯 Redirecting to dashboard...');
          router.push(routeHelpers.getDashboardRedirect());
        }, 1000);
      });

    } catch (error) {
      console.log('❌ Registration error caught:', error);
      showToast.dismiss();

      if (error instanceof AuthError) {
        console.log('🔍 AuthError details:', {
          code: error.code,
          message: error.message,
          field: error.field
        });

        // Handle field-specific errors
        if (error.field) {
          console.log('🎯 Setting field error for:', error.field);
          setError(error.field as keyof RegisterFormData, {
            message: error.message,
          });
        }

        showToast.error(error.message);
        console.error('Registration error:', error.message);
      } else {
        console.log('❓ Unexpected error type:', typeof error, error);
        showToast.error('An unexpected error occurred. Please try again.');
        console.error('Unexpected error:', error);
      }
    }
  };

  const handleSocialLoginClick = async (provider: 'Google' | 'Facebook' | 'Github') => {
    console.log(`🔗 ${provider} social login initiated`);

    try {
      setIsSocialLoading(provider);
      console.log(`📤 Setting loading state for ${provider}`);
      showToast.loading(`Connecting to ${provider}...`);

      switch (provider) {
        case 'Google':
          console.log('🔍 Redirecting to Google OAuth...');
          await handleGoogleLogin();
          break;
        case 'Facebook':
          console.log('🔍 Redirecting to Facebook OAuth...');
          await handleFacebookLogin();
          break;
        case 'Github':
          console.log('🔍 Redirecting to GitHub OAuth...');
          await handleGithubLogin();
          break;
        default:
          throw new Error('Unsupported social provider');
      }
    } catch (error) {
      console.log(`❌ ${provider} login error caught:`, error);
      showToast.dismiss();

      if (error instanceof AuthError) {
        console.log(`🔍 ${provider} AuthError details:`, {
          code: error.code,
          message: error.message
        });
        showToast.error(`${provider} login failed: ${error.message}`);
      } else {
        console.log(`❓ ${provider} unexpected error type:`, typeof error, error);
        showToast.error(`Failed to connect to ${provider}. Please try again.`);
      }

      console.error(`${provider} login error:`, error);
    } finally {
      console.log(`🔄 Clearing ${provider} loading state`);
      setIsSocialLoading(null);
    }
  };

  return (
    <div className="w-full max-w-[25rem] space-y-6">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FieldGroup>
          {/* Profile Field */}
          <div className="grid grid-cols-2 gap-4">
            <Field>
              <Label htmlFor="firstName">First Name</Label>
              <FieldContent>
                <div className="relative">
                  <Input
                    id="firstName"
                    type="text"
                    placeholder="Enter First Name"
                    {...register('firstName')}
                    disabled={isSubmitting}
                  />
                </div>
              </FieldContent>
              {errors.firstName && (
                <p className="text-destructive text-sm">{errors.firstName.message}</p>
              )}
            </Field>

            <Field>
              <Label htmlFor="lastName">Last Name</Label>
              <FieldContent>
                <div className="relative">
                  <Input
                    id="lastName"
                    type="text"
                    placeholder="Enter Last Name"
                    {...register('lastName')}
                    disabled={isSubmitting}
                  />
                </div>
              </FieldContent>
              {errors.lastName && (
                <p className="text-destructive text-sm">{errors.lastName.message}</p>
              )}
            </Field>
          </div>

          {/* Email Field */}
          <Field>
            <Label htmlFor="email">Email</Label>
            <FieldContent>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                {...register('email')}
                disabled={isSubmitting}
              />
            </FieldContent>
            {errors.email && (
              <p className="text-destructive text-sm">{errors.email.message}</p>
            )}
          </Field>

          {/* Username Field */}
          <Field>
            <Label htmlFor="username">Username</Label>
            <FieldContent>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                {...register('username')}
                disabled={isSubmitting}
              />
            </FieldContent>
            {errors.username && (
              <p className="text-destructive text-sm">{errors.username.message}</p>
            )}
          </Field>

          {/* Password Fields */}
          <div className="grid grid-cols-2 gap-4">
            <Field>
              <Label htmlFor="password">Password</Label>
              <FieldContent>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Enter your password"
                    className="pr-10"
                    {...register('password')}
                    disabled={isSubmitting}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute h-auto inset-y-0 right-0 pr-3 flex items-center"
                    disabled={isSubmitting}
                  >
                    {showPassword ? (
                      <FiEyeOff
                        className="h-4 w-4 text-muted-foreground hover:text-foreground"
                      />
                    ) : (
                      <FiEye
                        className="h-4 w-4 text-muted-foreground hover:text-foreground"
                      />
                    )}
                  </Button>
                </div>
              </FieldContent>
              {errors.password && (
                <p className="text-destructive text-sm">{errors.password.message}</p>
              )}
            </Field>

            <Field>
              <Label htmlFor="password_confirm">Confirm Password</Label>
              <FieldContent>
                <div className="relative">
                  <Input
                    id="password_confirm"
                    type={showPasswordConfirm ? 'text' : 'password'}
                    placeholder="Enter password again"
                    className="pr-10"
                    {...register('confirmPassword')}
                    disabled={isSubmitting}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    onClick={() => setShowPasswordConfirm(!showPasswordConfirm)}
                    className="absolute h-auto inset-y-0 right-0 pr-3 flex items-center"
                    disabled={isSubmitting}
                  >
                    {showPasswordConfirm ? (
                      <FiEyeOff
                        className="h-4 w-4 text-muted-foreground hover:text-foreground"
                      />
                    ) : (
                      <FiEye
                        className="h-4 w-4 text-muted-foreground hover:text-foreground"
                      />
                    )}
                  </Button>
                </div>
              </FieldContent>
              {errors.confirmPassword && (
                <p className="text-destructive text-sm">{errors.confirmPassword.message}</p>
              )}
            </Field>
          </div>

          {/* Terms and Conditions */}
          <Field>
            <FieldContent>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="acceptTerms"
                  checked={watch('acceptTerms')}
                  onCheckedChange={(checked: boolean) => setValue('acceptTerms', checked)}
                  disabled={isSubmitting}
                  className="rounded border-gray-300 text-primary focus:ring-primary"
                />
                <Label htmlFor="acceptTerms" className="text-sm text-muted-foreground">
                  I agree to the{' '}
                  <a
                    href="/terms"
                    className="text-primary hover:underline"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Terms and Conditions
                  </a>
                </Label>
              </div>
            </FieldContent>
            {errors.acceptTerms && (
              <p className="text-destructive text-sm">{errors.acceptTerms.message}</p>
            )}
          </Field>
        </FieldGroup>

        {/* Register Button */}
        <Button
          type="submit"
          className="w-full"
          disabled={isSubmitting || isPending}
        >
          {isSubmitting || isPending ? 'Creating Account...' : 'Create Account'}
        </Button>
      </form>

      {/* Divider */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <span className="w-full border-t" />
        </div>
        <div className="relative flex justify-center text-xs uppercase">
          <span className="bg-background px-2 text-muted-foreground">
            Or continue with
          </span>
        </div>
      </div>

      {/* Social Media Login */}
      <div className="space-y-3">
        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLoginClick('Google')}
          disabled={isSocialLoading === 'Google' || isSubmitting}
        >
          <FiGoogle className="mr-2 h-4 w-4" />
          {isSocialLoading === 'Google' ? 'Connecting...' : 'Continue with Google'}
        </Button>

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLoginClick('Facebook')}
          disabled={isSocialLoading === 'Facebook' || isSubmitting}
        >
          <FiFacebook className="mr-2 h-4 w-4" color="#1877F2" />
          {isSocialLoading === 'Facebook' ? 'Connecting...' : 'Continue with Facebook'}
        </Button>

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLoginClick('Github')}
          disabled={isSocialLoading === 'Github' || isSubmitting}
        >
          <FiGithub className="mr-2 h-4 w-4" />
          {isSocialLoading === 'Github' ? 'Connecting...' : 'Continue with Github'}
        </Button>
      </div>
    </div>
  );
};

export default RegisterForm;
