'use client';

import React, { useState } from 'react';
import { usePostTypes, useDeletePostType } from '@/hooks/posts';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import Link from 'next/link';
import StoreLayout from '@/components/layouts/store-layout';

export default function PostTypesPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const { data: postTypes, error, isLoading, mutate } = usePostTypes();
  const { deletePostType, isLoading: isDeleting } = useDeletePostType();
  const [searchTerm, setSearchTerm] = useState('');
  const [showActiveOnly, setShowActiveOnly] = useState(false);
  const [showBuiltinOnly, setShowBuiltinOnly] = useState(false);

  const filteredPostTypes = Array.isArray(postTypes) ? postTypes.filter(postType => {
    const matchesSearch = postType.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         postType.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         postType.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesActive = !showActiveOnly || postType.is_active;
    const matchesBuiltin = !showBuiltinOnly || postType.is_builtin;
    return matchesSearch && matchesActive && matchesBuiltin;
  }) : [];

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this post type?')) {
      try {
        await deletePostType(id);
        mutate();
      } catch (err) {
        console.error('Delete failed:', err);
      }
    }
  };

  if (isLoading) return <div>Loading post types...</div>;
  if (error) return <div>Error loading post types: {(error as Error).message}</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Post Types</h1>
        <Button asChild>
          <Link href="/posts/post-types/create">Create Post Type</Link>
        </Button>
      </div>

      <div className="flex gap-4 mb-4">
        <Input
          placeholder="Search post types..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="max-w-sm"
        />
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showActiveOnly}
            onChange={(e) => setShowActiveOnly(e.target.checked)}
          />
          Active only
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={showBuiltinOnly}
            onChange={(e) => setShowBuiltinOnly(e.target.checked)}
          />
          Builtin only
        </label>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Key</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Posts</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredPostTypes?.map(postType => (
            <TableRow key={postType.id}>
              <TableCell>{postType.name}</TableCell>
              <TableCell>{postType.key}</TableCell>
              <TableCell>{postType.description}</TableCell>
              <TableCell>
                <Badge variant={postType.is_active ? 'default' : 'secondary'}>
                  {postType.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={postType.is_builtin ? 'outline' : 'default'}>
                  {postType.is_builtin ? 'Builtin' : 'Custom'}
                </Badge>
              </TableCell>
              <TableCell>{postType.post_count}</TableCell>
              <TableCell>{new Date(postType.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <Button asChild variant="outline" size="sm" className="mr-2">
                  <Link href={`/posts/post-types/${postType.id}`}>View</Link>
                </Button>
                <Button variant="outline" size="sm" className="mr-2" onClick={() => { /* Edit handler */ }}>Edit</Button>
                {!postType.is_builtin && (
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(postType.id)} disabled={isDeleting}>
                    Delete
                  </Button>
                )}
              </TableCell>
            </TableRow>
          )) || <TableRow><TableCell colSpan={8}>No post types found</TableCell></TableRow>}
        </TableBody>
      </Table>
      </div>
    </StoreLayout>
  );
}
