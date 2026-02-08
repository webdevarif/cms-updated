'use client';

import React, { useState } from 'react';
import { useComments, useUpdateComment, useDeleteComment } from '@/hooks/posts';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Comment } from '@/types/posts.types';
import { PageHeader } from '@/components/ui/typography';
import { SkeletonCard } from '@/components/ui/skeleton';


import StoreLayout from '@/components/layouts/store-layout';
export default function CommentsPage({ params }: { params: Promise<{ id: string; locale: string }> }) {
  const { data: comments, error, isLoading, mutate } = useComments();
  const { updateComment, isLoading: isUpdating } = useUpdateComment();
  const { deleteComment, isLoading: isDeleting } = useDeleteComment();

  // Filter states
  const [searchTerm, setSearchTerm] = useState('');
  const [postFilter, setPostFilter] = useState('');
  const [userFilter, setUserFilter] = useState('');
  const [parentFilter, setParentFilter] = useState('');
  const [isApprovedFilter, setIsApprovedFilter] = useState('');
  const [isPublicFilter, setIsPublicFilter] = useState('');

  // Dialog states
  const [editingComment, setEditingComment] = useState<Comment | null>(null);
  const [editContent, setEditContent] = useState('');
  const [editApproved, setEditApproved] = useState(false);
  const [editPublic, setEditPublic] = useState(true);

  const handleEdit = async () => {
    if (!editingComment) return;

    try {
      await updateComment(editingComment.id, {
        content: editContent,
        is_approved: editApproved,
        is_public: editPublic,
      });
      setEditingComment(null);
      mutate();
    } catch (error) {
      console.error('Error updating comment:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm('Are you sure you want to delete this comment?')) {
      try {
        await deleteComment(id);
        mutate();
      } catch (error) {
        console.error('Error deleting comment:', error);
      }
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await updateComment(id, { is_approved: true });
      mutate();
    } catch (error) {
      console.error('Error approving comment:', error);
    }
  };

  const handleReject = async (id: string) => {
    try {
      await updateComment(id, { is_approved: false });
      mutate();
    } catch (error) {
      console.error('Error rejecting comment:', error);
    }
  };

  const openEditDialog = (comment: Comment) => {
    setEditingComment(comment);
    setEditContent(comment.content);
    setEditApproved(comment.is_approved);
    setEditPublic(comment.is_public);
  };

  if (isLoading) {
    return (
    <StoreLayout params={params}>
      <div className="p-4">
        <PageHeader title="Comments" />
        <div className="space-y-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  if (error) return <div>Error loading comments: {(error as Error).message}</div>;

  return (
    <StoreLayout params={params}>
      <div className="p-4">
      <PageHeader
        title="Comments"
        description="Manage and moderate user comments"
      />

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-4">
        <Input
          placeholder="Search comments..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />

        <Select value={postFilter} onValueChange={setPostFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Post" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Posts</SelectItem>
            {/* TODO: Load posts dynamically */}
          </SelectContent>
        </Select>

        <Select value={userFilter} onValueChange={setUserFilter}>
          <SelectTrigger>
            <SelectValue placeholder="User" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All Users</SelectItem>
            {/* TODO: Load users dynamically */}
          </SelectContent>
        </Select>

        <Select value={parentFilter} onValueChange={setParentFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Parent" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="none">Top Level</SelectItem>
            {/* TODO: Load comments dynamically for parent options */}
          </SelectContent>
        </Select>

        <Select value={isApprovedFilter} onValueChange={setIsApprovedFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Approved" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="true">Approved</SelectItem>
            <SelectItem value="false">Not Approved</SelectItem>
          </SelectContent>
        </Select>

        <Select value={isPublicFilter} onValueChange={setIsPublicFilter}>
          <SelectTrigger>
            <SelectValue placeholder="Public" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">All</SelectItem>
            <SelectItem value="true">Public</SelectItem>
            <SelectItem value="false">Private</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Content</TableHead>
            <TableHead>User</TableHead>
            <TableHead>Post</TableHead>
            <TableHead>Parent</TableHead>
            <TableHead>Approved</TableHead>
            <TableHead>Public</TableHead>
            <TableHead>Created</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {comments?.map((comment: Comment) => (
            <TableRow key={comment.id}>
              <TableCell>
                <div className="max-w-xs truncate">
                  {comment.content}
                </div>
              </TableCell>
              <TableCell>
                <div>
                  <div className="font-medium">{comment.user?.username || 'Anonymous'}</div>
                  <div className="text-sm text-gray-500">{comment.user?.email || 'No email'}</div>
                </div>
              </TableCell>
              <TableCell>
                <Badge variant="outline">Post {comment.post}</Badge>
              </TableCell>
              <TableCell>
                {comment.parent ? (
                  <Badge variant="outline">Reply to {comment.parent}</Badge>
                ) : (
                  <span className="text-gray-500">Top level</span>
                )}
              </TableCell>
              <TableCell>
                <Badge variant={comment.is_approved ? 'default' : 'secondary'}>
                  {comment.is_approved ? 'Approved' : 'Not Approved'}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={comment.is_public ? 'default' : 'secondary'}>
                  {comment.is_public ? 'Public' : 'Private'}
                </Badge>
              </TableCell>
              <TableCell>{new Date(comment.created_at).toLocaleDateString()}</TableCell>
              <TableCell>
                <div className="flex gap-1">
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button variant="outline" size="sm" onClick={() => openEditDialog(comment)}>
                        Edit
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-md">
                      <DialogHeader>
                        <DialogTitle>Edit Comment</DialogTitle>
                      </DialogHeader>
                      <div className="space-y-4">
                        <div>
                          <label className="text-sm font-medium">Content</label>
                          <Textarea
                            value={editContent}
                            onChange={(e) => setEditContent(e.target.value)}
                            rows={4}
                          />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="flex items-center gap-2">
                            <Checkbox
                              checked={editApproved}
                              onCheckedChange={(checked) => setEditApproved(checked as boolean)}
                            />
                            <label className="text-sm">Approved</label>
                          </div>
                          <div className="flex items-center gap-2">
                            <Checkbox
                              checked={editPublic}
                              onCheckedChange={(checked) => setEditPublic(checked as boolean)}
                            />
                            <label className="text-sm">Public</label>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button onClick={handleEdit} disabled={isUpdating}>
                            {isUpdating ? 'Updating...' : 'Update'}
                          </Button>
                          <Button variant="outline" onClick={() => setEditingComment(null)}>
                            Cancel
                          </Button>
                        </div>
                      </div>
                    </DialogContent>
                  </Dialog>

                  {!comment.is_approved && (
                    <Button size="sm" onClick={() => handleApprove(comment.id)} disabled={isUpdating}>
                      Approve
                    </Button>
                  )}
                  {comment.is_approved && (
                    <Button size="sm" variant="outline" onClick={() => handleReject(comment.id)} disabled={isUpdating}>
                      Reject
                    </Button>
                  )}
                  <Button variant="destructive" size="sm" onClick={() => handleDelete(comment.id)} disabled={isDeleting}>
                    Delete
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          )) || <TableRow><TableCell colSpan={8}>No comments found</TableCell></TableRow>}
        </TableBody>
      </Table>
      </div>
    </StoreLayout>
  );
}
