import React from 'react'
import { Metadata } from 'next'
import PageContent from './page-content'
import { createLocalizedMetadata } from '@/lib/metadata'

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  return createLocalizedMetadata(locale, {
    title: 'Stores',
    description: 'Manage your store locations and inventory',
    keywords: ['stores', 'inventory', 'locations', 'management', 'retail'],
  });
}

const Stores = () => {
  return (
    <PageContent />
  )
}

export default Stores;
