import { NextIntlClientProvider } from 'next-intl';
import { setRequestLocale } from 'next-intl/server';
import { hasLocale } from 'next-intl';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

interface StoresLayoutProps {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}

export default async function StoresLayout({ children, params }: StoresLayoutProps) {
  const { locale } = await params;

  // Validate locale
  if (!hasLocale(routing.locales, locale)) {
    notFound();
  }

  // Enable static rendering
  setRequestLocale(locale);

  return (
    <NextIntlClientProvider>
      {children}
    </NextIntlClientProvider>
  );
}
