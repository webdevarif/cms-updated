'use client';

import React, { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateCategory, useCategories } from '@/hooks/posts';
import { categoryCreateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';


import StoreLayout from '@/components/layouts/store-layout';
export default function CreateCategoryPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const router = useRouter();
  const { data: categories } = useCategories();
  const { createCategory, isLoading } = useCreateCategory();

  // Form state
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [parentId, setParentId] = useState('');
  const [isActive, setIsActive] = useState(true);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = categoryCreateSchema.parse({
        name,
        slug,
        description,
        parent: parentId || undefined,
        is_active: isActive,
      });
      await createCategory(result);
      router.push(`/stores/${storeId}/posts/categories`);
    } catch (error) {
      console.error('Error creating category:', error);
    }
  };

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Category</h1>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
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
          <p className="text-sm text-gray-600 mt-1">Leave empty to auto-generate from name</p>
        </div>

        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div>
          <Label htmlFor="parent">Parent Category (optional)</Label>
          <Select value={parentId} onValueChange={setParentId}>
            <SelectTrigger>
              <SelectValue placeholder="Select parent category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">No parent</SelectItem>
              {categories?.filter(cat => cat.id !== parentId).map(category => (
                <SelectItem key={category.id} value={category.id}>
                  {category.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Checkbox
            id="isActive"
            checked={isActive}
            onCheckedChange={(checked) => setIsActive(checked as boolean)}
          />
          <Label htmlFor="isActive">Active</Label>
        </div>

        <div className="flex gap-2">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Category'}
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
