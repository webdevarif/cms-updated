import React from 'react'
import { Metadata } from 'next'
import PageContent from './page-content'
import { createLocalizedMetadata } from '@/lib/metadata'

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  return createLocalizedMetadata(locale, {
    title: 'Contact Us',
    description: 'Get in touch with the Digital Farmers team',
    keywords: ['contact', 'support', 'help', 'team', 'communication'],
  });
}

const ContactUs = () => {
  return (
    <PageContent />
  )
}

export default ContactUs;
