# Accounts API Documentation

## Overview
The accounts app handles user authentication, user management, and social authentication endpoints.

## Authentication

### Djoser Authentication Endpoints

#### User Registration
```http
POST /auth/users/
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123",
  "re_password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```http
POST /auth/jwt/create/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /auth/jwt/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Current User
```http
GET /auth/users/me/
Authorization: Bearer {access_token}
```

#### Change Password
```http
POST /auth/users/set_password/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "new_password": "newpassword123",
  "re_new_password": "newpassword123",
  "current_password": "oldpassword123"
}
```

#### Password Reset
```http
POST /auth/users/reset_password/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Resend Activation Email
```http
POST /auth/users/resend_activation/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

## User Management

### User CRUD Operations

#### List Users
```http
GET /users/
Authorization: Bearer {access_token}
```

**Response (Admin):**
```json
[
  {
    "id": 1,
    "email": "admin@example.com",
    "username": "admin",
    "first_name": "Admin",
    "last_name": "User",
    "display_name": "Admin User",
    "is_active": true,
    "is_superuser": true,
    "date_joined": "2024-01-01T00:00:00Z"
  }
]
```

**Response (Regular User):** Only returns current user

#### Create User (Admin Only)
```http
POST /users/
Authorization: Bearer {admin_access_token}
Content-Type: application/json

{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Get User
```http
GET /users/{id}/
Authorization: Bearer {access_token}
```

#### Update User
```http
PATCH /users/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name"
}
```

#### Delete User (Admin Only)
```http
DELETE /users/{id}/
Authorization: Bearer {admin_access_token}
```

### User Profile

#### Get Current Profile
```http
GET /users/profile/
Authorization: Bearer {access_token}
```

#### Update Current Profile
```http
PATCH /users/profile/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name"
}
```

### User Actions

#### Activate User (Admin Only)
```http
POST /users/{id}/activate/
Authorization: Bearer {admin_access_token}
```

#### Deactivate User (Admin Only)
```http
POST /users/{id}/deactivate/
Authorization: Bearer {admin_access_token}
```

## Social Authentication

#### Social Login
```http
POST /auth/social/{provider}/
Content-Type: application/json

{
  "uid": "123456789",
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Supported Providers:** `github`, `google`, `facebook`

**Response:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "display_name": "John Doe"
  }
}
```

## Authentication Methods

### Email or Username Login
The system supports login with either email or username:

```http
POST /auth/jwt/create/
Content-Type: application/json

{
  "email": "user@example.com"  // or "username": "username"
  "password": "password123"
}
```

### Custom Authentication Backend
- **EmailOrUsernameModelBackend**: Allows login with email or username
- **Priority**: Custom backend → Django ModelBackend → Allauth backend

## Permissions

### User Management Permissions
- **Admin Users**: Full CRUD access to all users
- **Regular Users**: Can only update their own profile
- **Superusers**: Full system access

### Social Auth
- **Public Access**: Social login endpoints are public
- **Required Fields**: `uid`, `email`, `name`

## Error Responses

### Authentication Errors
```json
{
  "detail": "No active account found with the given credentials"
}
```

### Permission Errors
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Validation Errors
```json
{
  "email": ["A user with that email already exists."],
  "password": ["This field is required."]
}
```

## Email Verification

### Registration Flow
1. User registers via `/auth/users/`
2. Verification email sent (if enabled)
3. User clicks verification link
4. Account activated
5. User can login

### Configuration
- **Development**: Email verification disabled
- **Production**: Email verification required
- **Environment Variable**: `EMAIL_VERIFICATION_ENABLED`

## Rate Limiting

### Login Attempts
- **Limit**: 5 failed attempts
- **Timeout**: 5 minutes
- **Reset**: After successful login or timeout

## Security Features

### Password Requirements
- Minimum length: 8 characters
- Common passwords rejected
- Numeric passwords rejected
- User attribute similarity rejected

### Token Security
- **Access Token**: 60 minutes lifetime
- **Refresh Token**: 7 days lifetime
- **Rotation**: Refresh tokens rotate on use
- **Algorithm**: HS256

## Examples

### Complete User Registration Flow
```bash
# 1. Register user
curl -X POST http://localhost:8000/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "re_password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'

# 2. Login
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# 3. Get profile
curl -X GET http://localhost:8000/users/profile/ \
  -H "Authorization: Bearer {access_token}"
```

### Admin User Management
```bash
# 1. Admin login
curl -X POST http://localhost:8000/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# 2. List all users
curl -X GET http://localhost:8000/users/ \
  -H "Authorization: Bearer {admin_access_token}"

# 3. Create new user
curl -X POST http://localhost:8000/users/ \
  -H "Authorization: Bearer {admin_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "newpass123",
    "first_name": "New",
    "last_name": "User"
  }'
```
