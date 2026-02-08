'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { usePost, useUpdatePost, useDeletePost } from '@/hooks/posts';
import { postUpdateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Post } from '@/types/posts.types';


import StoreLayout from '@/components/layouts/store-layout';
export default function PostDetailPage({ params }: { params: Promise<{ id: string; locale: string; pid: string }> }) {
  return <PostDetailPageInner params={params} />;
}

function PostDetailPageInner({ params }: { params: Promise<{ id: string; locale: string; pid: string }> }) {
  const router = useRouter();
  const [resolvedParams, setResolvedParams] = useState<{ id: string; pid: string } | null>(null);

  const { data: post, error, isLoading } = usePost(resolvedParams?.pid || '');
  const { updatePost, isLoading: isUpdating } = useUpdatePost();
  const { deletePost, isLoading: isDeleting } = useDeletePost();

  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');
  const [slug, setSlug] = useState('');
  const [excerpt, setExcerpt] = useState('');
  const [content, setContent] = useState('');
  const [contentType, setContentType] = useState('html');
  const [status, setStatus] = useState('draft');
  const [isFeatured, setIsFeatured] = useState(false);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Resolve params
  useEffect(() => {
    params.then(p => setResolvedParams({ id: p.id, pid: p.pid }));
  }, [params]);

  if (!resolvedParams) return <div>Loading...</div>;

  const storeId = resolvedParams.id;
  const postId = resolvedParams.pid;

  // Initialize form when post data becomes available
  if (post && !title && !isEditing) {
    setTitle(post.title);
    setSlug(post.slug || '');
    setExcerpt(post.excerpt || '');
    setContent(post.content || '');
    setContentType(post.content_type);
    setStatus(post.status);
    setIsFeatured(post.is_featured);
    setSelectedCategories(post.categories.map(cat => cat.id));
    setSelectedTags(post.tags.map(tag => tag.id));
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = postUpdateSchema.parse({
        title,
        slug,
        excerpt,
        content,
        content_type: contentType,
        status,
        is_featured: isFeatured,
        categories: selectedCategories,
        tags: selectedTags,
      });
      // Pass the data directly - the API will handle the conversion
      await updatePost(postId, result as unknown as Partial<Post>);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating post:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this post?')) {
      try {
        await deletePost(postId);
        router.push(`/stores/${storeId}/posts`);
      } catch (error) {
        console.error('Error deleting post:', error);
      }
    }
  };

  const handleCancel = () => {
    if (post) {
      setTitle(post.title);
      setSlug(post.slug || '');
      setExcerpt(post.excerpt || '');
      setContent(post.content);
      setContentType(post.content_type);
      setStatus(post.status);
      setIsFeatured(post.is_featured);
      setSelectedCategories(post.categories.map(cat => cat.id));
      setSelectedTags(post.tags.map(tag => tag.id));
    }
    setIsEditing(false);
  };

  if (isLoading) return <div>Loading post...</div>;
  if (error) return <div>Error loading post: {(error as Error).message}</div>;
  if (!post) return <div>Post not found</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Post Details</h1>
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
            {post.title}
            <Badge variant={post.status === 'published' ? 'default' : 'secondary'}>
              {post.status}
            </Badge>
            {post.is_featured && <Badge variant="default">⭐ Featured</Badge>}
          </CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline">{post.post_type_name}</Badge>
            <Badge variant="outline">{post.content_type}</Badge>
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
                  <p>{post.post_type_name}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Created By</h3>
                  <p>{post.created_by.username}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Updated By</h3>
                  <p>{post.updated_by.username}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Published</h3>
                  <p>{post.published_at ? new Date(post.published_at).toLocaleDateString() : 'Not published'}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Created</h3>
                  <p>{new Date(post.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Last Updated</h3>
                  <p>{new Date(post.updated_at).toLocaleDateString()}</p>
                </div>
              </div>

              {post.slug && (
                <div>
                  <h3 className="font-semibold">Slug</h3>
                  <p>/{post.slug}</p>
                </div>
              )}

              {post.excerpt && (
                <div>
                  <h3 className="font-semibold">Excerpt</h3>
                  <p>{post.excerpt}</p>
                </div>
              )}

              <div>
                <h3 className="font-semibold">Content</h3>
                <div className="bg-gray-100 p-4 rounded">
                  <pre className="whitespace-pre-wrap">{post.content}</pre>
                </div>
              </div>

              {post.categories.length > 0 && (
                <div>
                  <h3 className="font-semibold">Categories</h3>
                  <div className="flex gap-2">
                    {post.categories.map(category => (
                      <Badge key={category.id} variant="outline">
                        {category.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {post.tags.length > 0 && (
                <div>
                  <h3 className="font-semibold">Tags</h3>
                  <div className="flex gap-2">
                    {post.tags.map(tag => (
                      <Badge key={tag.id} variant="outline">
                        {tag.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {post.template && (
                <div>
                  <h3 className="font-semibold">Template</h3>
                  <div className="bg-gray-100 p-2 rounded">
                    <p><strong>Name:</strong> {post.template.name}</p>
                    <p><strong>Key:</strong> {post.template.key}</p>
                    <p><strong>Role:</strong> {post.template.template_role}</p>
                    <p><strong>Type:</strong> {post.template.template_type}</p>
                    <p><strong>Theme ID:</strong> {post.template.theme_id}</p>
                  </div>
                </div>
              )}

              {post.meta && Object.keys(post.meta).length > 0 && (
                <div>
                  <h3 className="font-semibold">Metadata</h3>
                  <div className="bg-gray-100 p-2 rounded">
                    <pre className="text-sm">{JSON.stringify(post.meta, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
      </StoreLayout>
  );
}
