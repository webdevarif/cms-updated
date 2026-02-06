'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { usePost, usePostMeta, useAddPostMeta, useUpdatePostMeta, useDeletePostMeta } from '@/hooks/posts';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function PostMetadataPage() {
  const params = useParams();
  const router = useRouter();
  const postId = params.id as string;
  const { data: post, error, isLoading } = usePost(postId);
  const { data: metadata, mutate: mutateMeta } = usePostMeta(postId);
  const { addPostMeta } = useAddPostMeta();
  const { updatePostMeta } = useUpdatePostMeta();
  const { deletePostMeta } = useDeletePostMeta();
  
  const [isAdding, setIsAdding] = useState(false);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [editValue, setEditValue] = useState('');

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await addPostMeta(postId, { key: newKey, value: newValue } as { key: string; value: unknown });
      setNewKey('');
      setNewValue('');
      setIsAdding(false);
      mutateMeta();
    } catch (error) {
      console.error('Error adding metadata:', error);
    }
  };

  const handleEdit = async (key: string) => {
    try {
      await updatePostMeta(postId, { key, value: editValue });
      setEditingKey(null);
      setEditValue('');
      mutateMeta();
    } catch (error) {
      console.error('Error updating metadata:', error);
    }
  };

  const handleDelete = async (key: string) => {
    if (confirm(`Are you sure you want to delete metadata key "${key}"?`)) {
      try {
        await deletePostMeta(postId, key);
        mutateMeta();
      } catch (error) {
        console.error('Error deleting metadata:', error);
      }
    }
  };

  const startEdit = (key: string, value: unknown) => {
    setEditingKey(key);
    setEditValue(typeof value === 'string' ? value : JSON.stringify(value, null, 2));
  };

  const cancelEdit = () => {
    setEditingKey(null);
    setEditValue('');
  };

  if (isLoading) return <div>Loading post...</div>;
  if (error) return <div>Error loading post: {(error as Error).message}</div>;
  if (!post) return <div>Post not found</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h1 className="text-2xl font-bold">Post Metadata</h1>
          <p className="text-gray-600">Managing metadata for: {post.title}</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={() => setIsAdding(true)}>Add Metadata</Button>
          <Button variant="outline" onClick={() => router.back()}>Back to Post</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Metadata Key-Value Pairs</CardTitle>
        </CardHeader>
        <CardContent>
          {isAdding && (
            <div className="mb-6 p-4 border rounded">
              <h3 className="font-semibold mb-3">Add New Metadata</h3>
              <form onSubmit={handleAdd} className="space-y-3">
                <div>
                  <Label htmlFor="newKey">Key</Label>
                  <Input
                    id="newKey"
                    value={newKey}
                    onChange={(e) => setNewKey(e.target.value)}
                    placeholder="e.g., seo_description"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="newValue">Value (JSON)</Label>
                  <Textarea
                    id="newValue"
                    value={newValue}
                    onChange={(e) => setNewValue(e.target.value)}
                    placeholder='e.g., "A great blog post about..." or {"field": "value"}'
                    rows={3}
                    required
                  />
                  <p className="text-sm text-gray-600 mt-1">
                    Enter a string, number, boolean, or JSON object
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button type="submit">Add</Button>
                  <Button type="button" variant="outline" onClick={() => setIsAdding(false)}>
                    Cancel
                  </Button>
                </div>
              </form>
            </div>
          )}

          <div className="space-y-4">
            {metadata && Object.keys(metadata).length > 0 ? (
              Object.entries(metadata).map(([key, value]) => (
                <div key={key} className="border rounded p-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg">{key}</h4>
                      {editingKey === key ? (
                        <div className="mt-2 space-y-2">
                          <Textarea
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            rows={4}
                            className="font-mono text-sm"
                          />
                          <div className="flex gap-2">
                            <Button size="sm" onClick={() => handleEdit(key)}>
                              Save
                            </Button>
                            <Button size="sm" variant="outline" onClick={cancelEdit}>
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="mt-2">
                          <pre className="bg-gray-100 p-2 rounded text-sm overflow-auto max-h-32">
                            {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                          </pre>
                          <div className="flex gap-2 mt-2">
                            <Button size="sm" variant="outline" onClick={() => startEdit(key, value)}>
                              Edit
                            </Button>
                            <Button size="sm" variant="destructive" onClick={() => handleDelete(key)}>
                              Delete
                            </Button>
                          </div>
                        </div>
                      )}
                    </div>
                    <Badge variant="outline" className="ml-4">
                      {typeof value === 'string' ? 'string' : Array.isArray(value) ? 'array' : typeof value}
                    </Badge>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <p>No metadata found for this post.</p>
                <p className="text-sm mt-2">Click &quot;Add Metadata&quot; to get started.</p>
              </div>
            )}
          </div>

          <div className="mt-6 bg-blue-50 p-4 rounded">
            <h3 className="font-semibold mb-2">About Metadata:</h3>
            <ul className="text-sm space-y-1">
              <li>• Metadata allows storing additional key-value information for posts</li>
              <li>• Values can be strings, numbers, booleans, or JSON objects</li>
              <li>• Common uses: SEO data, custom fields, configuration settings</li>
              <li>• Metadata is automatically included in API responses</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
