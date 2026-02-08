import { Metadata } from 'next';

// Base metadata configuration
export const baseMetadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  title: {
    default: 'Digital Farmers CMS',
    template: '%s | Digital Farmers CMS'
  },
  description: 'Modern agricultural management system with internationalization and authentication',
  keywords: ['agriculture', 'farming', 'cms', 'management', 'digital'],
  authors: [{ name: 'Digital Farmers Team' }],
  creator: 'Digital Farmers',
  publisher: 'Digital Farmers',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    siteName: 'Digital Farmers CMS',
    title: 'Digital Farmers CMS',
    description: 'Modern agricultural management system with internationalization and authentication',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Digital Farmers CMS',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Digital Farmers CMS',
    description: 'Modern agricultural management system with internationalization and authentication',
    images: ['/og-image.png'],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: process.env.GOOGLE_SITE_VERIFICATION,
    yandex: process.env.YANDEX_VERIFICATION,
    yahoo: process.env.YAHOO_VERIFICATION,
  },
};

// Page-specific metadata generators
export const createPageMetadata = (options: {
  title: string;
  description?: string;
  keywords?: string[];
  image?: string;
  noIndex?: boolean;
  locale?: string;
}): Metadata => {
  const {
    title,
    description,
    keywords,
    image = '/og-image.png',
    noIndex = false,
    locale = 'en_US'
  } = options;

  return {
    metadataBase: baseMetadata.metadataBase,
    title: title + ' | Digital Farmers CMS', // Explicitly apply template
    description: description || baseMetadata.description,
    keywords: keywords ? keywords.join(', ') : (baseMetadata.keywords as string[])?.join(', ') || '',
    authors: baseMetadata.authors,
    creator: baseMetadata.creator as string | undefined,
    publisher: baseMetadata.publisher as string | undefined,
    formatDetection: baseMetadata.formatDetection,
    openGraph: {
      ...baseMetadata.openGraph,
      title: title + ' | Digital Farmers CMS', // Also apply to OpenGraph
      description: description || (baseMetadata.openGraph?.description as string),
      locale,
      images: [
        {
          url: image,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
    },
    twitter: {
      ...baseMetadata.twitter,
      title: title + ' | Digital Farmers CMS', // Also apply to Twitter
      description: description || (baseMetadata.twitter?.description as string),
      images: [image],
    },
    robots: noIndex
      ? {
          index: false,
          follow: false,
          googleBot: {
            index: false,
            follow: false,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
          },
        }
      : baseMetadata.robots,
    verification: {
      google: baseMetadata.verification?.google || undefined,
      yandex: baseMetadata.verification?.yandex || undefined,
      yahoo: baseMetadata.verification?.yahoo || undefined,
    },
  };
};

// Specific page metadata configurations
export const pageMetadata = {
  home: createPageMetadata({
    title: 'Home',
    description: 'Welcome to Digital Farmers CMS - Your modern agricultural management solution',
    keywords: ['home', 'dashboard', 'agriculture', 'farming'],
  }),
  login: createPageMetadata({
    title: 'Login',
    description: 'Sign in to your Digital Farmers CMS account',
    keywords: ['login', 'signin', 'authentication'],
    noIndex: true,
  }),
  register: createPageMetadata({
    title: 'Register',
    description: 'Create your Digital Farmers CMS account',
    keywords: ['register', 'signup', 'create account'],
    noIndex: true,
  }),
  dashboard: createPageMetadata({
    title: 'Dashboard',
    description: 'Manage your agricultural operations from the main dashboard',
    keywords: ['dashboard', 'management', 'operations'],
  }),
  stores: createPageMetadata({
    title: 'Stores',
    description: 'Manage your store locations and inventory',
    keywords: ['stores', 'inventory', 'locations'],
  }),
  contact: createPageMetadata({
    title: 'Contact Us',
    description: 'Get in touch with the Digital Farmers team',
    keywords: ['contact', 'support', 'help'],
  }),
  notFound: createPageMetadata({
    title: 'Page Not Found',
    description: 'The page you are looking for does not exist',
    noIndex: true,
  }),
  error: createPageMetadata({
    title: 'Error',
    description: 'An unexpected error occurred',
    noIndex: true,
  }),
};

// Locale-specific metadata helpers
export const createLocalizedMetadata = (
  locale: string,
  baseOptions: Parameters<typeof createPageMetadata>[0]
): Metadata => {
  const localeConfig = {
    en: { locale: 'en_US', description: 'Modern agricultural management system' },
    es: { locale: 'es_ES', description: 'Sistema moderno de gestión agrícola' },
    fr: { locale: 'fr_FR', description: 'Système moderne de gestion agricole' },
    bn: { locale: 'bn_BD', description: 'আধুনিক কৃষি ব্যবস্থাপনা সিস্টেম' },
  };

  const config = localeConfig[locale as keyof typeof localeConfig] || localeConfig.en;

  return createPageMetadata({
    ...baseOptions,
    description: baseOptions.description || config.description,
    locale: config.locale,
  });
};

// Dynamic metadata generator for dynamic routes
export const createDynamicPageMetadata = (
  title: string,
  description: string,
  options: {
    keywords?: string[];
    image?: string;
    noIndex?: boolean;
    locale?: string;
  } = {}
): Metadata => {
  return createPageMetadata({
    title,
    description,
    ...options,
  });
};

// Helper function for creating metadata with dynamic parameters (Next.js 16 compatible)
export const createPageMetadataWithParams = async (
  baseOptions: Parameters<typeof createPageMetadata>[0],
  params?: Record<string, string | number> | Promise<Record<string, string | number>>
): Promise<Metadata> => {
  let { title, description } = baseOptions;

  // Handle Promise-based params (Next.js 16)
  const resolvedParams = params && typeof params.then === 'function' ? await params : params;

  // Replace placeholders in title and description with actual values
  if (resolvedParams) {
    Object.entries(resolvedParams).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`;
      title = title.replace(new RegExp(placeholder, 'g'), String(value));
      if (description) {
        description = description.replace(new RegExp(placeholder, 'g'), String(value));
      }
    });
  }

  return createPageMetadata({
    ...baseOptions,
    title,
    description,
  });
};

// Example usage helper for common dynamic patterns (Next.js 16 compatible)
export const createEntityPageMetadata = async (
  entityName: string,
  entityId: string | number,
  action: 'view' | 'edit' | 'create' = 'view',
  locale: string = 'en_US'
): Promise<Metadata> => {
  const actionText = {
    view: 'View',
    edit: 'Edit',
    create: 'Create'
  }[action];

  return createLocalizedMetadata(locale, {
    title: `${actionText} ${entityName}`,
    description: `${actionText} ${entityName} ${action === 'create' ? 'form' : `with ID: ${entityId}`}`,
    keywords: [entityName.toLowerCase(), action, 'management'],
  });
};

// Helper for Next.js 16 dynamic routes with Promise params
export const createDynamicRouteMetadata = async (
  params: Promise<{ locale: string } & Record<string, string | number>>,
  metadataOptions: {
    title: string;
    description?: string;
    keywords?: string[];
    noIndex?: boolean;
  }
): Promise<Metadata> => {
  const resolvedParams = await params;
  const { locale, ...routeParams } = resolvedParams;

  return createPageMetadataWithParams(
    {
      ...metadataOptions,
      locale,
    },
    routeParams
  );
};

export type { Metadata };
