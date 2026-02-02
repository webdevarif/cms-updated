'use client';

import { useTranslations } from 'next-intl';
import { Link, usePathname } from '@/i18n/navigation';
import { locales } from '@/i18n/request';
import { ROUTES } from '@/lib/routes';

export function ComponentExample() {
  const t = useTranslations('dashboard');
  const pathname = usePathname();

  // Debug: Check if translations are working
  console.log('Translation test:', {
    title: t('title'),
    description: t('description'),
    hasTitle: t.has('title'),
    hasDescription: t.has('description')
  });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <p className="mt-2">{t('description')}</p>

      {/* Navigation Links */}
      <div className="mt-8 space-y-4">
        <h2 className="text-lg font-semibold">Navigation</h2>
        <div className="space-y-2">
          <Link href={ROUTES.HOME} className="block text-blue-600 hover:text-blue-800">
            Home
          </Link>
          <Link href={ROUTES.DASHBOARD} className="block text-blue-600 hover:text-blue-800">
            Dashboard
          </Link>
          <Link href={ROUTES.DASHBOARD_STORES} className="block text-blue-600 hover:text-blue-800">
            Stores
          </Link>
          <Link href={ROUTES.LOGIN} className="block text-blue-600 hover:text-blue-800">
            Login
          </Link>
          <Link href={ROUTES.REGISTER} className="block text-blue-600 hover:text-blue-800">
            Register
          </Link>
          <Link href={ROUTES.CONTACT_US} className="block text-blue-600 hover:text-blue-800">
            Contact Us
          </Link>
        </div>
      </div>

      {/* Locale Switcher */}
      <div className="mt-8 space-y-4">
        <h2 className="text-lg font-semibold">Language / Locale</h2>
        <div className="flex gap-2">
          {locales.map((locale) => (
            <Link
              key={locale}
              href={pathname}
              locale={locale}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
            >
              {locale.toUpperCase()}
            </Link>
          ))}
        </div>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Debug: title exists: {t.has('title') ? 'YES' : 'NO'}, description exists: {t.has('description') ? 'YES' : 'NO'}
      </div>
    </div>
  );
}
