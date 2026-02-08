'use client';

import React, { use } from 'react';
import { useRouter } from 'next/navigation';
import { useThemes, useDeleteTheme } from '@/hooks/themes';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { PageHeader } from '@/components/ui/typography';
import StoreLayout from '@/components/layouts/store-layout';
import {
  Palette,
  Paintbrush,
  FileCode,
  Layers,
  Plus,
  Trash2,
  Edit,
  Eye,
} from 'lucide-react';
import { Theme } from '@/types/themes.types';

export default function ThemesPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const resolvedParams = use(params);
  const storeId = resolvedParams.id;
  const router = useRouter();

  const { data: themes, isLoading, error, mutate } = useThemes();
  const { deleteTheme, isLoading: isDeleting } = useDeleteTheme();

  const handleDelete = async (themeId: string) => {
    if (!confirm('Are you sure you want to delete this theme?')) return;
    try {
      await deleteTheme(themeId);
      mutate();
    } catch (err) {
      console.error('Failed to delete theme:', err);
    }
  };

  const handleOpenBuilder = (themeId: string) => {
    router.push(`/stores/${storeId}/builder?theme=${themeId}`);
  };

  return (
    <StoreLayout params={params}>
      <div className="space-y-6">
        <PageHeader
          title="Themes"
          description="Manage your store's visual themes, color schemes, and templates."
          actions={
            <Button onClick={() => router.push(`/stores/${storeId}/themes/create`)}>
              <Plus className="h-4 w-4 mr-2" />
              New Theme
            </Button>
          }
        />

        {isLoading && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[1, 2, 3].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <Skeleton className="h-5 w-40" />
                </CardHeader>
                <CardContent className="space-y-3">
                  <Skeleton className="h-24 w-full rounded-md" />
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-4 w-1/2" />
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-700">Failed to load themes. Please try again.</p>
          </div>
        )}

        {themes && themes.length === 0 && (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Palette className="h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-1">No themes yet</h3>
              <p className="text-sm text-gray-500 mb-4">Create your first theme to start customizing your store.</p>
              <Button onClick={() => router.push(`/stores/${storeId}/themes/create`)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Theme
              </Button>
            </CardContent>
          </Card>
        )}

        {themes && themes.length > 0 && (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {themes.map((theme: Theme) => (
              <ThemeCard
                key={theme.id}
                theme={theme}
                onDelete={handleDelete}
                onOpenBuilder={handleOpenBuilder}
                isDeleting={isDeleting}
              />
            ))}
          </div>
        )}
      </div>
    </StoreLayout>
  );
}

function ThemeCard({
  theme,
  onDelete,
  onOpenBuilder,
  isDeleting,
}: {
  theme: Theme;
  onDelete: (id: string) => void;
  onOpenBuilder: (id: string) => void;
  isDeleting: boolean;
}) {
  const defaultScheme = theme.color_schemes?.find((cs) => cs.is_default) || theme.color_schemes?.[0];

  return (
    <Card className="group relative overflow-hidden hover:shadow-lg transition-shadow">
      {/* Color preview strip */}
      <div className="h-2 flex">
        {defaultScheme ? (
          <>
            <div className="flex-1" style={{ backgroundColor: defaultScheme.colors.primary_button.background }} />
            <div className="flex-1" style={{ backgroundColor: defaultScheme.colors.links }} />
            <div className="flex-1" style={{ backgroundColor: defaultScheme.colors.headings }} />
            <div className="flex-1" style={{ backgroundColor: defaultScheme.colors.text }} />
            <div className="flex-1" style={{ backgroundColor: defaultScheme.colors.borders }} />
          </>
        ) : (
          <div className="flex-1 bg-gradient-to-r from-blue-500 via-purple-500 to-pink-500" />
        )}
      </div>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div>
            <CardTitle className="text-base">{theme.name}</CardTitle>
            {theme.description && (
              <p className="text-sm text-gray-500 mt-1 line-clamp-2">{theme.description}</p>
            )}
          </div>
          {theme.is_default && (
            <Badge variant="secondary" className="ml-2 shrink-0">Default</Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Stats */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2 text-gray-600">
            <Palette className="h-4 w-4" />
            <span>{theme.color_schemes?.length || 0} Color Schemes</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <FileCode className="h-4 w-4" />
            <span>{theme.templates?.length || 0} Templates</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <Paintbrush className="h-4 w-4" />
            <span>{theme.style_classes?.length || 0} Classes</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <Layers className="h-4 w-4" />
            <span>{theme.layouts?.length || 0} Layouts</span>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 pt-2 border-t">
          <Button
            variant="default"
            size="sm"
            className="flex-1"
            onClick={() => onOpenBuilder(theme.id)}
          >
            <Eye className="h-4 w-4 mr-1" />
            Open Builder
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onOpenBuilder(theme.id)}
          >
            <Edit className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onDelete(theme.id)}
            disabled={isDeleting || theme.is_default}
          >
            <Trash2 className="h-4 w-4 text-red-500" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
