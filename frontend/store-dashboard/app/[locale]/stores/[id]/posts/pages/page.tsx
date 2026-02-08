'use client';

import React, { useState, useMemo } from 'react';
import { usePages } from '@/hooks/posts';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Link from 'next/link';
import { Post } from '@/types/posts.types';


import StoreLayout from '@/components/layouts/store-layout';
export default function PagesPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const { data: pages, error, isLoading } = usePages();
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [contentTypeFilter, setContentTypeFilter] = useState('all');
  const [isFeaturedFilter, setIsFeaturedFilter] = useState('all');
  const [ordering, setOrdering] = useState('-created_at');

  // Memoized filtered pages
  const filteredPages = useMemo(() => {
    return pages?.filter((page: Post) => {
      const matchesSearch = !searchTerm ||
        page.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        page.slug?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        page.excerpt?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesStatus = statusFilter === 'all' || page.status === statusFilter;
      const matchesContentType = contentTypeFilter === 'all' || page.content_type === contentTypeFilter;
      const matchesFeatured = isFeaturedFilter === 'all' ||
        (isFeaturedFilter === 'true' ? page.is_featured : !page.is_featured);

      return matchesSearch && matchesStatus && matchesContentType && matchesFeatured;
    });
  }, [pages, searchTerm, statusFilter, contentTypeFilter, isFeaturedFilter]);

  if (isLoading) return <div>Loading pages...</div>;
  if (error) return <div>Error loading pages: {(error as Error).message}</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Pages</h1>
        <Button asChild>
          <Link href="/posts/pages/create">Create Page</Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
        <Input
          placeholder="Search pages..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

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
          {filteredPages?.map((page: Post) => (
            <TableRow key={page.id}>
              <TableCell>
                <div>
                  <div className="font-medium">{page.title}</div>
                  {page.slug && <div className="text-sm text-gray-500">/{page.slug}</div>}
                </div>
              </TableCell>
              <TableCell>
                <Badge variant={
                  page.status === 'published' ? 'default' :
                  page.status === 'draft' ? 'secondary' : 'outline'
                }>
                  {page.status}
                </Badge>
              </TableCell>
              <TableCell>
                {page.is_featured && <Badge variant="default">⭐</Badge>}
              </TableCell>
              <TableCell>
                <Badge variant="outline">{page.content_type}</Badge>
              </TableCell>
              <TableCell>{page.created_by?.username}</TableCell>
              <TableCell>{page.updated_by?.username}</TableCell>
              <TableCell>
                {page.published_at ? new Date(page.published_at).toLocaleDateString() : '-'}
              </TableCell>
              <TableCell>{new Date(page.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <Button asChild variant="outline" size="sm" className="mr-2">
                  <Link href={`/posts/pages/${page.id}`}>View</Link>
                </Button>
                <Button variant="outline" size="sm" className="mr-2" onClick={() => { /* Edit handler */ }}>Edit</Button>
                <Button variant="destructive" size="sm" onClick={() => { /* Delete handler */ }}>Delete</Button>
              </TableCell>
            </TableRow>
          )) || <TableRow><TableCell colSpan={9}>No pages found</TableCell></TableRow>}
        </TableBody>
      </Table>
      </div>
    </StoreLayout>
  );
}
