'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { Store } from '@/types/stores.types';
import { useStores, useCreateStore, useUpdateStore, useDeleteStore } from '@/hooks/stores';
import { storeActionHandlers } from '@/handles/stores.handles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent, FieldGroup } from '@/components/ui/field';
import { PageHeader, Heading, Paragraph } from '@/components/ui/typography';
import { LogIn } from 'lucide-react';
import DashLayout from '@/components/layouts/dash-layout';

const StoresPage = () => {
  const t = useTranslations();
  const st = useTranslations('stores');
  const router = useRouter();
  const { data: stores, error: storesError, isLoading: storesLoading, mutate } = useStores();
  const { createStore, isLoading: createLoading } = useCreateStore();
  const { updateStore, isLoading: updateLoading } = useUpdateStore();
  const { deleteStore, isLoading: deleteLoading } = useDeleteStore();

  // Debug: Log the stores data to see what we're getting
  console.log('Stores data:', stores, typeof stores, Array.isArray(stores));

  // Ensure stores is always an array
  const storesArray = Array.isArray(stores) ? stores : [];

  const [editingId, setEditingId] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState<Partial<Store>>(storeActionHandlers.initializeCreateForm());
  const [editForm, setEditForm] = useState<Partial<Store>>({});

  const handleCreate = async () => {
    try {
      const errors = storeActionHandlers.validateStoreForm(createForm);
      if (errors.length > 0) {
        alert(errors.join('\n'));
        return;
      }

      const storeData = storeActionHandlers.prepareStoreData(createForm);
      await createStore(storeData);
      setCreateForm(storeActionHandlers.resetCreateForm());
      mutate();
    } catch (error) {
      console.error('Create store error:', error);
      alert('Failed to create store');
    }
  };

  const handleEdit = (store: Store) => {
    setEditingId(store.id);
    setEditForm(store);
  };

  const handleUpdate = async () => {
    if (!editingId) return;
    try {
      const errors = storeActionHandlers.validateStoreForm(editForm);
      if (errors.length > 0) {
        alert(errors.join('\n'));
        return;
      }

      await updateStore(editingId, editForm as Partial<Store>);
      setEditingId(null);
      setEditForm({});
      mutate();
    } catch (error) {
      console.error('Update store error:', error);
      alert('Failed to update store');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(st('confirmDelete'))) return;
    try {
      await deleteStore(id);
      mutate();
    } catch (error) {
      console.error('Delete store error:', error);
      alert(st('errors.deleteFailed'));
    }
  };

  if (storesLoading) return <div>{t('common.loading')}</div>;
  if (storesError) {
    console.error('Stores error:', storesError);
    return <div>{t('common.error')}: {storesError.message || 'Failed to load stores'}</div>;
  }

  return (
    <DashLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <PageHeader
          title={st('title')}
          description={st('subtitle')}
          actions={
            <Button onClick={() => setShowCreateForm(!showCreateForm)}>
              {st('createStore')}
            </Button>
          }
        />

      {showCreateForm && (
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <Heading variant="h3" className="mb-4">{st('createStore')}</Heading>
          <FieldGroup className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Field>
              <Label htmlFor="name">{st('storeName')}</Label>
              <FieldContent>
                <Input
                  id="name"
                  value={createForm.name || ''}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder={st('storeName')}
                />
              </FieldContent>
            </Field>
            <Field>
              <Label htmlFor="slug">{st('storeSlug')}</Label>
              <FieldContent>
                <Input
                  id="slug"
                  value={createForm.slug || ''}
                  onChange={(e) => setCreateForm({ ...createForm, slug: e.target.value })}
                  placeholder="store-slug"
                />
              </FieldContent>
            </Field>
            <Field>
              <Label htmlFor="status">{st('storeStatus')}</Label>
              <FieldContent>
                <Input
                  id="status"
                  value={createForm.status || 'pending'}
                  onChange={(e) => setCreateForm({ ...createForm, status: e.target.value as 'active' | 'inactive' | 'pending' })}
                  placeholder="pending"
                />
              </FieldContent>
            </Field>
            <Field>
              <Label htmlFor="description">{st('storeDescription')}</Label>
              <FieldContent>
                <Input
                  id="description"
                  value={createForm.description || ''}
                  onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                  placeholder={st('storeDescription')}
                />
              </FieldContent>
            </Field>
          </FieldGroup>
          <Button onClick={handleCreate} disabled={createLoading} className="mt-4">
            {createLoading ? t('common.loading') : st('createStore')}
          </Button>
        </div>
      )}

      {/* Stores List */}
      <div className="bg-white rounded-lg shadow-md">
        <Heading variant="h3" className="p-6 pb-0">{t('dashboard.stores')}</Heading>
        <div className="p-6">
          {storesArray.length === 0 ? (
            <Paragraph variant="p2">{st('noStores')}</Paragraph>
          ) : (
            <div className="space-y-4">
              {storesArray.map((store: Store) => (
                <div key={store.id} className="border rounded-lg p-4">
                  {editingId === store.id ? (
                    <div className="space-y-4">
                      <FieldGroup className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <Field>
                          <Label>{st('storeName')}</Label>
                          <FieldContent>
                            <Input
                              value={editForm.name || ''}
                              onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                            />
                          </FieldContent>
                        </Field>
                        <Field>
                          <Label>{st('storeSlug')}</Label>
                          <FieldContent>
                            <Input
                              value={editForm.slug || ''}
                              onChange={(e) => setEditForm({ ...editForm, slug: e.target.value })}
                            />
                          </FieldContent>
                        </Field>
                        <Field>
                          <Label>{st('storeStatus')}</Label>
                          <FieldContent>
                            <Input
                              value={editForm.status || ''}
                              onChange={(e) => setEditForm({ ...editForm, status: e.target.value as 'active' | 'inactive' | 'pending' })}
                            />
                          </FieldContent>
                        </Field>
                        <Field>
                          <Label>{st('storeDescription')}</Label>
                          <FieldContent>
                            <Input
                              value={editForm.description || ''}
                              onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                            />
                          </FieldContent>
                        </Field>
                      </FieldGroup>
                      <div className="flex gap-2">
                        <Button onClick={handleUpdate} disabled={updateLoading}>
                          {updateLoading ? t('common.loading') : t('common.save')}
                        </Button>
                        <Button variant="outline" onClick={() => setEditingId(null)}>
                          {t('common.cancel')}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <Heading variant="h4">{store.name}</Heading>
                          <Paragraph variant="p3" className="text-muted-foreground">{store.slug}</Paragraph>
                          <Paragraph variant="p4" className="text-muted-foreground">
                            {t('common.status')}: {st(`status.${store.status}`)} | {st('accessCode')}: {store.access_code}
                          </Paragraph>
                          <Paragraph variant="p4" className="text-muted-foreground">
                            {t('common.created')}: {new Date(store.created_at).toLocaleDateString()}
                          </Paragraph>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            variant="default"
                            onClick={() => router.push(`/stores/${store.id}`)}
                          >
                            <LogIn className="h-4 w-4 mr-2" />
                            {st('login')}
                          </Button>
                          <Button variant="outline" onClick={() => handleEdit(store)}>
                            {t('common.edit')}
                          </Button>
                          <Button variant="destructive" onClick={() => handleDelete(store.id)} disabled={deleteLoading}>
                            {deleteLoading ? t('common.loading') : t('common.delete')}
                          </Button>
                        </div>
                      </div>
                      {store.description && (
                        <Paragraph variant="p2">{store.description}</Paragraph>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      </div>
    </DashLayout>
  );
};

export default StoresPage;
