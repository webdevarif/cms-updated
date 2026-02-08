import AuthLayout from '@/components/layouts/auth-layout';
import { Link } from '@/i18n/navigation';
import { ROUTES } from '@/lib/routes';
import { Button } from '@/components/ui/button';
import { Heading, Paragraph, Text } from '@/components/ui/typography';
import RegisterForm from './forms/_RegisterForm';

const PageContent = () => {
  return (
    <AuthLayout>
      <div className="p-4 lg:p-8 flex flex-col justify-center items-center w-full h-full space-y-10">
        <div className="w-full max-w-[25rem] text-center">
          <Heading variant="h2" className="mb-6">
            Register
          </Heading>
          <Paragraph variant="p2" color="muted" className="mb-6">
            Welcome back! create an account
          </Paragraph>
        </div>

        <RegisterForm />

        <div className="">
          <Text color="muted">
            Already have an account?{' '}
            <Button variant={'link'} asChild>
              <Link href={ROUTES.AUTH.LOGIN}>Sign In</Link>
            </Button>
          </Text>
        </div>
      </div>
    </AuthLayout>
  )
}

export default PageContent;
