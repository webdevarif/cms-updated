# Stores API Documentation v2.0

## Overview
The Stores API provides comprehensive store management functionality for the Digital Farmers CMS platform. This API allows users to create, manage, and configure their online stores with full multi-tenant support.

## Authentication
- **Public Endpoints**: No authentication required
- **Customer Endpoints**: Requires `IsStoreUser` permission (store users)
- **Dashboard Endpoints**: Requires `IsStoreOwner` permission (store owners only)

## Endpoints

### Public Endpoints (`/v2/public/`)
Provides read-only access to active stores for store discovery.

#### List Stores
```
GET /api/stores/v2/public/
```
Query parameters:
- `domain` - Filter by domain
- `subdomain` - Filter by subdomain slug

#### Get Store Details
```
GET /api/stores/v2/public/{id}/
```

### Customer Endpoints (`/v2/customer/`)
Allows authenticated store users to manage their stores.

#### List My Stores
```
GET /api/stores/v2/customer/
```

#### Create Store
```
POST /api/stores/v2/customer/
```

#### Update Store
```
PUT /api/stores/v2/customer/{id}/
PATCH /api/stores/v2/customer/{id}/
```

#### Verify Store Email
```
POST /api/stores/v2/customer/{id}/verify_email/
```

### Dashboard Endpoints (`/v2/dashboard/`)
Full store management for store owners.

#### Store CRUD Operations
Same as customer endpoints with additional permissions.

#### Store Actions
```
POST /api/stores/v2/dashboard/{id}/activate/
POST /api/stores/v2/dashboard/{id}/deactivate/
```

#### Analytics
```
GET /api/stores/v2/dashboard/{id}/analytics/?days=30
```

#### Store Settings
```
GET /api/stores/v2/dashboard/{id}/settings/
PUT /api/stores/v2/dashboard/{id}/settings/
PATCH /api/stores/v2/dashboard/{id}/settings/
```

## Data Models

### Store Model
```json
{
  "id": "uuid",
  "name": "Store Name",
  "slug": "store-slug",
  "domain": "store.example.com",
  "description": "Store description",
  "logo": "media_file_id",
  "favicon": "media_file_id",
  "status": "active|pending|inactive|suspended",
  "store_type": "ecommerce|blog|portfolio|corporate|other",
  "verification_token": "token",
  "access_code": "6-digit-code",
  "meta_title": "SEO Title",
  "meta_description": "SEO Description",
  "meta_keywords": "keyword1,keyword2",
  "google_analytics_id": "GA-XXXXX",
  "facebook_pixel_id": "123456789",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z",
  "last_accessed": "2023-01-01T00:00:00Z"
}
```

### Store Settings Model
```json
{
  "site_name": "My Store",
  "site_description": "Store description",
  "contact_email": "contact@store.com",
  "phone": "+1234567890",
  "address": "123 Main St",
  "city": "City",
  "state": "State",
  "country": "Country",
  "postal_code": "12345",
  "currency": "USD",
  "timezone": "UTC",
  "language": "en",
  "tax_rate": 0.08,
  "shipping_enabled": true,
  "free_shipping_threshold": 50.00,
  "logo": "media_file_id",
  "favicon": "media_file_id",
  "custom_settings": {},
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-01T00:00:00Z"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation error message",
  "field_errors": {
    "name": ["This field is required"],
    "slug": ["Slug must be unique"]
  }
}
```

### 401 Unauthorized
```json
{
  "error": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "error": "You don't have permission to access this store"
}
```

### 404 Not Found
```json
{
  "error": "Store not found"
}
```

## Rate Limiting
- Emails: 100/hour per store
- SMTP Tests: 10/hour per user

## Management Commands

### Migrate Stores
```bash
python manage.py migrate_stores --dry-run --batch-size=1000
```

## Version History
- **v2.0**: Complete rewrite with consolidated API structure
- **v1.0**: Legacy three-layer architecture (deprecated)
