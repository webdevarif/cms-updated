import React from 'react';
import { cn } from '@/lib/utils';

// Typography variants and sizes
const headingVariants = {
  h1: 'text-4xl font-bold tracking-tight lg:text-5xl',
  h2: 'text-3xl font-semibold tracking-tight',
  h3: 'text-2xl font-semibold tracking-tight',
  h4: 'text-xl font-semibold tracking-tight',
  h5: 'text-lg font-semibold tracking-tight',
  h6: 'text-base font-semibold tracking-tight',
};

const paragraphVariants = {
  p1: 'text-lg leading-relaxed',
  p2: 'text-base leading-normal',
  p3: 'text-sm leading-relaxed',
  p4: 'text-xs leading-normal',
};

const textColors = {
  default: 'text-foreground',
  muted: 'text-muted-foreground',
  primary: 'text-primary',
  secondary: 'text-secondary',
  accent: 'text-accent',
  destructive: 'text-destructive',
  success: 'text-green-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
  info: 'text-blue-600',
};

// Heading Component
interface HeadingProps {
  as?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
  variant?: keyof typeof headingVariants;
  size?: keyof typeof headingVariants;
  color?: keyof typeof textColors;
  className?: string;
  children: React.ReactNode;
}

export const Heading: React.FC<HeadingProps> = ({
  as: Tag = 'h2',
  variant,
  size,
  color = 'default',
  className,
  children,
}) => {
  const variantClass = variant ? headingVariants[variant] : '';
  const sizeClass = size ? headingVariants[size] : '';
  const colorClass = textColors[color];

  const classes = cn(
    variantClass || sizeClass,
    colorClass,
    className
  );

  return <Tag className={classes}>{children}</Tag>;
};

// Paragraph Component
interface ParagraphProps {
  variant?: keyof typeof paragraphVariants;
  size?: keyof typeof paragraphVariants;
  color?: keyof typeof textColors;
  className?: string;
  children: React.ReactNode;
}

export const Paragraph: React.FC<ParagraphProps> = ({
  variant,
  size,
  color = 'default',
  className,
  children,
}) => {
  const variantClass = variant ? paragraphVariants[variant] : '';
  const sizeClass = size ? paragraphVariants[size] : '';
  const colorClass = textColors[color];

  const classes = cn(
    variantClass || sizeClass || paragraphVariants.p2,
    colorClass,
    className
  );

  return <p className={classes}>{children}</p>;
};

// Text Component (for spans, divs, etc.)
interface TextProps {
  as?: 'span' | 'div' | 'small';
  variant?: keyof typeof paragraphVariants;
  size?: keyof typeof paragraphVariants;
  color?: keyof typeof textColors;
  className?: string;
  children: React.ReactNode;
}

export const Text: React.FC<TextProps> = ({
  as: Tag = 'span',
  variant,
  size,
  color = 'default',
  className,
  children,
}) => {
  const variantClass = variant ? paragraphVariants[variant] : '';
  const sizeClass = size ? paragraphVariants[size] : '';
  const colorClass = textColors[color];

  const classes = cn(
    variantClass || sizeClass || paragraphVariants.p2,
    colorClass,
    className
  );

  return <Tag className={classes}>{children}</Tag>;
};

// Section Title Component (for page sections)
interface SectionTitleProps {
  title: string;
  subtitle?: string;
  centered?: boolean;
  className?: string;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({
  title,
  subtitle,
  centered = false,
  className,
}) => {
  return (
    <div className={cn('space-y-2', centered && 'text-center', className)}>
      <Heading variant="h2" color="default">
        {title}
      </Heading>
      {subtitle && (
        <Paragraph variant="p2" color="muted">
          {subtitle}
        </Paragraph>
      )}
    </div>
  );
};

// Page Header Component
interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  actions,
  className,
}) => {
  return (
    <div className={cn('flex flex-col gap-4 md:flex-row md:items-center md:justify-between', className)}>
      <div className="space-y-1">
        <Heading variant="h1" color="default">
          {title}
        </Heading>
        {description && (
          <Paragraph variant="p2" color="muted">
            {description}
          </Paragraph>
        )}
      </div>
      {actions && <div className="flex-shrink-0">{actions}</div>}
    </div>
  );
};

// Export all components
export { headingVariants, paragraphVariants, textColors };
export type { HeadingProps, ParagraphProps, TextProps, SectionTitleProps, PageHeaderProps };
