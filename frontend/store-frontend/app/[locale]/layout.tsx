import type { ReactNode } from "react";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, localeDirections } from "@/i18n/request";

type Props = {
  children: ReactNode;
  params: Promise<{ locale: string }>;
};

export default async function LocaleLayout(props: Props) {
  const { children, params } = props;
  const { locale } = await params;

  const messages = await getMessages(locale);
  const dir = localeDirections[locale as keyof typeof localeDirections] ?? 'ltr';

  console.log("Store-frontend layout debug:", {
    locale,
    dir,
    messagesKeys: Object.keys(messages),
  });

  return (
    <NextIntlClientProvider
      locale={locale}
      messages={messages}
      timeZone="UTC"
    >
      {children}
    </NextIntlClientProvider>
  );
}
