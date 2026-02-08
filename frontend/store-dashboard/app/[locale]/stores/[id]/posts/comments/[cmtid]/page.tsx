'use client';

import React, { useState, use } from 'react';
import { useRouter } from 'next/navigation';
import { useComment, useUpdateComment, useDeleteComment } from '@/hooks/posts';
import { commentUpdateSchema } from '@/schemas/posts.schemas';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Comment } from '@/types/posts.types';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';


import StoreLayout from '@/components/layouts/store-layout';
export default function CommentDetailPage({ params }: { params: Promise<{ id: string; locale: string; cmtid: string }> }) {
  const router = useRouter();
  const resolvedParams = React.use(params);
  const id = resolvedParams.cmtid;
  const { data: comment, error, isLoading } = useComment(commentId);
  const { updateComment, isLoading: isUpdating } = useUpdateComment();
  const { deleteComment, isLoading: isDeleting } = useDeleteComment();

  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState('');
  const [isApproved, setIsApproved] = useState(false);
  const [isPublic, setIsPublic] = useState(true);

  // Initialize form when data loads
  React.useEffect(() => {
    if (comment) {
      setContent(comment.content);
      setIsApproved(comment.is_approved);
      setIsPublic(comment.is_public);
    }
  }, [comment]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = commentUpdateSchema.parse({
        content,
        is_approved: isApproved,
        is_public: isPublic,
      });
      await updateComment(id, result as unknown as Partial<Comment>);
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating comment:', error);
    }
  };

  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this comment?')) {
      try {
        await deleteComment(id);
        router.push(`/stores/${storeId}/posts/comments`);
      } catch (error) {
        console.error('Error deleting comment:', error);
      }
    }
  };

  const handleCancel = () => {
    if (comment) {
      setContent(comment.content);
      setIsApproved(comment.is_approved);
      setIsPublic(comment.is_public);
    }
    setIsEditing(false);
  };

  const handleApprove = async () => {
    try {
      await updateComment(id, { is_approved: true });
    } catch (error) {
      console.error('Error approving comment:', error);
    }
  };

  const handleReject = async () => {
    try {
      await updateComment(id, { is_approved: false });
    } catch (error) {
      console.error('Error rejecting comment:', error);
    }
  };

  if (isLoading) return <div>Loading comment...</div>;
  if (error) return <div>Error loading comment: {(error as Error).message}</div>;
  if (!comment) return <div>Comment not found</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Comment Details</h1>
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
          <CardTitle>Comment Moderation</CardTitle>
        </CardHeader>
        <CardContent>
          {isEditing ? (
            <form onSubmit={handleUpdate} className="space-y-4">
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
                  <h3 className="font-semibold">User</h3>
                  <p>{comment.user?.username || 'Anonymous'}</p>
                  <p className="text-sm text-gray-500">{comment.user?.email || 'No email'}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Post</h3>
                  <Badge variant="outline">Post {comment.post}</Badge>
                </div>
                <div>
                  <h3 className="font-semibold">Parent</h3>
                  {comment.parent ? (
                    <Badge variant="outline">Reply to {comment.parent}</Badge>
                  ) : (
                    <span className="text-gray-500">Top level comment</span>
                  )}
                </div>
                <div>
                  <h3 className="font-semibold">Status</h3>
                  <div className="flex gap-2">
                    <Badge variant={comment.is_approved ? 'default' : 'secondary'}>
                      {comment.is_approved ? 'Approved' : 'Not Approved'}
                    </Badge>
                    <Badge variant={comment.is_public ? 'default' : 'secondary'}>
                      {comment.is_public ? 'Public' : 'Private'}
                    </Badge>
                  </div>
                </div>
                <div>
                  <h3 className="font-semibold">Created</h3>
                  <p>{new Date(comment.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <h3 className="font-semibold">Last Updated</h3>
                  <p>{new Date(comment.updated_at).toLocaleDateString()}</p>
                </div>
              </div>

              <div>
                <h3 className="font-semibold">Content</h3>
                <div className="bg-gray-100 p-4 rounded">
                  <p className="whitespace-pre-wrap">{comment.content}</p>
                </div>
              </div>

              <div className="flex gap-2">
                {!comment.is_approved && (
                  <Button onClick={handleApprove} disabled={isUpdating}>
                    Approve
                  </Button>
                )}
                {comment.is_approved && (
                  <Button variant="outline" onClick={handleReject} disabled={isUpdating}>
                    Reject
                  </Button>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
      </StoreLayout>
  );
}
