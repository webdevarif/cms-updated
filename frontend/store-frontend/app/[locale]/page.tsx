'use client';

import { useTranslations } from 'next-intl';
import { Link, usePathname } from '@/lib/navigation';
import { locales } from '@/i18n/request';

export default function Page() {
  const t = useTranslations('home');
  const pathname = usePathname();

  return (
    <main className="min-h-screen flex items-center justify-center p-8">
      <div className="max-w-2xl mx-auto text-center">
        <h1 className="text-4xl font-bold mb-4">{t('title')}</h1>
        <p className="text-lg text-gray-600 mb-8">{t('description')}</p>

        <div className="space-y-4">
          <h2 className="text-2xl font-semibold">{t('welcome')}</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-8">
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold">{t('featuredProducts')}</h3>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold">{t('categories')}</h3>
            </div>
            <div className="p-4 border rounded-lg">
              <h3 className="font-semibold">{t('contact')}</h3>
            </div>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="mt-12 space-y-4">
          <h2 className="text-lg font-semibold">Navigation</h2>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Home
            </Link>
            <Link href="/dashboard" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Dashboard
            </Link>
            <Link href="/auth/login" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              Login
            </Link>
            <Link href="/auth/register" className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
              Register
            </Link>
            <Link href="/contact-us" className="px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
              Contact Us
            </Link>
          </div>
        </div>

        {/* Locale Switcher */}
        <div className="mt-8 space-y-4">
          <h2 className="text-lg font-semibold">Language / Locale</h2>
          <div className="flex justify-center gap-2">
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

        <div className="mt-8 text-sm text-gray-500">
          Locale-specific content loaded successfully!
        </div>
      </div>
    </main>
  );
}
