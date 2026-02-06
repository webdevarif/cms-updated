'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { StoreMembership } from '@/types/stores.types';
import { 
  useStoreMemberships
} from '@/hooks/stores';
import { storeActionHandlers } from '@/handles/stores.handles';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Field, FieldContent, FieldGroup } from '@/components/ui/field';
import { Heading, Paragraph, Text } from '@/components/ui/typography';
import { UserPlus, Trash2, Mail, User, Crown } from 'lucide-react';
import StoreLayout from '@/components/layouts/store-layout';

const StoreUsersPage = () => {
  const params = useParams();
  const storeId = params.id as string;

  const { data: memberships, mutate: mutateMemberships } = useStoreMemberships(storeId);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    email: '',
    role: 'member'
  });
  const [loadingStates, setLoadingStates] = useState({
    creatingMember: false
  });

  const handleCreateMember = async () => {
    setLoadingStates({ ...loadingStates, creatingMember: true });
    try {
      const membershipData: Omit<StoreMembership, 'id' | 'store' | 'joined_at'> = {
        user: { 
          id: '', 
          username: '', 
          email: createForm.email, 
          first_name: '', 
          last_name: '' 
        },
        role: createForm.role
      };

      await storeActionHandlers.createMembership(storeId, membershipData);
      setShowCreateForm(false);
      setCreateForm({ email: '', role: 'member' });
      mutateMemberships();
    } catch (error) {
      console.error('Create member error:', error);
      alert('Failed to add member');
    } finally {
      setLoadingStates({ ...loadingStates, creatingMember: false });
    }
  };

  const handleRemoveMember = async () => {
    if (!confirm('Are you sure you want to remove this member?')) return;

    try {
      // TODO: Implement member removal
      alert('Member removal not yet implemented');
    } catch (error) {
      console.error('Remove member error:', error);
      alert('Failed to remove member');
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner':
        return <Crown className="h-4 w-4 text-yellow-500" />;
      case 'admin':
        return <User className="h-4 w-4 text-blue-500" />;
      default:
        return <User className="h-4 w-4 text-gray-500" />;
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'owner':
        return 'bg-yellow-100 text-yellow-800';
      case 'admin':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <StoreLayout params={{ id: storeId }}>
      <div className="p-6 max-w-6xl mx-auto">
        <div className="mb-6">
          <Heading variant="h2" className="mb-2">Store Members</Heading>
        <Paragraph color="muted">
          Manage members and their roles for this store
        </Paragraph>
        </div>

        {/* Add Member Button */}
        <div className="mb-6">
          <Button onClick={() => setShowCreateForm(true)}>
            <UserPlus className="h-4 w-4 mr-2" />
            Add Member
          </Button>
        </div>

        {/* Create Member Form */}
        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6 border border-gray-200">
            <Heading variant="h3" className="mb-4">Add New Member</Heading>
            <FieldGroup className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Field>
                <Label>Email Address</Label>
                <FieldContent>
                  <Input
                    type="email"
                    value={createForm.email}
                    onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                    placeholder="user@example.com"
                    disabled={loadingStates.creatingMember}
                  />
                </FieldContent>
              </Field>

              <Field>
                <Label>Role</Label>
                <FieldContent>
                  <select
                    value={createForm.role}
                    onChange={(e) => setCreateForm({ ...createForm, role: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white text-gray-900 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    disabled={loadingStates.creatingMember}
                  >
                    <option value="member">Member</option>
                    <option value="admin">Admin</option>
                  </select>
                </FieldContent>
              </Field>
            </FieldGroup>

            <div className="flex gap-3 mt-6">
              <Button
                onClick={handleCreateMember}
                disabled={loadingStates.creatingMember}
              >
                {loadingStates.creatingMember ? 'Adding...' : 'Add Member'}
              </Button>
              <Button
                variant="outline"
                onClick={() => setShowCreateForm(false)}
                disabled={loadingStates.creatingMember}
              >
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Members List */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <Heading variant="h3">Current Members</Heading>
          </div>

          <div className="divide-y divide-gray-200">
            {memberships && memberships.length > 0 ? (
              memberships.map((membership) => (
                <div key={membership.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      {getRoleIcon(membership.role)}
                    </div>
                    <div>
                      <Text className="font-medium">
                        {membership.user.first_name} {membership.user.last_name}
                      </Text>
                      <div className="flex items-center space-x-2">
                        <Mail className="h-3 w-3 text-gray-400" />
                        <Text variant="p4" color="muted">{membership.user.email}</Text>
                      </div>
                      <Text variant="p4" color="muted">
                        Joined: {new Date(membership.joined_at).toLocaleDateString()}
                      </Text>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleColor(membership.role)}`}>
                      {membership.role}
                    </span>

                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRemoveMember}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center">
                <Text color="muted">No members found</Text>
              </div>
            )}
          </div>
        </div>
      </div>
    </StoreLayout>
  );
};

export default StoreUsersPage;
