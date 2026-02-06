'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { usePage, useUpdatePage, useDeletePage } from '@/hooks/posts';
import { pageCreateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Post } from '@/types/posts.types';

export default function PageDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const { data: page, error, isLoading } = usePage(id);
  const { updatePage, isLoading: isUpdating } = useUpdatePage();
  const { deletePage, isLoading: isDeleting } = useDeletePage();
  
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('html');
  const [status, setStatus] = useState('draft');
  const [isFeatured, setIsFeatured] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

  // Initialize form when data loads
  React.useEffect(() => {
    if (page) {
      setTitle(page.title);
      setSlug(page.slug || '');
      setExcerpt(page.excerpt || '');
      setContent(page.content);
      setContentType(page.content_type);
      setStatus(page.status);
      setIsFeatured(page.is_featured);
      setSelectedCategories(page.categories.map(cat => cat.id));
    }
  }, [page]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = pageCreateSchema.parse({
        title,
        slug,
        excerpt,
        content,
        content_type: contentType,
        status,
        is_featured: isFeatured,
        categories: selectedCategories,
      });
      await updatePage(id, result as unknown as Partial<Post>);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating page:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this page?')) {
      try {
        await deletePage(id);
        router.push('/posts/pages');
      } catch (error) {
        console.error('Error deleting page:', error);
      }
    }
  };

  const handleCancel = () => {
    if (page) {
      setTitle(page.title);
      setSlug(page.slug || '');
      setExcerpt(page.excerpt || '');
      setContent(page.content);
      setContentType(page.content_type);
      setStatus(page.status);
      setIsFeatured(page.is_featured);
      setSelectedCategories(page.categories.map(cat => cat.id));
    }
    setIsEditing(false);
  };

  if (isLoading) return <div>Loading page...</div>;
  if (error) return <div>Error loading page: {(error as Error).message}</div>;
  if (!page) return <div>Page not found</div>;

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Page Details</h1>
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
            {page.title}
            <Badge variant={page.status === 'published' ? 'default' : 'secondary'}>
              {page.status}
            </Badge>
            {page.is_featured && <Badge variant="default">⭐ Featured</Badge>}
          </CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline">Page</Badge>
            <Badge variant="outline">{page.content_type}</Badge>
          </div>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="status">Status</Label>
                  <Select value={status} onValueChange={setStatus}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="published">Published</SelectItem>
                      <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label htmlFor="contentType">Content Type</Label>
                  <Select value={contentType} onValueChange={setContentType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select content type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="html">HTML</SelectItem>
                      <SelectItem value="markdown">Markdown</SelectItem>
                      <SelectItem value="json">JSON</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
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
                <Label htmlFor="excerpt">Excerpt</Label>
                <Textarea
                  id="excerpt"
                  value={excerpt}
                  onChange={(e) => setExcerpt(e.target.value)}
                />
              </div>

              <div>
                <Label htmlFor="content">Content</Label>
                <Textarea
                  id="content"
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  rows={10}
                  required
                />
              </div>

              <div className="flex items-center gap-2">
                <Checkbox
                  id="isFeatured"
                  checked={isFeatured}
                  onCheckedChange={(checked) => setIsFeatured(checked as boolean)}
                />
                <Label htmlFor="isFeatured">Featured</Label>
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
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold">Post Type</h3>
                  <p>{page.post_type_name}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Created By</h3>
                  <p>{page.created_by.username}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Updated By</h3>
                  <p>{page.updated_by.username}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Published</h3>
                  <p>{page.published_at ? new Date(page.published_at).toLocaleDateString() : 'Not published'}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Created</h3>
                  <p>{new Date(page.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Last Updated</h3>
                  <p>{new Date(page.updated_at).toLocaleDateString()}</p>
                </div>
              </div>

              {page.slug && (
                <div>
                  <h3 className="font-semibold">Slug</h3>
                  <p>/{page.slug}</p>
                </div>
              )}

              {page.excerpt && (
                <div>
                  <h3 className="font-semibold">Excerpt</h3>
                  <p>{page.excerpt}</p>
                </div>
              )}

              <div>
                <h3 className="font-semibold">Content</h3>
                <div className="bg-gray-100 p-4 rounded">
                  <pre className="whitespace-pre-wrap">{page.content}</pre>
                </div>
              </div>

              {page.categories.length > 0 && (
                <div>
                  <h3 className="font-semibold">Categories</h3>
                  <div className="flex gap-2">
                    {page.categories.map(category => (
                      <Badge key={category.id} variant="outline">
                        {category.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {page.template && (
                <div>
                  <h3 className="font-semibold">Template</h3>
                  <div className="bg-gray-100 p-2 rounded">
                    <p><strong>Name:</strong> {page.template.name}</p>
                    <p><strong>Key:</strong> {page.template.key}</p>
                    <p><strong>Role:</strong> {page.template.template_role}</p>
                    <p><strong>Type:</strong> {page.template.template_type}</p>
                    <p><strong>Theme ID:</strong> {page.template.theme_id}</p>
                  </div>
                </div>
              )}

              {page.meta && Object.keys(page.meta).length > 0 && (
                <div>
                  <h3 className="font-semibold">Metadata</h3>
                  <div className="bg-gray-100 p-2 rounded">
                    <pre className="text-sm">{JSON.stringify(page.meta, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
