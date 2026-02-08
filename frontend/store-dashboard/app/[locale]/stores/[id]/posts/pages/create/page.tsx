'use client';

import React, { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useCreatePage, useCategories } from '@/hooks/posts';
import { pageCreateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { MultiSelect } from '@/components/ui/multi-select';


import StoreLayout from '@/components/layouts/store-layout';
export default function CreatePagePage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const router = useRouter();

  // TODO: Get actual store ID from context or auth
  // For now, using a hardcoded store ID to test API functionality
  const storeId = '1'; // Temporary hardcoded store ID

  const { data: categories } = useCategories();
  const { createPage, isLoading } = useCreatePage();

  // Form state
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('html');
  const [status, setStatus] = useState('draft');
  const [isFeatured, setIsFeatured] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = pageCreateSchema.parse({
        title,
        slug,
        excerpt,
        content,
        content_type: contentType,
        status,
        is_featured: isFeatured,
        categories: selectedCategories,
        store: storeId,
      });
      await createPage(result);
      router.push(`/stores/${storeId}/posts/pages`);
    } catch (error) {
      console.error('Error creating page:', error);
    }
  };

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Page</h1>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="status">Status</Label>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="published">Published</SelectItem>
                <SelectItem value="archived">Archived</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <Label htmlFor="contentType">Content Type</Label>
            <Select value={contentType} onValueChange={setContentType}>
              <SelectTrigger>
                <SelectValue placeholder="Select content type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="html">HTML</SelectItem>
                <SelectItem value="markdown">Markdown</SelectItem>
                <SelectItem value="json">JSON</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div>
          <Label htmlFor="title">Title</Label>
          <Input
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>

        <div>
          <Label htmlFor="slug">Slug (optional)</Label>
          <Input
            id="slug"
            value={slug}
            onChange={(e) => setSlug(e.target.value)}
          />
          <p className="text-sm text-gray-600 mt-1">Leave empty to auto-generate from title</p>
        </div>

        <div>
          <Label htmlFor="excerpt">Excerpt</Label>
          <Textarea
            id="excerpt"
            value={excerpt}
            onChange={(e) => setExcerpt(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="content">Content</Label>
          <Textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={10}
            required
          />
        </div>

        <div className="flex items-center gap-2">
          <Checkbox
            id="isFeatured"
            checked={isFeatured}
            onCheckedChange={(checked) => setIsFeatured(checked as boolean)}
          />
          <Label htmlFor="isFeatured">Featured</Label>
        </div>

        {categories && categories.length > 0 && (
          <div>
            <Label>Categories</Label>
            <MultiSelect
              options={categories.map(cat => ({ value: cat.id, label: cat.name }))}
              selected={selectedCategories}
              onChange={setSelectedCategories}
              placeholder="Select categories"
              className="mt-2"
            />
          </div>
        )}

        <div className="flex gap-2">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Page'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
      </StoreLayout>
  );
}
