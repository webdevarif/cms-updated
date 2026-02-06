'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreatePostType } from '@/hooks/posts';
import { postTypeCreateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

export default function CreatePostTypePage() {
  const [name, setName] = useState('');
  const [key, setKey] = useState('');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);
  const { createPostType, isLoading } = useCreatePostType();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = postTypeCreateSchema.parse({ name, key, description, is_active: isActive });
      await createPostType(result);
      router.push('/posts/post-types');
    } catch (error) {
      console.error('Error creating post type:', error);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Post Type</h1>
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
          <Label htmlFor="key">Key</Label>
          <Input
            id="key"
            value={key}
            onChange={(e) => setKey(e.target.value)}
            required
          />
          <p className="text-sm text-gray-600 mt-1">URL-safe key, lowercase with hyphens</p>
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="isActive"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
          />
          <Label htmlFor="isActive">Active</Label>
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Post Type'}
        </Button>
      </form>
    </div>
  );
}
