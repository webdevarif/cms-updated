'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { StoreRole } from '@/types/stores.types';
import { 
  useStoreRoles
} from '@/hooks/stores';
import { storeActionHandlers } from '@/handles/stores.handles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent, FieldGroup } from '@/components/ui/field';
import { Heading, Paragraph, Text } from '@/components/ui/typography';
import { Plus, Trash2, Edit3, Shield, Users } from 'lucide-react';
import StoreLayout from '@/components/layouts/store-layout';

const StoreRolesPage = () => {
  const params = useParams();
  const storeId = params.id as string;

  const { data: roles, mutate: mutateRoles } = useStoreRoles(storeId);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRole, setEditingRole] = useState<StoreRole | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    description: '',
    actions: [] as string[]
  });
  const [loadingStates, setLoadingStates] = useState({
    creatingRole: false,
    updatingRole: false
  });

  // Available permissions/actions
  const availableActions = [
    'manage_products',
    'view_orders',
    'manage_orders',
    'manage_settings',
    'manage_staff',
    'view_analytics',
    'manage_inventory'
  ];

  const handleCreateRole = async () => {
    setLoadingStates({ ...loadingStates, creatingRole: true });
    try {
      const roleData: Omit<StoreRole, 'id' | 'store' | 'created_at' | 'updated_at'> = {
        name: formData.name,
        slug: formData.slug,
        description: formData.description,
        actions: formData.actions
      };

      await storeActionHandlers.createRole(storeId, roleData);
      setShowCreateForm(false);
      setFormData({ name: '', slug: '', description: '', actions: [] });
      mutateRoles();
    } catch (error) {
      console.error('Create role error:', error);
      alert('Failed to create role');
    } finally {
      setLoadingStates({ ...loadingStates, creatingRole: false });
    }
  };

  const handleEditRole = (role: StoreRole) => {
    setEditingRole(role);
    setFormData({
      name: role.name,
      slug: role.slug,
      description: role.description || '',
      actions: role.actions || []
    });
  };

  const handleUpdateRole = async () => {
    if (!editingRole) return;

    setLoadingStates({ ...loadingStates, updatingRole: true });
    try {
      await storeActionHandlers.updateStore(editingRole.id, {
        name: formData.name,
        slug: formData.slug,
        description: formData.description
      });

      setEditingRole(null);
      setFormData({ name: '', slug: '', description: '', actions: [] });
      mutateRoles();
    } catch (error) {
      console.error('Update role error:', error);
      alert('Failed to update role');
    } finally {
      setLoadingStates({ ...loadingStates, updatingRole: false });
    }
  };

  const handleDeleteRole = async (roleId: string) => {
    if (!confirm('Are you sure you want to delete this role? This action cannot be undone.')) return;

    try {
      await storeActionHandlers.deleteStore(roleId);
      mutateRoles();
    } catch (error) {
      console.error('Delete role error:', error);
      alert('Failed to delete role');
    }
  };

  const toggleAction = (action: string) => {
    setFormData(prev => ({
      ...prev,
      actions: prev.actions.includes(action)
        ? prev.actions.filter(a => a !== action)
        : [...prev.actions, action]
    }));
  };

  const getActionLabel = (action: string) => {
    const labels: Record<string, string> = {
      'manage_products': 'Manage Products',
      'view_orders': 'View Orders',
      'manage_orders': 'Manage Orders',
      'manage_settings': 'Manage Settings',
      'manage_staff': 'Manage Staff',
      'view_analytics': 'View Analytics',
      'manage_inventory': 'Manage Inventory'
    };
    return labels[action] || action;
  };

  return (
    <StoreLayout params={{ id: storeId }}>
      <div className="p-6 max-w-6xl mx-auto">
        <div className="mb-6">
          <Heading variant="h2" className="mb-2">Store Roles</Heading>
        <Paragraph color="muted">
          Define roles and permissions for store members
        </Paragraph>
        </div>

      {/* Add Role Button */}
      <div className="mb-6">
        <Button onClick={() => setShowCreateForm(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Create Role
        </Button>
      </div>

      {/* Create/Edit Role Form */}
      {(showCreateForm || editingRole) && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-200">
          <Heading variant="h3" className="mb-4">
            {editingRole ? 'Edit Role' : 'Create New Role'}
          </Heading>

          <FieldGroup className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <Field>
              <Label>Role Name</Label>
              <FieldContent>
                <Input
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Store Manager"
                  disabled={loadingStates.creatingRole || loadingStates.updatingRole}
                />
              </FieldContent>
            </Field>

            <Field>
              <Label>Role Slug</Label>
              <FieldContent>
                <Input
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                  placeholder="e.g., store-manager"
                  disabled={loadingStates.creatingRole || loadingStates.updatingRole}
                />
              </FieldContent>
            </Field>

            <Field className="md:col-span-2">
              <Label>Description (Optional)</Label>
              <FieldContent>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe this role's responsibilities..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  disabled={loadingStates.creatingRole || loadingStates.updatingRole}
                />
              </FieldContent>
            </Field>
          </FieldGroup>

          {/* Permissions */}
          <div className="mb-6">
            <Heading variant="h4" className="mb-3">Permissions</Heading>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {availableActions.map((action) => (
                <label key={action} className="flex items-center space-x-3 p-3 border border-gray-200 rounded-md hover:bg-gray-50 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.actions.includes(action)}
                    onChange={() => toggleAction(action)}
                    disabled={loadingStates.creatingRole || loadingStates.updatingRole}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <div>
                    <Text className="font-medium">{getActionLabel(action)}</Text>
                    <Text variant="p4" color="muted">{action}</Text>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              onClick={editingRole ? handleUpdateRole : handleCreateRole}
              disabled={loadingStates.creatingRole || loadingStates.updatingRole}
            >
              {loadingStates.creatingRole || loadingStates.updatingRole
                ? (editingRole ? 'Updating...' : 'Creating...')
                : (editingRole ? 'Update Role' : 'Create Role')
              }
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setShowCreateForm(false);
                setEditingRole(null);
                setFormData({ name: '', slug: '', description: '', actions: [] });
              }}
              disabled={loadingStates.creatingRole || loadingStates.updatingRole}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Roles List */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <Heading variant="h3">Current Roles</Heading>
        </div>

        <div className="divide-y divide-gray-200">
          {roles && roles.length > 0 ? (
            roles.map((role) => (
              <div key={role.id} className="px-6 py-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 mt-1">
                      <Shield className="h-5 w-5 text-blue-500" />
                    </div>
                    <div className="flex-1">
                      <Heading variant="h4" className="mb-1">{role.name}</Heading>
                      <Text variant="p4" color="muted" className="mb-2">{role.slug}</Text>
                      {role.description && (
                        <Paragraph className="mb-3">{role.description}</Paragraph>
                      )}

                      {/* Permissions */}
                      <div className="flex items-center space-x-2 mb-2">
                        <Users className="h-4 w-4 text-gray-400" />
                        <Text variant="p4" color="muted">Permissions:</Text>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {role.actions && role.actions.length > 0 ? (
                          role.actions.map((action) => (
                            <span key={action} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                              {getActionLabel(action)}
                            </span>
                          ))
                        ) : (
                          <Text variant="p4" color="muted">No permissions assigned</Text>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEditRole(role)}
                    >
                      <Edit3 className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDeleteRole(role.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="px-6 py-8 text-center">
              <Text color="muted">No roles found</Text>
            </div>
          )}
        </div>
      </div>
    </div>
    </StoreLayout>
  );
};

export default StoreRolesPage;
