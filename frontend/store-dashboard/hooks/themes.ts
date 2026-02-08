'use client';

import { useState, useCallback } from 'react';
import useSWR from 'swr';
import { apiClient } from '@/lib/api-client';
import { ROUTES, buildUrlWithParams } from '@/lib/routes';
import {
  Theme,
  ColorScheme,
  Layout,
  StyleClass,
  Template,
  ThemeCreateFormData,
  ThemeUpdateFormData,
  ColorSchemeCreateFormData,
  ColorSchemeUpdateFormData,
  TemplateCreateFormData,
  TemplateUpdateFormData,
  StyleClassCreateFormData,
  StyleClassUpdateFormData,
  LayoutCreateFormData,
} from '@/types/themes.types';

// Type for paginated responses
interface PaginatedData<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}

// ─── Theme Hooks ──────────────────────────────────────────────────────────────

export function useThemes(storeId?: string | number) {
  const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.LIST, { store: storeId }) : null;

  const { data, error, isLoading, mutate } = useSWR<Theme[]>(
    url,
    async (url: string) => {
      console.log('Fetching themes from:', url);
      try {
        const res = await apiClient.get<PaginatedData<Theme>>(url);
        console.log('Themes API response:', res);
        const themes = Array.isArray(res.data) ? res.data : res.data.results || [];
        console.log('Extracted themes array:', themes);
        return themes;
      } catch (err) {
        console.warn('Failed to fetch themes:', err);
        return []; // Return empty array on error
      }
    },
    {
      onError: (error) => {
        console.warn('Themes fetch error:', error);
      }
    }
  );

  // Debug logging
  console.log('useThemes hook state:', { url, data, error, isLoading });

  return { data: data || [], error, isLoading, mutate };
}

