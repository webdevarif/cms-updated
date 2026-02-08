import { Metadata } from 'next'
import PageContent from './page-content'
import { createLocalizedMetadata } from '@/lib/metadata'

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;

  return createLocalizedMetadata(locale, {
    title: 'Login',
    description: 'Sign in to your Digital Farmers CMS account',
    keywords: ['login', 'signin', 'authentication', 'account'],
    noIndex: true,
  });
}

const Login = () => {
  return (
    <PageContent />
  )
}

export default Login;
