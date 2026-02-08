'use client';

import React, { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useCategory, useUpdateCategory, useDeleteCategory } from '@/hooks/posts';
import { categoryUpdateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Category } from '@/types/posts.types';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';


import StoreLayout from '@/components/layouts/store-layout';
export default function CategoryDetailPage({ params }: { params: Promise<{ id: string; locale: string; catid: string }> }) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const id = resolvedParams.catid;
  const { data: category, error, isLoading } = useCategory(categoryId);
  const { updateCategory, isLoading: isUpdating } = useUpdateCategory();
  const { deleteCategory, isLoading: isDeleting } = useDeleteCategory();

  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [parentId, setParentId] = useState('');
  const [isActive, setIsActive] = useState(true);

  // Initialize form when data loads
  React.useEffect(() => {
    if (category) {
      setName(category.name);
      setSlug(category.slug || '');
      setDescription(category.description || '');
      setParentId(category.parent?.id || '');
      setIsActive(category.is_active);
    }
  }, [category]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = categoryUpdateSchema.parse({
        name,
        slug,
        description,
        parent: parentId || undefined,
        is_active: isActive,
      });
      await updateCategory(id, result as unknown as Partial<Category>);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating category:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this category?')) {
      try {
        await deleteCategory(id);
        router.push(`/stores/${storeId}/posts/categories`);
      } catch (error) {
        console.error('Error deleting category:', error);
      }
    }
  };

  const handleCancel = () => {
    if (category) {
      setName(category.name);
      setSlug(category.slug || '');
      setDescription(category.description || '');
      setParentId(category.parent?.id || '');
      setIsActive(category.is_active);
    }
    setIsEditing(false);
  };

  if (isLoading) return <div>Loading category...</div>;
  if (error) return <div>Error loading category: {(error as Error).message}</div>;
  if (!category) return <div>Category not found</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Category Details</h1>
        <div className="flex gap-2">
          {!isEditing && (
            <>
              <Button onClick={() => setIsEditing(true)}>Edit</Button>
              <Button variant="destructive" onClick={handleDelete} disabled={isDeleting}>
                {isDeleting ? 'Deleting...' : 'Delete'}
              </Button>
            </>
          )}
          <Button variant="outline" onClick={() => router.back()}>Back</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {category.name}
            <Badge variant={category.is_active ? 'default' : 'secondary'}>
              {category.is_active ? 'Active' : 'Inactive'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleUpdate} className="space-y-4">
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
                <Label htmlFor="slug">Slug</Label>
                <Input
                  id="slug"
                  value={slug}
                  onChange={(e) => setSlug(e.target.value)}
                />
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
                <Label htmlFor="parent">Parent Category</Label>
                <Select value={parentId} onValueChange={setParentId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select parent category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No parent</SelectItem>
                    {/* TODO: Load categories and filter out current category */}
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
                <Button type="submit" disabled={isUpdating}>
                  {isUpdating ? 'Updating...' : 'Update'}
                </Button>
                <Button type="button" variant="outline" onClick={handleCancel}>
                  Cancel
                </Button>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold">Slug</h3>
                <p>{category.slug || 'No slug'}</p>
              </div>
              <div>
                <h3 className="font-semibold">Description</h3>
                <p>{category.description || 'No description'}</p>
              </div>
              <div>
                <h3 className="font-semibold">Parent</h3>
                {category.parent ? (
                  <p>{category.parent.name}</p>
                ) : (
                  <p className="text-gray-500">No parent</p>
                )}
              </div>
              <div>
                <h3 className="font-semibold">Post Count</h3>
                <p>{category.post_count} posts</p>
              </div>
              <div>
                <h3 className="font-semibold">Created</h3>
                <p>{new Date(category.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <h3 className="font-semibold">Last Updated</h3>
                <p>{new Date(category.updated_at).toLocaleDateString()}</p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
      </StoreLayout>
  );
}
