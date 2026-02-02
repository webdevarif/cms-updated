'use client';

import { NextIntlClientProvider } from 'next-intl';
import { SessionProvider } from 'next-auth/react';
import { SWRProvider } from '@/providers/SWRProvider';

interface ProvidersProps {
  children: React.ReactNode;
  messages: Record<string, Record<string, string>>; // Proper type for nested translation objects
  locale: string;
  timeZone: string;
}

export function Providers({ children, messages, locale, timeZone }: ProvidersProps) {
  return (
    <NextIntlClientProvider locale={locale} messages={messages} timeZone={timeZone}>
      <SessionProvider>
        <SWRProvider>
          {children}
        </SWRProvider>
      </SessionProvider>
    </NextIntlClientProvider>
  );
}
