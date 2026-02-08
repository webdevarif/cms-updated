import { useApiGet } from './api-hooks';
import { ROUTES } from '@/lib/routes';

// External API hooks (example for weather)
export function useWeather(city: string) {
  const url = `${ROUTES.API.EXTERNAL.WEATHER}?q=${city}&appid=your-api-key`;
  return useApiGet<Record<string, unknown>>(url, { withAuth: false });
}

// Add more external API hooks here as needed
// export function usePayments() { ... }
// export function useAnalytics() { ... }
