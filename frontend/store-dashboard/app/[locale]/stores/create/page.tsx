import React from 'react';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateStore } from '@/hooks/stores';
import { storeCreateSchema, StoreCreateFormData } from '@/schemas/stores.schemas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/toast/use-toast';

export default function CreateStorePage() {
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState('pending');
  const { createStore, isLoading } = useCreateStore();
  const router = useRouter();
  const { toast } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = storeCreateSchema.parse({ name, slug, description, status });
      await createStore(result as StoreCreateFormData);
      toast({ title: 'Store created successfully', description: 'Redirecting to store list.' });
      router.push('/stores'); // Adjust for locale if needed
    } catch (err) {
      const error = err as Error;
      toast({ title: 'Error creating store', description: error.message, variant: 'destructive' });
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Create New Store</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <Label htmlFor="name">Name</Label>
          <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
        </div>
        <div>
          <Label htmlFor="slug">Slug</Label>
          <Input id="slug" value={slug} onChange={(e) => setSlug(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
        <div>
          <Label htmlFor="status">Status</Label>
          <select id="status" value={status} onChange={(e) => setStatus(e.target.value)} className="w-full p-2 border rounded">
            <option value="pending">Pending</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </div>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Store'}
        </Button>
      </form>
    </div>
  );
}
