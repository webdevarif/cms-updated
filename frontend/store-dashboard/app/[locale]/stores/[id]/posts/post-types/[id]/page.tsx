'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { usePostType, useUpdatePostType } from '@/hooks/posts';
import { postTypeUpdateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function PostTypeDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: postType, error, isLoading } = usePostType(id);
  const { updatePostType, isLoading: isUpdating } = useUpdatePostType();
  
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [isActive, setIsActive] = useState(true);

  // Initialize form when data loads
  React.useEffect(() => {
    if (postType) {
      setName(postType.name);
      setDescription(postType.description || '');
      setIsActive(postType.is_active);
    }
  }, [postType]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = postTypeUpdateSchema.parse({ name, description, is_active: isActive });
      await updatePostType(id, result);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating post type:', error);
    }
  };

  const handleCancel = () => {
    if (postType) {
      setName(postType.name);
      setDescription(postType.description || '');
      setIsActive(postType.is_active);
    }
    setIsEditing(false);
  };

  if (isLoading) return <div>Loading post type...</div>;
  if (error) return <div>Error loading post type: {(error as Error).message}</div>;
  if (!postType) return <div>Post type not found</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Post Type Details</h1>
        <div className="flex gap-2">
          {!isEditing && (
            <Button onClick={() => setIsEditing(true)}>Edit</Button>
          )}
          <Button variant="outline" onClick={() => router.back()}>Back</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{postType.name}</CardTitle>
          <div className="flex gap-2">
            <Badge variant={postType.is_active ? 'default' : 'secondary'}>
              {postType.is_active ? 'Active' : 'Inactive'}
            </Badge>
            <Badge variant={postType.is_builtin ? 'outline' : 'default'}>
              {postType.is_builtin ? 'Builtin' : 'Custom'}
            </Badge>
          </div>
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
                <h3 className="font-semibold">Key</h3>
                <p>{postType.key}</p>
              </div>
              <div>
                <h3 className="font-semibold">Description</h3>
                <p>{postType.description || 'No description'}</p>
              </div>
              <div>
                <h3 className="font-semibold">Post Count</h3>
                <p>{postType.post_count} posts</p>
              </div>
              <div>
                <h3 className="font-semibold">Created</h3>
                <p>{new Date(postType.created_at).toLocaleDateString()}</p>
              </div>
              <div>
                <h3 className="font-semibold">Last Updated</h3>
                <p>{new Date(postType.updated_at).toLocaleDateString()}</p>
              </div>
              {postType.schema && (
                <div>
                  <h3 className="font-semibold">Schema</h3>
                  <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto">
                    {JSON.stringify(postType.schema, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
