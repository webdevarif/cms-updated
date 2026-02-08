import AuthLayout from '@/components/layouts/auth-layout';
import LoginForm from './forms/_LoginForm';
import { Link } from '@/i18n/navigation';
import { ROUTES } from '@/lib/routes';
import { Button } from '@/components/ui/button';
import { Heading, Paragraph, Text } from '@/components/ui/typography';

const PageContent = () => {
  return (
    <AuthLayout>
      <div className="p-4 lg:p-8 flex flex-col justify-center items-center w-full h-full space-y-10">
        <div className="w-full max-w-[25rem] text-center">
          <Heading variant="h2" className="mb-6">
            Login
          </Heading>
          <Paragraph variant="p2" color="muted" className="mb-6">
            Welcome back! Please login to your account
          </Paragraph>
        </div>

        <LoginForm />

        <div className="">
          <Text color="muted">
            Don&apos;t have an account?{' '}
            <Button variant={'link'} asChild>
              <Link className='link-primary' href={ROUTES.AUTH.REGISTER}>Sign Up</Link>
            </Button>
          </Text>
        </div>
      </div>
    </AuthLayout>
  )
}

export default PageContent;
