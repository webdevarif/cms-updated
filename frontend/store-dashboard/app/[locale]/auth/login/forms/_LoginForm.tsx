"use client";
import React, { useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useLogin } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent, FieldGroup } from '@/components/ui/field';
import { Link } from '@/i18n/navigation';
import { FiEye, FiEyeOff, FiGoogle, FiFacebook, FiGithub } from '@/lib/icons';
import { loginSchema, LoginFormData } from '@/schemas/auth.schemas';
import { handleGoogleLogin, handleFacebookLogin, handleGithubLogin } from '@/handles/auth.handles';
import { ROUTES } from '@/lib/routes';
import { showToast } from '@/lib/toast';
import { Paragraph } from '@/components/ui/typography';

const LoginForm = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const { login, isLoading } = useLogin();

  const {
    register,
    handleSubmit,
    formState: { errors },
    control,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      login: '',
      password: '',
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setFormError(null);
    try {
      await login(data);
      showToast.success('Login successful!');
      // Redirect is handled in useLogin hook
    } catch (error: unknown) {
      // Set inline error message (do not reset form)
      const authError = error as { isAuthError?: boolean; status?: number; message?: string };
      if (authError?.isAuthError && authError.status === 401) {
        setFormError(authError.message || 'Incorrect username or password');
      } else {
        setFormError('Something went wrong. Please try again.');
      }

      // Show a single toast for the error
      showToast.error(formError || 'Something went wrong. Please try again.');
    }
  };

  const handleSocialLoginClick = async (provider: string) => {
    try {
      console.log(`Social login with ${provider}`);
      switch (provider) {
        case 'Google':
          await handleGoogleLogin();
          break;
        case 'Facebook':
          await handleFacebookLogin();
          break;
        case 'Github':
          await handleGithubLogin();
          break;
        default:
          console.error('Unsupported social provider:', provider);
      }
    } catch (error) {
      console.error('Social login error:', error);
    }
  };

  return (
    <div className="w-full max-w-[25rem] space-y-6">
      {formError && (
        <Paragraph className="text-sm text-red-500 text-center">
          {formError}
        </Paragraph>
      )}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FieldGroup>
          {/* Username/Email Field */}
          <Field>
            <Label htmlFor="login">Username or Email</Label>
            <FieldContent>
              <Input
                id="login"
                type="text"
                className="pr-10"
                placeholder="Enter your username or email"
                {...register('login')}
              />
            </FieldContent>
            {errors.login && (
              <p className="text-destructive text-sm">{errors.login.message}</p>
            )}
          </Field>

          {/* Password Field */}
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
                />
                <Button
                  variant={'ghost'}
                  type='button'
                  size={'icon'}
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 h-auto right-0 px-3 hover:bg-transparent flex items-center"
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

          {/* Remember Me & Forgot Password */}
          <Field>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Controller
                  name="rememberMe"
                  control={control}
                  render={({ field }) => (
                    <Checkbox
                      id="remember"
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  )}
                />
                <Label
                  htmlFor="remember"
                  className="text-sm font-medium cursor-pointer"
                >
                  Remember me
                </Label>
              </div>
              <Button
                type='button'
                variant={'link'}
                asChild
                className='p-0 h-auto'
              >
                <Link href={ROUTES.AUTH.FORGET_PASSWORD}>
                  Forgot Password?
                </Link>
              </Button>
            </div>
          </Field>
        </FieldGroup>

        {/* Sign In Button */}
        <Button type="submit" className="w-full" disabled={isLoading}>
          {isLoading ? 'Signing in...' : 'Sign In'}
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
        >
          <FiGoogle className="mr-2 h-4 w-4" />
          Continue with Google
        </Button>

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLoginClick('Facebook')}
        >
          <FiFacebook className="mr-2 h-4 w-4" color="#1877F2" />
          Continue with Facebook
        </Button>

        <Button
          type="button"
          variant="outline"
          className="w-full"
          onClick={() => handleSocialLoginClick('Github')}
        >
          <FiGithub className="mr-2 h-4 w-4" />
          Continue with Github
        </Button>
      </div>
    </div>
  );
};

export default LoginForm;
