# Stores API Documentation

## Overview
The stores app manages store-related operations including store CRUD, role management, user assignments, and API key management.

## Store Management

### Store CRUD Operations

#### List Stores
```http
GET /stores/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "My Store",
    "slug": "my-store",
    "description": "A sample store",
    "owner": {
      "id": 1,
      "email": "owner@example.com",
      "display_name": "Store Owner"
    },
    "status": "active",
    "access_code": "ABC123",
    "memberships_count": 3,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Store
```http
POST /stores/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Store",
  "slug": "new-store",
  "description": "A new online store",
  "status": "pending"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New Store",
  "slug": "new-store",
  "description": "A new online store",
  "owner": {
    "id": 1,
    "email": "owner@example.com",
    "display_name": "Store Owner"
  },
  "status": "pending",
  "access_code": "XYZ789",
  "memberships_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get Store
```http
GET /stores/{id}/
Authorization: Bearer {access_token}
```

#### Update Store
```http
PATCH /stores/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Store Name",
  "description": "Updated description"
}
```

#### Delete Store
```http
DELETE /stores/{id}/
Authorization: Bearer {access_token}
```

### Store Members Management

#### Get Store Members
```http
GET /stores/{id}/members/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "email": "member@example.com",
      "display_name": "Store Member"
    },
    "store": 1,
    "role": "admin",
    "joined_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

#### Add Store Member
```http
POST /stores/{id}/members/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_id": 2,
  "role": "admin"
}
```

### Store Memberships

#### List User Memberships
```http
GET /stores/memberships/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 1,
      "email": "user@example.com",
      "display_name": "John Doe"
    },
    "store": {
      "id": 1,
      "name": "My Store",
      "slug": "my-store"
    },
    "role": "owner",
    "joined_at": "2024-01-01T00:00:00Z",
    "is_active": true
  }
]
```

#### Create Membership
```http
POST /stores/memberships/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user": 2,
  "store": 1,
  "role": "member"
}
```

#### Update Membership
```http
PATCH /stores/memberships/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "role": "admin"
}
```

#### Delete Membership
```http
DELETE /stores/memberships/{id}/
Authorization: Bearer {access_token}
```

## Role Management

### Store Roles

#### List Store Roles
```http
GET /stores/{store_id}/roles/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Store Admin",
    "slug": "store-admin",
    "description": "Full store access",
    "permissions": [
      "manage_products",
      "manage_orders",
      "manage_settings",
      "manage_staff"
    ],
    "store": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Store Role
```http
POST /stores/{store_id}/roles/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Custom Role",
  "description": "Custom store role",
  "permissions": [
    "manage_products",
    "view_orders"
  ]
}
```

#### Get Role
```http
GET /stores/{store_id}/roles/{role_id}/
Authorization: Bearer {access_token}
```

#### Update Role
```http
PATCH /stores/{store_id}/roles/{role_id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Role",
  "actions": [
    "manage_products",
    "manage_orders",
    "manage_settings"
  ]
}
```

#### Delete Role
```http
DELETE /stores/{store_id}/roles/{role_id}/
Authorization: Bearer {access_token}
```

#### Get Role Users
```http
GET /stores/{store_id}/roles/{role_id}/users/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "email": "member@example.com",
      "display_name": "Store Member"
    },
    "role": {
      "id": 1,
      "name": "Store Admin"
    },
    "assigned_by": {
      "id": 1,
      "email": "owner@example.com"
    },
    "assigned_at": "2024-01-01T00:00:00Z"
  }
]
```

### User Role Assignments

#### List User Roles
```http
GET /stores/{store_id}/user-roles/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "email": "member@example.com",
      "display_name": "Store Member"
    },
    "role": {
      "id": 1,
      "name": "Store Admin"
    },
    "assigned_by": {
      "id": 1,
      "email": "owner@example.com"
    },
    "assigned_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Assign User Role
```http
POST /stores/{store_id}/user-roles/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user": 2,
  "role": 1
}
```

#### Update User Role
```http
PATCH /stores/{store_id}/user-roles/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "role": 2
}
```

#### Delete User Role
```http
DELETE /stores/{store_id}/user-roles/{id}/
Authorization: Bearer {access_token}
```

## API Key Management

### Store API Keys

#### List API Keys
```http
GET /stores/{store_id}/api-keys/
Authorization: Bearer {access_token}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Integration Key",
    "prefix": "sk_test_",
    "permissions": [
      "manage_products",
      "view_orders"
    ],
    "is_active": true,
    "created_by": {
      "id": 1,
      "email": "owner@example.com"
    },
    "created_at": "2024-01-01T00:00:00Z",
    "last_used": null,
    "expires_at": null
  }
]
```

#### Create API Key
```http
POST /stores/{store_id}/api-keys/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New API Key",
  "permissions": [
    "manage_products",
    "view_orders"
  ],
  "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response:**
