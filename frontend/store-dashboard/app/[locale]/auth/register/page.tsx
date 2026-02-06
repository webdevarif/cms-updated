import React from 'react'
import { Metadata } from 'next'
import PageContent from './page-content'
import { createLocalizedMetadata } from '@/lib/metadata'

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  return createLocalizedMetadata(locale, {
    title: 'Register',
    description: 'Create your Digital Farmers CMS account',
    keywords: ['register', 'signup', 'create account', 'join'],
    noIndex: true,
  });
}

const Register = () => {
  return (
    <PageContent />
  )
}

export default Register;
