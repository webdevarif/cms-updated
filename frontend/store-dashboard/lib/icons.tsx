// Centralized Icons Library
// Using different icon libraries: Hugeicons, React Icons, Lucide React

// Hugeicons Icons (for form fields)
import { HugeiconsIcon } from '@hugeicons/react';
import { LockIcon, EyeIcon } from '@hugeicons/core-free-icons';

// React Icons (for social media)
import { FcGoogle } from 'react-icons/fc';
import { FaFacebook, FaGithub } from 'react-icons/fa';

// Lucide React Icons (for general UI)
import { Eye, Mail, User, Check, X, AlertCircle, ChevronDown, ChevronUp, ChevronLeft, ChevronRight } from 'lucide-react';

// Type definitions for different icon libraries
type HugeiconsProps = {
  className?: string;
  style?: React.CSSProperties;
  width?: string | number;
  height?: string | number;
  color?: string;
  id?: string;
  title?: string;
  viewBox?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  strokeLinecap?: 'butt' | 'round' | 'square' | 'inherit';
  strokeLinejoin?: 'round' | 'inherit' | 'miter' | 'bevel';
  opacity?: number | string;
  transform?: string;
  [key: string]: unknown;
};

type ReactIconsProps = {
  className?: string;
  style?: React.CSSProperties;
  width?: string | number;
  height?: string | number;
  color?: string;
  id?: string;
  title?: string;
  viewBox?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number | string;
  strokeLinecap?: 'butt' | 'round' | 'square' | 'inherit';
  strokeLinejoin?: 'round' | 'inherit' | 'miter' | 'bevel';
  opacity?: number | string;
  transform?: string;
  [key: string]: unknown;
};

type LucideProps = {
  className?: string;
  style?: React.CSSProperties;
  width?: string | number;
  height?: string | number;
  color?: string;
  id?: string;
  title?: string;
  viewBox?: string;
  fill?: string;
  stroke?: string;
  strokeWidth?: number | string;
  strokeLinecap?: 'butt' | 'round' | 'square' | 'inherit';
  strokeLinejoin?: 'round' | 'inherit' | 'miter' | 'bevel';
  opacity?: number | string;
  transform?: string;
  [key: string]: unknown;
};

// Form Field Icons
export const FiLock = (props: HugeiconsProps) => (
  <HugeiconsIcon icon={LockIcon} {...props} />
);

export const FiEye = (props: HugeiconsProps) => (
  <HugeiconsIcon icon={EyeIcon} {...props} />
);

export const FiEyeOff = (props: LucideProps) => (
  <Eye {...props} />
);

// Social Media Icons
export const FiGoogle = (props: ReactIconsProps) => (
  <FcGoogle {...props} />
);

export const FiFacebook = (props: ReactIconsProps) => (
  <FaFacebook {...props} />
);

export const FiGithub = (props: ReactIconsProps) => (
  <FaGithub {...props} />
);

// General UI Icons (Lucide)
export const FiMail = Mail;
export const FiEmail = Mail;
export const FiUser = User;
export const FiCheck = Check;
export const FiX = X;
export const FiAlertCircle = AlertCircle;
export const FiChevronDown = ChevronDown;
export const FiChevronUp = ChevronUp;
export const FiChevronLeft = ChevronLeft;
export const FiChevronRight = ChevronRight;

// Icon configuration for consistent styling
export const iconConfig = {
  size: {
    xs: 'h-3 w-3',
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6',
    xl: 'h-8 w-8',
  },
  color: {
    primary: 'text-primary',
    secondary: 'text-secondary',
    muted: 'text-muted-foreground',
    destructive: 'text-destructive',
    github: '#000000',
  }
};

// Helper function for consistent icon sizing
export const getIconSize = (size: keyof typeof iconConfig.size) => iconConfig.size[size];

// Helper function for brand colors
export const getBrandColor = (brand: keyof typeof iconConfig.color) => {
  const color = iconConfig.color[brand];
  return color.startsWith('#') ? color : color;
};
