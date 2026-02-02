import Link from 'next/link';
import { usePathname as useNextPathname, useRouter as useNextRouter } from 'next/navigation';
import { locales } from '../i18n/request';

// Custom Link component that handles locale routing
export function Link({ href, locale, children, ...props }: any) {
  const pathname = usePathname();
  const currentLocale = pathname.split('/')[1];

  // If locale is provided, use it, otherwise use current locale
  const targetLocale = locale || currentLocale;

  // Ensure href starts with /
  const normalizedHref = href.startsWith('/') ? href : `/${href}`;

  // Add locale prefix if not already present
  const hrefWithLocale = normalizedHref.startsWith(`/${targetLocale}`)
    ? normalizedHref
    : `/${targetLocale}${normalizedHref}`;

  return (
    <Link href={hrefWithLocale} {...props}>
      {children}
    </Link>
  );
}

// Custom usePathname that returns path without locale
export function usePathname() {
  const pathname = useNextRouter().pathname;
  const segments = pathname.split('/');
  // Remove locale segment if present
  if (locales.includes(segments[1] as any)) {
    return '/' + segments.slice(2).join('/');
  }
  return pathname;
}

// Custom useRouter
export function useRouter() {
  const router = useNextRouter();

  return {
    ...router,
    push: (href: string, options?: any) => {
      const pathname = router.pathname;
      const currentLocale = pathname.split('/')[1];

      const normalizedHref = href.startsWith('/') ? href : `/${href}`;
      const hrefWithLocale = normalizedHref.startsWith(`/${currentLocale}`)
        ? normalizedHref
        : `/${currentLocale}${normalizedHref}`;

      router.push(hrefWithLocale, options);
    },
    replace: (href: string, options?: any) => {
      const pathname = router.pathname;
      const currentLocale = pathname.split('/')[1];

      const normalizedHref = href.startsWith('/') ? href : `/${href}`;
      const hrefWithLocale = normalizedHref.startsWith(`/${currentLocale}`)
        ? normalizedHref
        : `/${currentLocale}${normalizedHref}`;

      router.replace(hrefWithLocale, options);
    }
  };
}

// Simple redirect function
export function redirect(href: string) {
  const currentLocale = typeof window !== 'undefined'
    ? window.location.pathname.split('/')[1]
    : 'en';

  const normalizedHref = href.startsWith('/') ? href : `/${href}`;
  const hrefWithLocale = normalizedHref.startsWith(`/${currentLocale}`)
    ? normalizedHref
    : `/${currentLocale}${normalizedHref}`;

  if (typeof window !== 'undefined') {
    window.location.href = hrefWithLocale;
  }
}
