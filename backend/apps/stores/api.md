# Stores API Documentation

## Overview

The Stores API provides endpoints for managing stores in the Digital Farmers CMS. All endpoints follow RESTful conventions and support proper authentication and authorization.

## Base URL

```
/v2/api/stores/
```

## Authentication

- **Public endpoints**: No authentication required
- **Dashboard endpoints**: JWT authentication required

---

## Public Endpoints

### List Active Stores

```http
GET /v2/api/stores/public/
```

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "My Store",
      "slug": "my-store",
      "description": "A great store",
      "logo": null,
      "domain": null,
      "meta_title": "",
      "meta_description": "",
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

### Get Store by Slug

```http
GET /v2/api/stores/public/{slug}/
```

**Response:**
```json
{
  "id": 1,
  "name": "My Store",
  "slug": "my-store",
  "description": "A great store",
  "logo": null,
  "domain": null,
  "meta_title": "",
  "meta_description": "",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## Dashboard Endpoints

### Create Store

```http
POST /v2/api/stores/
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "name": "My Store",
  "slug": "my-store",
  "description": "A great store",
  "store_type": "ecommerce"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "My Store",
  "slug": "my-store",
  "description": "A great store",
  "owner": 1,
  "owner_email": "user@example.com",
  "status": "pending",
  "status_display": "Pending",
  "store_type": "ecommerce",
  "store_type_display": "E-commerce",
  "domain": null,
  "logo": null,
  "favicon": null,
  "settings": {},
  "meta_title": "",
  "meta_description": "",
  "meta_keywords": "",
  "google_analytics_id": "",
  "facebook_pixel_id": "",
  "access_code": "123456",
  "verification_token": "...",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "last_accessed": null
}
```

### Update Store

```http
PUT /v2/api/stores/{id}/
Authorization: Bearer {token}
```

**Request Body:**
```json
{
  "name": "Updated Store Name",
  "description": "Updated description"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Updated Store Name",
  ...
}
```

### Get Store Analytics

```http
GET /v2/api/stores/{id}/analytics/?days=30
Authorization: Bearer {token}
```

**Response:**
```json
{
  "page_views": 1500,
  "unique_visitors": 800,
  "security_events": 5,
  "period_days": 30
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

---

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