export function useTheme(id: string | number, storeId?: string | number) {
  const url = id && storeId ? buildUrlWithParams(ROUTES.API.THEMES.DETAIL, { store: storeId, id }) : null;
  const { data, error, isLoading, mutate } = useSWR<Theme>(url, async (url: string) => {
    const res = await apiClient.get<Theme>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateTheme() {
  const [isLoading, setIsLoading] = useState(false);
  const createTheme = useCallback(async (data: ThemeCreateFormData): Promise<Theme> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<Theme>(ROUTES.API.THEMES.CREATE, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createTheme, isLoading };
}

export function useUpdateTheme() {
  const [isLoading, setIsLoading] = useState(false);
  const updateTheme = useCallback(async (id: string | number, data: ThemeUpdateFormData, storeId?: string | number): Promise<Theme> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.UPDATE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for theme update');
      const res = await apiClient.patch<Theme>(url, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateTheme, isLoading };
}

export function useDeleteTheme() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteTheme = useCallback(async (id: string | number, storeId?: string | number): Promise<void> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.DELETE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for theme delete');
      await apiClient.delete(url);
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteTheme, isLoading };
}

// ─── Color Scheme Hooks ───────────────────────────────────────────────────────

export function useColorSchemes(themeId?: string | number, storeId?: string | number) {
  const url = themeId && storeId
    ? `${buildUrlWithParams(ROUTES.API.THEMES.COLOR_SCHEMES.LIST, { store: storeId })}?theme=${themeId}`
    : null;

  const { data, error, isLoading, mutate } = useSWR<ColorScheme[]>(
    url,
    async (url: string) => {
      try {
        const res = await apiClient.get<PaginatedData<ColorScheme> | ColorScheme[]>(url);
        return Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.warn('Failed to fetch color schemes:', err);
        return []; // Return empty array on error
      }
    },
    {
      onError: (error) => {
        console.warn('Color schemes fetch error:', error);
      }
    }
  );
  return { data: data || [], error, isLoading, mutate };
}

export function useCreateColorScheme() {
  const [isLoading, setIsLoading] = useState(false);
  const createColorScheme = useCallback(async (data: ColorSchemeCreateFormData): Promise<ColorScheme> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<ColorScheme>(ROUTES.API.THEMES.COLOR_SCHEMES.CREATE, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createColorScheme, isLoading };
}

export function useUpdateColorScheme() {
  const [isLoading, setIsLoading] = useState(false);
  const updateColorScheme = useCallback(async (id: string | number, data: ColorSchemeUpdateFormData, storeId?: string | number): Promise<ColorScheme> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.COLOR_SCHEMES.UPDATE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for color scheme update');
      const res = await apiClient.patch<ColorScheme>(url, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateColorScheme, isLoading };
}

// ─── Template Hooks ───────────────────────────────────────────────────────────

export function useTemplates(themeId?: string | number, storeId?: string | number) {
  const url = themeId && storeId
    ? `${buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.LIST, { store: storeId })}?theme=${themeId}`
    : null;

  const { data, error, isLoading, mutate } = useSWR<Template[]>(
    url,
    async (url: string) => {
      try {
        const res = await apiClient.get<PaginatedData<Template> | Template[]>(url);
        return Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.warn('Failed to fetch templates:', err);
        return []; // Return empty array on error
      }
    },
    {
      onError: (error) => {
        console.warn('Templates fetch error:', error);
      }
    }
  );
  return { data: data || [], error, isLoading, mutate };
}

export function useTemplate(id: string | number) {
  const url = buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.DETAIL, { id });
  const { data, error, isLoading, mutate } = useSWR<Template>(url, async (url: string) => {
    const res = await apiClient.get<Template>(url);
    return res.data;
  });
  return { data, error, isLoading, mutate };
}

export function useCreateTemplate() {
  const [isLoading, setIsLoading] = useState(false);
  const createTemplate = useCallback(async (data: TemplateCreateFormData): Promise<Template> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<Template>(ROUTES.API.THEMES.TEMPLATES.CREATE, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createTemplate, isLoading };
}

export function useUpdateTemplate() {
  const [isLoading, setIsLoading] = useState(false);
  const updateTemplate = useCallback(async (id: string | number, data: TemplateUpdateFormData, storeId?: string | number): Promise<Template> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.UPDATE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for template update');
      const res = await apiClient.patch<Template>(url, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateTemplate, isLoading };
}

export function useDeleteTemplate() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteTemplate = useCallback(async (id: string | number): Promise<void> => {
    setIsLoading(true);
    try {
      const url = buildUrlWithParams(ROUTES.API.THEMES.TEMPLATES.DELETE, { id });
      await apiClient.delete(url);
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteTemplate, isLoading };
}

// ─── Style Class Hooks ────────────────────────────────────────────────────────

export function useStyleClasses(themeId?: string | number, storeId?: string | number) {
  const url = themeId && storeId
    ? `${buildUrlWithParams(ROUTES.API.THEMES.STYLE_CLASSES.LIST, { store: storeId })}?theme=${themeId}`
    : null;

  const { data, error, isLoading, mutate } = useSWR<StyleClass[]>(
    url,
    async (url: string) => {
      try {
        const res = await apiClient.get<PaginatedData<StyleClass> | StyleClass[]>(url);
        return Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.warn('Failed to fetch style classes:', err);
        return []; // Return empty array on error
      }
    },
    {
      onError: (error) => {
        console.warn('Style classes fetch error:', error);
      }
    }
  );
  return { data: data || [], error, isLoading, mutate };
}

export function useCreateStyleClass() {
  const [isLoading, setIsLoading] = useState(false);
  const createStyleClass = useCallback(async (data: StyleClassCreateFormData): Promise<StyleClass> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<StyleClass>(ROUTES.API.THEMES.STYLE_CLASSES.CREATE, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createStyleClass, isLoading };
}

export function useUpdateStyleClass() {
  const [isLoading, setIsLoading] = useState(false);
  const updateStyleClass = useCallback(async (id: string | number, data: StyleClassUpdateFormData, storeId?: string | number): Promise<StyleClass> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.STYLE_CLASSES.UPDATE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for style class update');
      const res = await apiClient.patch<StyleClass>(url, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { updateStyleClass, isLoading };
}

export function useDeleteStyleClass() {
  const [isLoading, setIsLoading] = useState(false);
  const deleteStyleClass = useCallback(async (id: string | number, storeId?: string | number): Promise<void> => {
    setIsLoading(true);
    try {
      const url = storeId ? buildUrlWithParams(ROUTES.API.THEMES.STYLE_CLASSES.DELETE, { store: storeId, id }) : null;
      if (!url) throw new Error('Store ID required for style class delete');
      await apiClient.delete(url);
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { deleteStyleClass, isLoading };
}

// ─── Layout Hooks ─────────────────────────────────────────────────────────────

export function useLayouts(themeId?: string | number, storeId?: string | number) {
  const url = themeId && storeId
    ? `${buildUrlWithParams(ROUTES.API.THEMES.LAYOUTS.LIST, { store: storeId })}?theme=${themeId}`
    : null;

  const { data, error, isLoading, mutate } = useSWR<Layout[]>(
    url,
    async (url: string) => {
      try {
        const res = await apiClient.get<PaginatedData<Layout> | Layout[]>(url);
        return Array.isArray(res.data) ? res.data : res.data.results || [];
      } catch (err) {
        console.warn('Failed to fetch layouts:', err);
        return []; // Return empty array on error
      }
    },
    {
      onError: (error) => {
        console.warn('Layouts fetch error:', error);
      }
    }
  );
  return { data: data || [], error, isLoading, mutate };
}

export function useCreateLayout() {
  const [isLoading, setIsLoading] = useState(false);
  const createLayout = useCallback(async (data: LayoutCreateFormData): Promise<Layout> => {
    setIsLoading(true);
    try {
      const res = await apiClient.post<Layout>(ROUTES.API.THEMES.LAYOUTS.CREATE, data);
      return res.data;
    } finally {
      setIsLoading(false);
    }
  }, []);
  return { createLayout, isLoading };
}
