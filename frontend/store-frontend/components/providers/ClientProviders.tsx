'use client';

import { NextIntlClientProvider } from 'next-intl';
import { SessionProvider } from 'next-auth/react';
import { SWRProvider } from '@/providers/SWRProvider';

interface ProvidersProps {
  children: React.ReactNode;
  messages: Record<string, string>;
  locale: string;
}

export function Providers({ children, messages, locale }: ProvidersProps) {
  return (
    <NextIntlClientProvider locale={locale} messages={messages}>
      <SessionProvider>
        <SWRProvider>
          {children}
        </SWRProvider>
      </SessionProvider>
    </NextIntlClientProvider>
  );
}
