import React from 'react'
import { Metadata } from 'next'
import PageContent from './page-content'
import { createLocalizedMetadata } from '@/lib/metadata'

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  return createLocalizedMetadata(locale, {
    title: 'Dashboard',
    description: 'Manage your agricultural operations from the main dashboard',
    keywords: ['dashboard', 'management', 'operations', 'agriculture', 'farming'],
  });
}

const Dashboard = () => {
  return (
    <PageContent />
  )
}

export default Dashboard;
