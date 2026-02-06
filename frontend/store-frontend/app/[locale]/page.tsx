import { Metadata } from 'next';
import { createLocalizedMetadata } from '@/lib/metadata';
import { useTranslations } from 'next-intl';

export async function generateMetadata({ params }: { params: Promise<{ locale: string }> }): Promise<Metadata> {
  const { locale } = await params;
  
  return createLocalizedMetadata(locale, {
    title: 'Home',
    description: 'Welcome to Digital Farmers CMS - Your modern agricultural management solution',
    keywords: ['home', 'dashboard', 'agriculture', 'farming', 'cms'],
  });
}

export default function Page() {
  const t = useTranslations('home');

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

        <div className="mt-8 text-sm text-gray-500">
          Locale-specific content loaded successfully!
        </div>
    </div>
    </main>
  );
}
