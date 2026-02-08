'use client';

import React, { useState, useMemo } from 'react';
import { useCategories } from '@/hooks/posts';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Link from 'next/link';
import { Category } from '@/types/posts.types';
import StoreLayout from '@/components/layouts/store-layout';

export default function CategoriesPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const { data: categories, error, isLoading } = useCategories();

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [isActiveFilter, setIsActiveFilter] = useState('all');
  const [parentFilter, setParentFilter] = useState('all');

  // Memoized filtered categories
  const filteredCategories = useMemo(() => {
    return categories?.filter((category: Category) => {
      const matchesSearch = !searchTerm ||
        category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        category.slug?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        category.description?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesActive = isActiveFilter === 'all' ||
        (isActiveFilter === 'true' ? category.is_active : !category.is_active);

      const matchesParent = parentFilter === 'all' ||
        (parentFilter === 'none' ? !category.parent : category.parent?.id === parentFilter);

      return matchesSearch && matchesActive && matchesParent;
    });
  }, [categories, searchTerm, isActiveFilter, parentFilter]);

  // Build parent options for filter
  const parentOptions = useMemo(() => {
    const options = [{ id: 'none', name: 'No Parent' }];
    categories?.forEach((cat: Category) => {
      if (!options.find(opt => opt.id === cat.id)) {
        options.push({ id: cat.id, name: cat.name });
      }
    });
    return options;
  }, [categories]);

  if (isLoading) return <div>Loading categories...</div>;
  if (error) return <div>Error loading categories: {(error as Error).message}</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Categories</h1>
        <Button asChild>
          <Link href="/posts/categories/create">Create Category</Link>
        </Button>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <Input
          placeholder="Search categories..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <Select value={isActiveFilter} onValueChange={setIsActiveFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Active Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="true">Active</SelectItem>
            <SelectItem value="false">Inactive</SelectItem>
          </SelectContent>
        </Select>

        <Select value={parentFilter} onValueChange={setParentFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Parent" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Parents</SelectItem>
            {parentOptions.map(option => (
              <SelectItem key={option.id} value={option.id}>
                {option.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Parent</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Posts</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {filteredCategories?.map((category: Category) => (
            <TableRow key={category.id}>
              <TableCell className="font-medium">{category.name}</TableCell>
              <TableCell>{category.slug}</TableCell>
              <TableCell>{category.description || '-'}</TableCell>
              <TableCell>
                {category.parent ? (
                  <Badge variant="outline">{category.parent.name}</Badge>
                ) : (
                  <span className="text-gray-500">No parent</span>
                )}
              </TableCell>
              <TableCell>
                <Badge variant={category.is_active ? 'default' : 'secondary'}>
                  {category.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </TableCell>
              <TableCell>{category.post_count}</TableCell>
              <TableCell>{new Date(category.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <Button asChild variant="outline" size="sm" className="mr-2">
                  <Link href={`/posts/categories/${category.id}`}>View</Link>
                </Button>
                <Button variant="outline" size="sm" className="mr-2" onClick={() => { /* Edit handler */ }}>Edit</Button>
                <Button variant="destructive" size="sm" onClick={() => { /* Delete handler */ }}>Delete</Button>
              </TableCell>
            </TableRow>
          )) || <TableRow><TableCell colSpan={8}>No categories found</TableCell></TableRow>}
        </TableBody>
      </Table>
      </div>
    </StoreLayout>
  );
}
