'use client';
import { useTranslations } from 'next-intl';
import LangSwitcher from '@/components/lang-switcher';
import ModeSwitcher from '@/components/mode-switcher';

const PageContent = () => {
  const t = useTranslations('dashboard');

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold">{t('title')}</h1>
      <p className="mt-2">{t('description')}</p>

      {/* Dropdown Switchers Everywhere */}
      <div className="mt-8">
        <h2 className="text-lg font-semibold mb-4">Dropdown Switchers - Use Anywhere</h2>
        <div className="space-y-4">
          <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg border border-blue-200 dark:border-blue-700">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-3">Header Style</h3>
            <div className="flex items-center gap-4">
              <span className="text-sm text-blue-700 dark:text-blue-300">Language:</span>
              <LangSwitcher />
              <span className="text-sm text-blue-700 dark:text-blue-300 ml-4">Theme:</span>
              <ModeSwitcher />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PageContent;
