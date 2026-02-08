'use client';

import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useCreatePost, usePostTypes, useCategories } from '@/hooks/posts';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { MultiSelect } from '@/components/ui/multi-select';
import { SkeletonCard } from '@/components/ui/skeleton';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { postCreateSchema, PostCreateFormData } from '@/schemas/posts.schemas';
import { PageHeader } from '@/components/ui/typography';


import StoreLayout from '@/components/layouts/store-layout';
export default function CreatePostPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const router = useRouter();
  const params = useParams();
  const storeId = params.id as string;

  const { data: postTypes, isLoading: postTypesLoading } = usePostTypes(storeId);
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const { createPost, isLoading } = useCreatePost();

  const form = useForm({
    resolver: zodResolver(postCreateSchema),
    defaultValues: {
      post_type: '',
      title: '',
      slug: '',
      excerpt: '',
      content: '',
      content_type: 'html',
      status: 'draft',
      is_featured: false,
      categories: [],
      store: storeId,
    },
  });

  const onSubmit = async (data: PostCreateFormData) => {
    try {
      await createPost(data);
      router.push(`/stores/${storeId}/posts`);
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  if (postTypesLoading || categoriesLoading) {
    return (
    <StoreLayout params={params}>
      <div className="p-4">
        <PageHeader title="Create New Post" />
        <div className="space-y-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <PageHeader
        title="Create New Post"
        description="Create a new post with categories and tags"
      />

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 max-w-4xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="post_type">Post Type</Label>
            <Controller
              name="post_type"
              control={form.control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select post type" />
                  </SelectTrigger>
                  <SelectContent>
                    {postTypes?.map(type => (
                      <SelectItem key={type.id} value={type.id}>
                        {type.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            />
            {form.formState.errors.post_type && (
              <p className="text-sm text-red-500">{form.formState.errors.post_type.message}</p>
            )}
          </div>
          <div>
            <Label htmlFor="status">Status</Label>
            <Controller
              name="status"
              control={form.control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>
        </div>

        <div>
          <Label htmlFor="title">Title</Label>
          <Controller
            name="title"
            control={form.control}
            render={({ field }) => (
              <Input
                id="title"
                {...field}
                placeholder="Enter post title"
              />
            )}
          />
          {form.formState.errors.title && (
            <p className="text-sm text-red-500">{form.formState.errors.title.message}</p>
          )}
        </div>

        <div>
          <Label htmlFor="slug">Slug (optional)</Label>
          <Controller
            name="slug"
            control={form.control}
            render={({ field }) => (
              <Input
                id="slug"
                {...field}
                placeholder="post-slug"
              />
            )}
          />
          <p className="text-sm text-gray-600 mt-1">Leave empty to auto-generate from title</p>
        </div>

        <div>
          <Label htmlFor="excerpt">Excerpt</Label>
          <Controller
            name="excerpt"
            control={form.control}
            render={({ field }) => (
              <Textarea
                id="excerpt"
                {...field}
                placeholder="Brief description of the post"
                rows={3}
              />
            )}
          />
        </div>

        <div>
          <Label htmlFor="content">Content</Label>
          <Controller
            name="content"
            control={form.control}
            render={({ field }) => (
              <Textarea
                id="content"
                {...field}
                placeholder="Write your post content here..."
                rows={10}
              />
            )}
          />
          {form.formState.errors.content && (
            <p className="text-sm text-red-500">{form.formState.errors.content.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="content_type">Content Type</Label>
            <Controller
              name="content_type"
              control={form.control}
              render={({ field }) => (
                <Select
                  value={field.value}
                  onValueChange={field.onChange}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select content type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="html">HTML</SelectItem>
                    <SelectItem value="markdown">Markdown</SelectItem>
                    <SelectItem value="json">JSON</SelectItem>
                  </SelectContent>
                </Select>
              )}
            />
          </div>
          <div className="flex items-center gap-2">
            <Controller
              name="is_featured"
              control={form.control}
              render={({ field }) => (
                <Checkbox
                  id="is_featured"
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              )}
            />
            <Label htmlFor="is_featured">Featured</Label>
          </div>
        </div>

        {categories && categories.length > 0 && (
          <div>
            <Label>Categories</Label>
            <Controller
              name="categories"
              control={form.control}
              render={({ field }) => (
                <MultiSelect
                  options={categories.map(cat => ({ value: cat.id, label: cat.name }))}
                  selected={field.value || []}
                  onChange={field.onChange}
                  placeholder="Select categories"
                  className="mt-2"
                />
              )}
            />
          </div>
        )}

        <div className="flex gap-2">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Post'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
