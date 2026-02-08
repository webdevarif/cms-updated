import { toast } from 'sonner';

// Toast utility functions for consistent usage throughout the app

export const showToast = {
  success: (message: string) => {
    toast.success(message);
  },

  error: (message: string) => {
    toast.error(message);
  },

  info: (message: string) => {
    toast.info(message);
  },

  warning: (message: string) => {
    toast.warning(message);
  },

  loading: (message: string) => {
    return toast.loading(message);
  },

  dismiss: (id?: string | number) => {
    toast.dismiss(id);
  },

  // Custom toast with more options
  custom: (message: string, options?: {
    duration?: number;
    position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'top-center' | 'bottom-center';
    icon?: string | React.ReactNode;
    action?: {
      label: string;
      onClick: () => void;
    };
  }) => {
    toast(message, options);
  }
};

// Export the toast function directly for advanced usage
export { toast };

// Default export for convenience
export default showToast;
