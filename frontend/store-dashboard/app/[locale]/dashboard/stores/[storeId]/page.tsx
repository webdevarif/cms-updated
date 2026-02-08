'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { StoreMembership, StoreRole, StoreAPIKey } from '@/types/stores.types';
import {
  useStore,
  useStoreMemberships,
  useStoreRoles,
  useStoreAPIKeys
} from '@/hooks/stores';
import { storeActionHandlers } from '@/handles/stores.handles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent } from '@/components/ui/field';
import { PageHeader, Heading, Paragraph, Text } from '@/components/ui/typography';
import DashLayout from '@/components/layouts/dash-layout';

const StoreDetailPage = () => {
  const params = useParams();
  const storeId = params.storeId as string;

  // Store data
  const { data: store, error: storeError, isLoading: storeLoading } = useStore(storeId);

  // Memberships
  const { data: memberships, mutate: mutateMemberships } = useStoreMemberships(storeId);

  // Roles
  const { data: roles, mutate: mutateRoles } = useStoreRoles(storeId);

  // API Keys
  const { data: apiKeys, mutate: mutateApiKeys } = useStoreAPIKeys(storeId);

  const [activeTab, setActiveTab] = useState<'overview' | 'memberships' | 'roles' | 'api-keys'>('overview');
  const [showCreateForms, setShowCreateForms] = useState({
    membership: false,
    role: false,
    apiKey: false,
  });
  const [loadingStates, setLoadingStates] = useState({
    creatingMembership: false,
    creatingRole: false,
    creatingApiKey: false,
    revokingKey: false,
  });

  if (storeLoading) return <div>Loading store...</div>;
  if (storeError) return <div>Error loading store: {storeError.message}</div>;
  if (!store) return <div>Store not found</div>;

  const handleCreateMembership = async (data: Omit<StoreMembership, 'id' | 'joined_at'>) => {
    setLoadingStates({ ...loadingStates, creatingMembership: true });
    try {
      await storeActionHandlers.createMembership(storeId, data);
      setShowCreateForms({ ...showCreateForms, membership: false });
      mutateMemberships();
    } catch (error) {
      console.error('Create membership error:', error);
      alert('Failed to create membership');
    } finally {
      setLoadingStates({ ...loadingStates, creatingMembership: false });
    }
  };

  const handleCreateRole = async (data: Omit<StoreRole, 'id' | 'created_at' | 'updated_at'>) => {
    setLoadingStates({ ...loadingStates, creatingRole: true });
    try {
      await storeActionHandlers.createRole(storeId, data);
      setShowCreateForms({ ...showCreateForms, role: false });
      mutateRoles();
    } catch (error) {
      console.error('Create role error:', error);
      alert('Failed to create role');
    } finally {
      setLoadingStates({ ...loadingStates, creatingRole: false });
    }
  };

  const handleCreateApiKey = async (data: Omit<StoreAPIKey, 'id' | 'created' | 'created_by'>) => {
    setLoadingStates({ ...loadingStates, creatingApiKey: true });
    try {
      await storeActionHandlers.createAPIKey(storeId, data);
      setShowCreateForms({ ...showCreateForms, apiKey: false });
      mutateApiKeys();
    } catch (error) {
      console.error('Create API key error:', error);
      alert('Failed to create API key');
    } finally {
      setLoadingStates({ ...loadingStates, creatingApiKey: false });
    }
  };

  const handleRevokeApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key?')) return;
    setLoadingStates({ ...loadingStates, revokingKey: true });
    try {
      await storeActionHandlers.revokeAPIKey(storeId, keyId);
      mutateApiKeys();
    } catch (error) {
      console.error('Revoke API key error:', error);
      alert('Failed to revoke API key');
    } finally {
      setLoadingStates({ ...loadingStates, revokingKey: false });
    }
  };

  return (
    <DashLayout>
      <div className="p-6 max-w-6xl mx-auto">
        <PageHeader
          title={store.name}
          description={`${store.slug} • ${store.status} • Access Code: ${store.access_code}`}
        />

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'memberships', label: 'Memberships' },
            { id: 'roles', label: 'Roles' },
            { id: 'api-keys', label: 'API Keys' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as 'overview' | 'memberships' | 'roles' | 'api-keys')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <Heading variant="h3" className="mb-4">Store Overview</Heading>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <Heading variant="h4" className="mb-2">Store Information</Heading>
              <Text variant="p3"><strong>Name:</strong> {store.name}</Text>
              <Text variant="p3"><strong>Slug:</strong> {store.slug}</Text>
              <Text variant="p3"><strong>Status:</strong> {store.status}</Text>
              <Text variant="p3"><strong>Access Code:</strong> {store.access_code}</Text>
              <Text variant="p3"><strong>Created:</strong> {new Date(store.created_at).toLocaleDateString()}</Text>
            </div>
            <div>
              <Heading variant="h4" className="mb-2">Owner Information</Heading>
              <Text variant="p3"><strong>Name:</strong> {store.owner.first_name} {store.owner.last_name}</Text>
              <Text variant="p3"><strong>Email:</strong> {store.owner.email}</Text>
              <Text variant="p3"><strong>Username:</strong> {store.owner.username}</Text>
            </div>
          </div>
          {store.description && (
            <div className="mt-6">
              <Heading variant="h4" className="mb-2">Description</Heading>
              <Paragraph variant="p2">{store.description}</Paragraph>
            </div>
          )}
        </div>
      )}

      {activeTab === 'memberships' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <Heading variant="h3">Store Memberships</Heading>
              <Button onClick={() => setShowCreateForms({ ...showCreateForms, membership: true })}>
                Add Membership
              </Button>
            </div>

            {showCreateForms.membership && (
              <div className="border rounded-lg p-4 mb-4">
                <Heading variant="h4" className="mb-4">Create New Membership</Heading>
                <MembershipCreateForm
                  onSubmit={handleCreateMembership}
                  onCancel={() => setShowCreateForms({ ...showCreateForms, membership: false })}
                  isLoading={loadingStates.creatingMembership}
                />
              </div>
            )}

            <div className="space-y-4">
              {memberships?.map((membership) => (
                <div key={membership.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <Heading variant="h4">{membership.user.first_name} {membership.user.last_name}</Heading>
                      <Text variant="p4" color="muted">{membership.user.email}</Text>
                      <Text variant="p4" color="muted">Role: {membership.role}</Text>
                      <Text variant="p4" color="muted">Joined: {new Date(membership.joined_at).toLocaleDateString()}</Text>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="destructive" size="sm">
                        Remove
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'roles' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <Heading variant="h3">Store Roles</Heading>
              <Button onClick={() => setShowCreateForms({ ...showCreateForms, role: true })}>
                Create Role
              </Button>
            </div>

            {showCreateForms.role && (
              <div className="border rounded-lg p-4 mb-4">
                <Heading variant="h4" className="mb-4">Create New Role</Heading>
                <RoleCreateForm
                  onSubmit={handleCreateRole}
                  onCancel={() => setShowCreateForms({ ...showCreateForms, role: false })}
                  isLoading={loadingStates.creatingRole}
                />
              </div>
            )}

            <div className="space-y-4">
              {roles?.map((role) => (
                <div key={role.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <Heading variant="h4">{role.name}</Heading>
                      <Text variant="p4" color="muted">{role.slug}</Text>
                      {role.description && <Text variant="p3" color="muted">{role.description}</Text>}
                      <div className="mt-2">
                        <Text variant="p4" className="font-medium">Permissions:</Text>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {role.actions.map((action) => (
                            <span key={action} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                              {action}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">
                        Edit
                      </Button>
                      <Button variant="destructive" size="sm">
                        Delete
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'api-keys' && (
        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-center mb-4">
              <Heading variant="h3">API Keys</Heading>
              <Button onClick={() => setShowCreateForms({ ...showCreateForms, apiKey: true })}>
                Create API Key
              </Button>
            </div>

            {showCreateForms.apiKey && (
              <div className="border rounded-lg p-4 mb-4">
                <Heading variant="h4" className="mb-4">Create New API Key</Heading>
                <ApiKeyCreateForm
                  onSubmit={handleCreateApiKey}
                  onCancel={() => setShowCreateForms({ ...showCreateForms, apiKey: false })}
                  isLoading={loadingStates.creatingApiKey}
                />
              </div>
            )}

            <div className="space-y-4">
              {apiKeys?.map((apiKey) => (
                <div key={apiKey.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <Heading variant="h4">{apiKey.name}</Heading>
                      <Text variant="p4" color="muted">Created: {new Date(apiKey.created).toLocaleDateString()}</Text>
                      {apiKey.last_used_at && (
                        <Text variant="p4" color="muted">Last used: {new Date(apiKey.last_used_at).toLocaleDateString()}</Text>
                      )}
                      <div className="mt-2">
                        <Text variant="p4" className="font-medium">Actions:</Text>
                        <div className="flex flex-wrap gap-1 mt-1">
                          {apiKey.actions.map((action) => (
                            <span key={action} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                              {action}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleRevokeApiKey(apiKey.id)}
                        disabled={loadingStates.revokingKey}
                      >
                        {loadingStates.revokingKey ? 'Revoking...' : 'Revoke'}
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
    </DashLayout>
  );
};

// Helper Components
interface MembershipCreateFormProps {
  onSubmit: (data: Omit<StoreMembership, 'id' | 'joined_at'>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

interface RoleCreateFormProps {
  onSubmit: (data: Omit<StoreRole, 'id' | 'created_at' | 'updated_at'>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

interface ApiKeyCreateFormProps {
  onSubmit: (data: Omit<StoreAPIKey, 'id' | 'created' | 'created_by'>) => void;
  onCancel: () => void;
  isLoading: boolean;
}

const MembershipCreateForm = ({ onSubmit, onCancel, isLoading }: MembershipCreateFormProps) => {
  const [formData, setFormData] = useState({
    user: { id: '', username: '', email: '', first_name: '', last_name: '' },
    role: '',
    store: { id: '', name: '', slug: '', status: 'pending' as const, access_code: '', created_at: '', updated_at: '', owner: { id: '', username: '', email: '', first_name: '', last_name: '' } },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field>
        <Label>User Email</Label>
        <FieldContent>
          <Input
            value={formData.user.email}
            onChange={(e) => setFormData({ ...formData, user: { ...formData.user, email: e.target.value } })}
            placeholder="user@example.com"
            required
          />
        </FieldContent>
      </Field>
      <Field>
        <Label>Role</Label>
        <FieldContent>
          <Input
            value={formData.role}
            onChange={(e) => setFormData({ ...formData, role: e.target.value })}
            placeholder="member, admin, etc."
            required
          />
        </FieldContent>
      </Field>
      <div className="flex gap-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
};

const RoleCreateForm = ({ onSubmit, onCancel, isLoading }: RoleCreateFormProps) => {
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    actions: [] as string[],
    store: { id: '', name: '', slug: '', status: 'pending' as const, access_code: '', created_at: '', updated_at: '', owner: { id: '', username: '', email: '', first_name: '', last_name: '' } },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field>
        <Label>Role Name</Label>
        <FieldContent>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Admin, Member, etc."
            required
          />
        </FieldContent>
      </Field>
      <Field>
        <Label>Slug</Label>
        <FieldContent>
          <Input
            value={formData.slug}
            onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
            placeholder="admin, member, etc."
            required
          />
        </FieldContent>
      </Field>
      <Field>
        <Label>Description</Label>
        <FieldContent>
          <Input
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Role description"
          />
        </FieldContent>
      </Field>
      <Field>
        <Label>Actions (comma-separated)</Label>
        <FieldContent>
          <Input
            value={formData.actions.join(', ')}
            onChange={(e) => setFormData({ ...formData, actions: e.target.value.split(',').map(a => a.trim()).filter(Boolean) })}
            placeholder="read, write, delete"
          />
        </FieldContent>
      </Field>
      <div className="flex gap-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
};

const ApiKeyCreateForm = ({ onSubmit, onCancel, isLoading }: ApiKeyCreateFormProps) => {
  const [formData, setFormData] = useState({
    name: '',
    actions: [] as string[],
    store: { id: '', name: '', slug: '', status: 'pending' as const, access_code: '', created_at: '', updated_at: '', owner: { id: '', username: '', email: '', first_name: '', last_name: '' } },
    revoked: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Field>
        <Label>API Key Name</Label>
        <FieldContent>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Production API Key"
            required
          />
        </FieldContent>
      </Field>
      <Field>
        <Label>Actions (comma-separated)</Label>
        <FieldContent>
          <Input
            value={formData.actions.join(', ')}
            onChange={(e) => setFormData({ ...formData, actions: e.target.value.split(',').map(a => a.trim()).filter(Boolean) })}
            placeholder="read, write, delete"
          />
        </FieldContent>
      </Field>
      <div className="flex gap-2">
        <Button type="submit" disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create'}
        </Button>
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>
    </form>
  );
};

export default StoreDetailPage;
