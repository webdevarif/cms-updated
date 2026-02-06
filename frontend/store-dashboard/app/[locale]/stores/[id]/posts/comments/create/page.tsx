import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateComment } from '@/hooks/posts';
import { commentCreateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';

export default function CreateCommentPage() {
  const router = useRouter();
  const { createComment, isLoading } = useCreateComment();

  // Form state
  const [postId, setPostId] = useState('');
  const [parentId, setParentId] = useState('');
  const [content, setContent] = useState('');
  const [isApproved, setIsApproved] = useState(false);
  const [isPublic, setIsPublic] = useState(true);

  // Mock data - in a real app this would come from APIs
  const mockPosts = [
    { id: '1', title: 'First Blog Post' },
    { id: '2', title: 'About Us Page' },
    { id: '3', title: 'Product Announcement' },
  ];

  const mockComments = [
    { id: '1', content: 'Great article!' },
    { id: '2', content: 'I have a question...' },
    { id: '3', content: 'Thanks for sharing' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = commentCreateSchema.parse({
        post: postId,
        parent: parentId || undefined,
        content,
        is_approved: isApproved,
        is_public: isPublic,
      });
      await createComment(result);
      router.push('/posts/comments');
    } catch (error) {
      console.error('Error creating comment:', error);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Comment</h1>
      <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
        <div>
          <Label htmlFor="post">Post</Label>
          <Select value={postId} onValueChange={setPostId} required>
            <SelectTrigger>
              <SelectValue placeholder="Select post" />
            </SelectTrigger>
            <SelectContent>
              {mockPosts.map(post => (
                <SelectItem key={post.id} value={post.id}>
                  {post.title}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="parent">Parent Comment (optional)</Label>
          <Select value={parentId} onValueChange={setParentId}>
            <SelectTrigger>
              <SelectValue placeholder="Select parent comment (for replies)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">No parent (top-level comment)</SelectItem>
              {mockComments.map(comment => (
                <SelectItem key={comment.id} value={comment.id}>
                  {comment.content}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-sm text-gray-600 mt-1">Select a parent comment to create a reply</p>
        </div>

        <div>
          <Label htmlFor="content">Content</Label>
          <Textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={4}
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Checkbox
              id="isApproved"
              checked={isApproved}
              onCheckedChange={(checked) => setIsApproved(checked as boolean)}
            />
            <Label htmlFor="isApproved">Approved</Label>
          </div>
          <div className="flex items-center gap-2">
            <Checkbox
              id="isPublic"
              checked={isPublic}
              onCheckedChange={(checked) => setIsPublic(checked as boolean)}
            />
            <Label htmlFor="isPublic">Public</Label>
          </div>
        </div>

        <div className="bg-gray-100 p-3 rounded">
          <h3 className="font-semibold mb-2">Comment Guidelines:</h3>
          <ul className="text-sm space-y-1">
            <li>• Comments support 1-level nesting (parent → replies)</li>
            <li>• Approved comments are visible to all users</li>
            <li>• Private comments are only visible to moderators</li>
            <li>• Content should be respectful and constructive</li>
          </ul>
        </div>

        <div className="flex gap-2">
          <Button type="submit" disabled={isLoading}>
            {isLoading ? 'Creating...' : 'Create Comment'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
