'use client';

import React, { use, useState, useMemo, useCallback } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';
import { useThemes, useTheme } from '@/hooks/themes';
import { useTemplates, useUpdateTemplate } from '@/hooks/themes';
import { useLayouts } from '@/hooks/themes';
import { BuilderLayout } from '@/components/builder/builder-layout';
import { Skeleton } from '@/components/ui/skeleton';

export default function BuilderPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const resolvedParams = use(params);
  const storeId = resolvedParams.id;
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  // URL-driven state
  const themeIdParam = searchParams.get('theme') || '';
  const templateIdParam = searchParams.get('template') || '';

  const { data: themes, isLoading: themesLoading } = useThemes(storeId);

  // Derive the effective theme ID: URL param > default > first
  const effectiveThemeId = useMemo(() => {
    if (themeIdParam) return themeIdParam;
    if (themes && themes.length > 0) {
      const defaultTheme = themes.find((t) => t.is_default) || themes[0];
      return defaultTheme.id;
    }
    return '';
  }, [themeIdParam, themes]);

  const { data: selectedTheme, isLoading: themeLoading } = useTheme(effectiveThemeId, storeId);
  const { data: templates } = useTemplates(effectiveThemeId || undefined, storeId);
  const { data: layouts } = useLayouts(effectiveThemeId || undefined, storeId);
  const { updateTemplate, isLoading: isSaving } = useUpdateTemplate();

  // Derive the effective template ID: URL param > first body template > first template
  const effectiveTemplateId = useMemo(() => {
    if (templateIdParam) return templateIdParam;
    if (templates && templates.length > 0) {
      const bodyTemplate = templates.find((t) => t.template_role === 'body');
      return (bodyTemplate || templates[0]).id;
    }
    return '';
  }, [templateIdParam, templates]);

  const selectedTemplate = templates?.find((t) => t.id === effectiveTemplateId) || null;

  // Find the default layout for header/footer in preview
  const defaultLayout = useMemo(() => {
    if (!layouts || layouts.length === 0) return null;
    return layouts.find((l) => l.is_default) || layouts[0];
  }, [layouts]);

  // Local content editing state (tracks unsaved changes)
  const [editedContent, setEditedContent] = useState<string | null>(null);
  const isDirty = editedContent !== null;

  // When template changes, reset edited content
  const currentContent = editedContent ?? selectedTemplate?.content ?? '';

  // Update URL query params without full navigation
  const updateQueryParams = useCallback((key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) {
      params.set(key, value);
    } else {
      params.delete(key);
    }
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
  }, [searchParams, router, pathname]);

  const handleSelectTheme = useCallback((themeId: string) => {
    const params = new URLSearchParams(searchParams.toString());
    params.set('theme', themeId);
    params.delete('template'); // Reset template when theme changes
    router.replace(`${pathname}?${params.toString()}`, { scroll: false });
    setEditedContent(null);
  }, [searchParams, router, pathname]);

  const handleSelectTemplate = useCallback((templateId: string) => {
    updateQueryParams('template', templateId);
    setEditedContent(null);
  }, [updateQueryParams]);

  const handleContentChange = useCallback((content: string) => {
    setEditedContent(content);
  }, []);

  const handleSave = async () => {
    if (!selectedTemplate || editedContent === null) return;
    try {
      await updateTemplate(selectedTemplate.id, {
        content: editedContent,
      }, storeId);
      setEditedContent(null); // Reset dirty state after save
    } catch (err) {
      console.error('Failed to save template:', err);
    }
  };

  const handlePublish = async () => {
    if (!selectedTemplate) return;
    try {
      await updateTemplate(selectedTemplate.id, { is_active: true }, storeId);
    } catch (err) {
      console.error('Failed to publish template:', err);
    }
  };

  if (themesLoading || themeLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-100">
        <div className="space-y-4 text-center">
          <Skeleton className="h-8 w-48 mx-auto" />
          <Skeleton className="h-4 w-64 mx-auto" />
        </div>
      </div>
    );
  }

  return (
    <BuilderLayout
      storeId={storeId}
      themes={themes || []}
      templates={templates || []}
      selectedTheme={selectedTheme || null}
      selectedTemplate={selectedTemplate}
      defaultLayout={defaultLayout}
      currentContent={currentContent}
      onContentChange={handleContentChange}
      onSelectTheme={handleSelectTheme}
      onSelectTemplate={handleSelectTemplate}
      onSave={handleSave}
      onPublish={handlePublish}
      isSaving={isSaving}
      isDirty={isDirty}
    />
  );
}
