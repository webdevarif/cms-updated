'use client';

import React, { useState, useMemo } from 'react';
import { usePosts, usePostTypes } from '@/hooks/posts';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Link from 'next/link';
import { Post } from '@/types/posts.types';
import StoreLayout from '@/components/layouts/store-layout';

export default function PostsPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const { data: posts, error, isLoading } = usePosts();
  const { data: postTypes } = usePostTypes();

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [postTypeFilter, setPostTypeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [contentTypeFilter, setContentTypeFilter] = useState('all');
  const [isFeaturedFilter, setIsFeaturedFilter] = useState('all');
  const [ordering, setOrdering] = useState('-created_at');

  // Memoized filtered posts
  const filteredPosts = useMemo(() => {
    if (!Array.isArray(posts)) return [];

    return posts?.filter((post: Post) => {
      const matchesSearch = !searchTerm ||
        post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.slug?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        post.excerpt?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesPostType = postTypeFilter === 'all' || post.post_type.id === postTypeFilter;
      const matchesStatus = statusFilter === 'all' || post.status === statusFilter;
      const matchesContentType = contentTypeFilter === 'all' || post.content_type === contentTypeFilter;
      const matchesFeatured = isFeaturedFilter === 'all' ||
        (isFeaturedFilter === 'true' ? post.is_featured : !post.is_featured);

      return matchesSearch && matchesPostType && matchesStatus && matchesContentType && matchesFeatured;
    });
  }, [posts, searchTerm, postTypeFilter, statusFilter, contentTypeFilter, isFeaturedFilter]);

  if (isLoading) return <div>Loading posts...</div>;
  if (error) return <div>Error loading posts: {(error as Error).message}</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Posts</h1>
          <Button asChild>
            <Link href="/posts/create">Create Post</Link>
          </Button>
        </div>

        {/* Filters */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-4">
          <Input
            placeholder="Search posts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <Select value={postTypeFilter} onValueChange={setPostTypeFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Post Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              {Array.isArray(postTypes) && postTypes?.map(type => (
                <SelectItem key={type.id} value={type.id}>
                  {type.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="published">Published</SelectItem>
              <SelectItem value="archived">Archived</SelectItem>
            </SelectContent>
          </Select>

          <Select value={contentTypeFilter} onValueChange={setContentTypeFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Content Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="html">HTML</SelectItem>
              <SelectItem value="markdown">Markdown</SelectItem>
              <SelectItem value="json">JSON</SelectItem>
            </SelectContent>
          </Select>

          <Select value={isFeaturedFilter} onValueChange={setIsFeaturedFilter}>
            <SelectTrigger>
              <SelectValue placeholder="Featured" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="true">Featured</SelectItem>
              <SelectItem value="false">Not Featured</SelectItem>
            </SelectContent>
          </Select>

          <Select value={ordering} onValueChange={setOrdering}>
            <SelectTrigger>
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="-created_at">Newest First</SelectItem>
              <SelectItem value="created_at">Oldest First</SelectItem>
              <SelectItem value="title">Title A-Z</SelectItem>
              <SelectItem value="-title">Title Z-A</SelectItem>
              <SelectItem value="-published_at">Recently Published</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Featured</TableHead>
              <TableHead>Content Type</TableHead>
              <TableHead>Created By</TableHead>
              <TableHead>Updated By</TableHead>
              <TableHead>Published</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredPosts?.map((post: Post) => (
              <TableRow key={post.id}>
                <TableCell>
                  <div>
                    <div className="font-medium">{post.title}</div>
                    {post.slug && <div className="text-sm text-gray-500">/{post.slug}</div>}
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{post.post_type_name}</Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={
                    post.status === 'published' ? 'default' :
                    post.status === 'draft' ? 'secondary' : 'outline'
                  }>
                    {post.status}
                  </Badge>
                </TableCell>
                <TableCell>
                  {post.is_featured && <Badge variant="default">⭐</Badge>}
                </TableCell>
                <TableCell>
                  <Badge variant="outline">{post.content_type}</Badge>
                </TableCell>
                <TableCell>{post.created_by?.username || 'Unknown'}</TableCell>
                <TableCell>{post.updated_by?.username || 'Unknown'}</TableCell>
                <TableCell>
                  {post.published_at ? new Date(post.published_at).toLocaleDateString() : '-'}
                </TableCell>
                <TableCell>{new Date(post.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  <Button asChild variant="outline" size="sm" className="mr-2">
                    <Link href={`/posts/${post.id}`}>View</Link>
                  </Button>
                  <Button variant="outline" size="sm" className="mr-2" onClick={() => { /* Edit handler */ }}>Edit</Button>
                  <Button variant="destructive" size="sm" onClick={() => { /* Delete handler */ }}>Delete</Button>
                </TableCell>
              </TableRow>
            )) || <TableRow><TableCell colSpan={10}>No posts found</TableCell></TableRow>}
          </TableBody>
        </Table>
      </div>
    </StoreLayout>
  );
}
