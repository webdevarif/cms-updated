import React from 'react';
import { useStores, useDeleteStore } from '@/hooks/stores';
import { Table, TableHeader, TableBody, TableRow, TableCell, TableHead } from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function StoresListPage() {
  const { data: stores, error, isLoading, mutate } = useStores();
  const { deleteStore, isLoading: isDeleting } = useDeleteStore();

  if (isLoading) return <div>Loading stores...</div>;
  if (error) return <div>Error loading stores: {(error as Error).message}</div>;

  const handleDelete = (storeId: string) => {
    if (confirm('Are you sure you want to delete this store?')) {
      deleteStore(storeId).then(() => {
        mutate();
      }).catch((err: Error) => {
        console.error('Delete failed:', err);
      });
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Stores List</h1>
      <Button asChild className="mb-4">
        <Link href="/stores/create">Create New Store</Link>
      </Button>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Slug</TableHead>
            <TableHead>Status</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {stores?.map(store => (
            <TableRow key={store.id}>
              <TableCell>{store.name}</TableCell>
              <TableCell>{store.slug}</TableCell>
              <TableCell>{store.status}</TableCell>
              <TableCell>
                <Button asChild variant="outline" size="sm" className="mr-2">
                  <Link href={`/stores/${store.id}`}>View</Link>
                </Button>
                <Button variant="outline" size="sm" className="mr-2" onClick={() => { /* Edit handler not implemented */ }}>Edit</Button>
                <Button variant="destructive" size="sm" onClick={() => handleDelete(store.id)} disabled={isDeleting}>
                  Delete
                </Button>
              </TableCell>
            </TableRow>
          )) || <TableRow><TableCell colSpan={4}>No stores found</TableCell></TableRow>}
        </TableBody>
      </Table>
    </div>
  );
}