```json
{
  "id": 2,
  "name": "New API Key",
  "api_key": "sk_test_1234567890abcdef...",
  "prefix": "sk_test_",
  "permissions": [
    "manage_products",
    "view_orders"
  ],
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Get API Key
```http
GET /stores/{store_id}/api-keys/{id}/
Authorization: Bearer {access_token}
```

#### Update API Key
```http
PATCH /stores/{store_id}/api-keys/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Key",
  "permissions": [
    "manage_products",
    "manage_orders"
  ]
}
```

#### Delete API Key
```http
DELETE /stores/{store_id}/api-keys/{id}/
Authorization: Bearer {access_token}
```

#### Revoke API Key
```http
POST /stores/{store_id}/api-keys/{id}/revoke/
Authorization: Bearer {access_token}
```

#### Get Available Actions
```http
GET /stores/{store_id}/api-keys/available_actions/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "actions": [
    "manage_products",
    "view_orders",
    "manage_settings",
    "manage_staff",
    "view_analytics",
    "manage_inventory"
  ]
}
```

## Permissions

### Store Permissions
- **IsStoreOwner**: Full access to owned stores
- **IsStoreMember**: Access to store if member
- **IsStoreAdminOrOwner**: Admin or owner access

### Role-Based Permissions
- **manage_products**: Create, update, delete products
- **view_orders**: View order information
- **manage_orders**: Process and update orders
- **manage_settings**: Update store settings
- **manage_staff**: Manage store staff and roles
- **view_analytics**: Access store analytics
- **manage_inventory**: Manage product inventory

### API Key Permissions
API keys can be assigned specific permissions from the available actions list.

## API Key Authentication

### Using API Keys
```http
GET /stores/{id}/products/
Authorization: Api-Key {api_key}
```

### API Key Headers
```http
Authorization: Api-Key sk_test_1234567890abcdef...
X-API-Key: sk_test_1234567890abcdef...
```

## Error Responses

### Permission Errors
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Validation Errors
```json
{
  "name": ["This field is required."],
  "permissions": ["Invalid permission: invalid_action"]
}
```

### Not Found Errors
```json
{
  "detail": "Not found."
}
```

## Examples

### Complete Store Setup
```bash
# 1. Create store
curl -X POST http://localhost:8000/stores/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Online Store",
    "description": "A sample online store",
    "store_type": "online"
  }'

# 2. Create custom role
curl -X POST http://localhost:8000/stores/1/roles/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Manager",
    "description": "Manages products and inventory",
    "permissions": ["manage_products", "manage_inventory"]
  }'

# 3. Assign role to user
curl -X POST http://localhost:8000/stores/1/user-roles/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user": 2,
    "role": 1
  }'

# 4. Create API key
curl -X POST http://localhost:8000/stores/1/api-keys/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Product Integration",
    "permissions": ["manage_products", "manage_inventory"]
  }'
```

### API Key Usage
```bash
# Use API key to access store resources
curl -X GET http://localhost:8000/stores/1/products/ \
  -H "Authorization: Api-Key sk_test_1234567890abcdef..."
```

### Store Member Management
```bash
# Add member to store
curl -X POST http://localhost:8000/stores/1/members/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 2,
    "role": "admin"
  }'

# View store members
curl -X GET http://localhost:8000/stores/1/members/ \
  -H "Authorization: Bearer {access_token}"

# Update member role
curl -X PATCH http://localhost:8000/stores/memberships/1/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "manager"
  }'
```

## Nested URL Structure

The stores app uses nested URLs for better organization:

```
/stores/                          # Store list/create
/stores/{id}/                     # Store details/update/delete
/stores/{id}/members/             # Store member management
/stores/{id}/roles/               # Store role management
/stores/{id}/user-roles/          # User role assignments
/stores/{id}/api-keys/            # API key management
/stores/memberships/              # User memberships (global)
```

This structure provides clear separation between store-specific resources and global membership management.
