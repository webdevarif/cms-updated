import StoreClientLayout from './StoreClientLayout';
import { getTranslations } from 'next-intl/server';

type StoreLayoutProps = {
  children: React.ReactNode;
  params: Promise<{ id: string | string[]; locale: string }>;
};

export default async function StoreLayout({ children, params }: StoreLayoutProps) {
  const resolvedParams = await params;
  const storeId = Array.isArray(resolvedParams.id) ? resolvedParams.id[0] : resolvedParams.id;

  return (
    <StoreClientLayout storeId={storeId || ''}>
      {children}
    </StoreClientLayout>
  );
}

export async function generateMetadata() {
  const t = await getTranslations('store');

  return {
    title: t('storeManagement'),
    description: t('manageYourStore'),
  };
}
