# Themes API Documentation

## Overview
The themes app provides a comprehensive theme management system for stores, including color schemes, layouts, style classes, and templates. Each store can have multiple themes with customizable visual configurations.

**New in this version**: All themes are now scoped under stores, with automatic default theme creation and full CRUD operations.

## Authentication

All themes API endpoints require authentication using JWT tokens:

```http
Authorization: Bearer {access_token}
```

## URL Structure

All theme endpoints are now scoped under stores:

```
/stores/{store_pk}/themes/                    # List/Create themes for a store
/stores/{store_pk}/themes/{id}/               # Get/Update/Delete specific theme
/stores/{store_pk}/color-schemes/             # List/Create color schemes
/stores/{store_pk}/color-schemes/{id}/        # Get/Update/Delete color scheme
/stores/{store_pk}/layouts/                   # List/Create layouts
/stores/{store_pk}/layouts/{id}/              # Get/Update/Delete layout
/stores/{store_pk}/style-classes/             # List/Create style classes
/stores/{store_pk}/style-classes/{id}/        # Get/Update/Delete style class
/stores/{store_pk}/templates/                 # List/Create templates
/stores/{store_pk}/templates/{id}/            # Get/Update/Delete template
```

## Theme Management

### Theme CRUD Operations

#### List Themes
```http
GET /stores/{store_pk}/themes/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `is_default` - Filter by default status (`true`/`false`)
- `key` - Filter by theme key
- `search` - Search in name, key, description
- `ordering` - Sort by `-is_default`, `name`

**Response:**
```json
[
  {
    "id": 1,
    "store": 1,
    "name": "Default Theme",
    "key": "default",
    "description": "Default theme for the store",
    "is_default": true,
    "typography": {
      "headings": {
        "font_family": "Inter, sans-serif",
        "weights": {
          "h1": "700",
          "h2": "600",
          "h3": "600",
          "h4": "600",
          "h5": "500",
          "h6": "500"
        },
        "sizes": {
          "h1": "2.25rem",
          "h2": "1.875rem",
          "h3": "1.5rem",
          "h4": "1.25rem",
          "h5": "1.125rem",
          "h6": "1rem"
        },
        "line_heights": {
          "h1": "1.2",
          "h2": "1.3",
          "h3": "1.4",
          "h4": "1.5",
          "h5": "1.5",
          "h6": "1.6"
        }
      },
      "body": {
        "font_family": "Inter, sans-serif",
        "size": "1rem",
        "line_height": "1.6",
        "weight": "400"
      },
      "buttons": {
        "font_family": "Inter, sans-serif",
        "weight": "500",
        "size": "0.875rem",
        "letter_spacing": "0.025em"
      },
      "inputs": {
        "font_family": "Inter, sans-serif",
        "size": "0.875rem",
        "weight": "400"
      }
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Theme
```http
POST /stores/{store_pk}/themes/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Custom Theme",
  "key": "custom",
  "description": "A custom theme for the store",
  "typography": {
    "headings": {
      "font_family": "Arial, sans-serif"
    }
  }
}
```

#### Get Theme
```http
GET /stores/{store_pk}/themes/{id}/
Authorization: Bearer {access_token}
```

#### Update Theme
```http
PATCH /stores/{store_pk}/themes/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "description": "Updated description"
}
```

#### Delete Theme
```http
DELETE /stores/{store_pk}/themes/{id}/
Authorization: Bearer {access_token}
```

**Note**: Cannot delete the last theme for a store. At least one theme must exist.

**Response:**
```json
{
  "id": 1,
  "store": 1,
  "name": "Default Theme",
  "key": "default",
  "description": "Default theme for the store",
  "is_default": true,
  "typography": {
    "headings": {
      "font_family": "Inter, sans-serif",
      "weights": {
        "h1": "700",
        "h2": "600",
        "h3": "600",
        "h4": "600",
        "h5": "500",
        "h6": "500"
      },
      "sizes": {
        "h1": "2.25rem",
        "h2": "1.875rem",
        "h3": "1.5rem",
        "h4": "1.25rem",
        "h5": "1.125rem",
        "h6": "1rem"
      },
      "line_heights": {
        "h1": "1.2",
        "h2": "1.3",
        "h3": "1.4",
        "h4": "1.5",
        "h5": "1.5",
        "h6": "1.6"
      }
    },
    "body": {
      "font_family": "Inter, sans-serif",
      "size": "1rem",
      "line_height": "1.6",
      "weight": "400"
    },
    "buttons": {
      "font_family": "Inter, sans-serif",
      "weight": "500",
      "size": "0.875rem",
      "letter_spacing": "0.025em"
    },
    "inputs": {
      "font_family": "Inter, sans-serif",
      "size": "0.875rem",
      "weight": "400"
    }
  },
  "color_schemes": [
    {
      "id": 1,
      "theme": 1,
      "key": "default",
      "name": "Default",
      "is_default": true,
      "colors": {
        "background": "#ffffff",
        "headings": "#1f2937",
        "text": "#4b5563",
        "links": "#3b82f6",
        "hover_links": "#2563eb",
        "borders": "#e5e7eb",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "primary_button": {
          "background": "#3b82f6",
          "text": "#ffffff",
          "hover_background": "#2563eb",
          "hover_text": "#ffffff",
          "hover_border": "#2563eb",
          "border": "#3b82f6"
        },
        "secondary_button": {
          "background": "#f3f4f6",
          "text": "#1f2937",
          "hover_background": "#e5e7eb",
          "hover_text": "#1f2937",
          "hover_border": "#d1d5db",
          "border": "#d1d5db"
        },
        "inputs": {
          "background": "#ffffff",
          "text": "#1f2937",
          "border": "#d1d5db",
          "hover_background": "#f9fafb",
          "hover_border": "#9ca3af",
          "focus_border": "#3b82f6"
        },
        "variants": {
          "background": "#ffffff",
          "text": "#1f2937",
          "border": "#e5e7eb",
          "hover_background": "#f3f4f6",
          "hover_text": "#1f2937",
          "hover_border": "#d1d5db"
        }
      },
      "dark_colors": {
        "background": "#111827",
        "headings": "#f3f4f6",
        "text": "#d1d5db",
        "links": "#60a5fa",
        "hover_links": "#3b82f6",
        "borders": "#374151",
        "shadow": "rgba(0, 0, 0, 0.4)",
        "primary_button": {
          "background": "#3b82f6",
          "text": "#ffffff",
          "hover_background": "#2563eb",
          "hover_text": "#ffffff",
          "hover_border": "#2563eb",
          "border": "#3b82f6"
        },
        "secondary_button": {
          "background": "#374151",
          "text": "#f3f4f6",
          "hover_background": "#4b5563",
          "hover_text": "#ffffff",
          "hover_border": "#6b7280",
          "border": "#4b5563"
        },
        "inputs": {
          "background": "#1f2937",
          "text": "#f3f4f6",
          "border": "#4b5563",
          "hover_background": "#374151",
          "hover_border": "#6b7280",
          "focus_border": "#60a5fa"
        },
        "variants": {
          "background": "#1f2937",
          "text": "#f3f4f6",
          "border": "#4b5563",
          "hover_background": "#374151",
          "hover_text": "#ffffff",
          "hover_border": "#6b7280"
        }
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "layouts": [
    {
      "id": 1,
      "theme": 1,
      "store": 3,
      "name": "Default Layout",
      "key": "default",
      "description": "Default layout for the theme",
      "header_template": null,
      "footer_template": null,
      "content_slots": {
        "main": "Main content area",
        "sidebar": "Sidebar content",
        "header": "Header content"
      },
      "is_default": true,
      "is_system": false,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "style_classes": [
    {
      "id": 1,
      "theme": 1,
      "name": "Primary Button",
      "slug": "btn-primary",
      "description": "Primary button style class",
      "default_css": {
        "color": "#ffffff",
        "background-color": "#3b82f6",
        "padding": "10px 20px",
        "border-radius": "6px",
        "font-weight": "500"
      },
      "light_css": {
        "background-color": "#2563eb",
        "color": "#ffffff"
      },
      "dark_css": {
        "background-color": "#1d4ed8",
        "color": "#ffffff"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "templates": [
    {
      "id": 1,
      "theme": 1,
      "name": "Product Page",
      "key": "product-page",
      "template_role": "body",
      "content": "<div class=\"product-page\">\n  <header>\n    <h1>{{ product.name }}</h1>\n  </header>\n  <main>\n    <div class=\"product-image\">\n      <img src=\"{{ product.image }}\" alt=\"{{ product.name }}\">\n    </div>\n    <div class=\"product-details\">\n      <p>{{ product.description }}</p>\n      <p>Price: ${{ product.price }}</p>\n    </div>\n  </main>\n</div>",
      "content_type": "html",
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Color Schemes

### Color Scheme CRUD Operations

#### List Color Schemes
```http
GET /stores/{store_pk}/color-schemes/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `theme` - Filter by theme ID
- `is_default` - Filter by default status (`true`/`false`)
- `key` - Filter by color scheme key
- `search` - Search in name, key
- `ordering` - Sort by `-is_default`, `name`

#### Create Color Scheme
```http
POST /stores/{store_pk}/color-schemes/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "theme": 1,
  "name": "Dark Mode",
  "key": "dark",
  "colors": {
    "background": "#1f2937",
    "headings": "#ffffff",
    "text": "#d1d5db",
    "links": "#60a5fa",
    "hover_links": "#3b82f6",
    "borders": "#374151",
    "shadow": "rgba(0, 0, 0, 0.4)",
    "primary_button": {
      "background": "#3b82f6",
      "text": "#ffffff",
      "hover_background": "#2563eb",
      "hover_text": "#ffffff",
      "hover_border": "#2563eb",
      "border": "#3b82f6"
    }
  },
  "dark_colors": {
    "background": "#111827",
    "headings": "#f3f4f6",
    "text": "#cbd5e1",
    "links": "#93c5fd",
    "hover_links": "#60a5fa",
    "borders": "#374151",
    "shadow": "rgba(0, 0, 0, 0.5)",
    "primary_button": {
      "background": "#60a5fa",
      "text": "#ffffff",
      "hover_background": "#3b82f6",
      "hover_text": "#ffffff",
      "hover_border": "#3b82f6",
      "border": "#60a5fa"
    }
  }
}
```

#### Get Color Scheme
```http
GET /stores/{store_pk}/color-schemes/{id}/
Authorization: Bearer {access_token}
```

#### Update Color Scheme
```http
PATCH /stores/{store_pk}/color-schemes/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Updated Dark Mode"
}
```

#### Delete Color Scheme
```http
DELETE /stores/{store_pk}/color-schemes/{id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "theme": 1,
  "key": "default",
  "name": "Default",
  "is_default": true,
  "colors": {
    "background": "#ffffff",
    "headings": "#1f2937",
    "text": "#4b5563",
    "links": "#3b82f6",
    "hover_links": "#2563eb",
    "borders": "#e5e7eb",
    "shadow": "rgba(0, 0, 0, 0.1)",
    "primary_button": {
      "background": "#3b82f6",
      "text": "#ffffff",
      "hover_background": "#2563eb",
      "hover_text": "#ffffff",
      "hover_border": "#2563eb",
      "border": "#3b82f6"
    },
    "secondary_button": {
      "background": "#f3f4f6",
      "text": "#1f2937",
      "hover_background": "#e5e7eb",
      "hover_text": "#1f2937",
      "hover_border": "#d1d5db",
      "border": "#d1d5db"
    },
    "inputs": {
      "background": "#ffffff",
      "text": "#1f2937",
      "border": "#d1d5db",
      "hover_background": "#f9fafb",
      "hover_border": "#9ca3af",
      "focus_border": "#3b82f6"
    },
    "variants": {
      "background": "#ffffff",
      "text": "#1f2937",
      "border": "#e5e7eb",
      "hover_background": "#f3f4f6",
      "hover_text": "#1f2937",
      "hover_border": "#d1d5db"
    }
  },
  "dark_colors": {
    "background": "#111827",
    "headings": "#f3f4f6",
    "text": "#d1d5db",
    "links": "#60a5fa",
    "hover_links": "#3b82f6",
    "borders": "#374151",
    "shadow": "rgba(0, 0, 0, 0.4)",
    "primary_button": {
      "background": "#3b82f6",
      "text": "#ffffff",
      "hover_background": "#2563eb",
      "hover_text": "#ffffff",
      "hover_border": "#2563eb",
      "border": "#3b82f6"
    },
    "secondary_button": {
      "background": "#374151",
      "text": "#f3f4f6",
      "hover_background": "#4b5563",
      "hover_text": "#ffffff",
      "hover_border": "#6b7280",
      "border": "#4b5563"
    },
    "inputs": {
      "background": "#1f2937",
      "text": "#f3f4f6",
      "border": "#4b5563",
      "hover_background": "#374151",
      "hover_border": "#6b7280",
      "focus_border": "#60a5fa"
    },
    "variants": {
      "background": "#1f2937",
      "text": "#f3f4f6",
      "border": "#4b5563",
      "hover_background": "#374151",
      "hover_text": "#ffffff",
      "hover_border": "#6b7280"
    }
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Layouts

### Layout CRUD Operations

#### List Layouts
```http
GET /stores/{store_pk}/layouts/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `theme` - Filter by theme ID
- `key` - Filter by layout key
- `is_default` - Filter by default status (`true`/`false`)
- `is_active` - Filter by active status (`true`/`false`)
- `search` - Search in name, key, description
- `ordering` - Sort by `name`

#### Create Layout
```http
POST /stores/{store_pk}/layouts/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "theme": 1,
  "name": "Product Layout",
  "key": "product",
  "description": "Layout for product pages",
  "header_template": null,
  "footer_template": null,
  "content_slots": {
    "main": "Main content area",
    "sidebar": "Product sidebar",
    "reviews": "Customer reviews section"
  },
  "is_default": false,
  "is_system": false,
  "is_active": true
}
```

#### Get Layout
```http
GET /stores/{store_pk}/layouts/{id}/
Authorization: Bearer {access_token}
```

#### Update Layout
```http
PATCH /stores/{store_pk}/layouts/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "description": "Updated layout description"
}
```

#### Delete Layout
```http
DELETE /stores/{store_pk}/layouts/{id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "theme": 1,
  "store": 3,
  "name": "Default Layout",
  "key": "default",
  "description": "Default layout for the theme",
  "header_template": null,
  "footer_template": null,
  "content_slots": {
    "main": "Main content area",
    "sidebar": "Sidebar content",
    "header": "Header content"
  },
  "is_default": true,
  "is_system": false,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Style Classes

### Style Class CRUD Operations

#### List Style Classes
```http
GET /stores/{store_pk}/style-classes/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `theme` - Filter by theme ID
- `slug` - Filter by style class slug
- `search` - Search in name, slug, description
- `ordering` - Sort by `name`

#### Create Style Class
```http
POST /stores/{store_pk}/style-classes/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "theme": 1,
  "name": "Call to Action Button",
  "slug": "btn-cta",
  "description": "Large call-to-action button",
  "default_css": {
    "color": "#ffffff",
    "background-color": "#ef4444",
    "padding": "12px 24px",
    "border-radius": "8px",
    "font-weight": "600",
    "font-size": "1rem"
  },
  "light_css": {
    "background-color": "#dc2626",
    "color": "#ffffff"
  },
  "dark_css": {
    "background-color": "#b91c1c",
    "color": "#ffffff"
  }
}
```

#### Get Style Class
```http
GET /stores/{store_pk}/style-classes/{id}/
Authorization: Bearer {access_token}
```

#### Update Style Class
```http
PATCH /stores/{store_pk}/style-classes/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "description": "Updated button description"
}
```

#### Delete Style Class
```http
DELETE /stores/{store_pk}/style-classes/{id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "theme": 1,
  "name": "Primary Button",
  "slug": "btn-primary",
  "description": "Primary button style class",
  "default_css": {
    "color": "#ffffff",
    "background-color": "#3b82f6",
    "padding": "10px 20px",
    "border-radius": "6px",
    "font-weight": "500"
  },
  "light_css": {
    "background-color": "#2563eb",
    "color": "#ffffff"
  },
  "dark_css": {
    "background-color": "#1d4ed8",
    "color": "#ffffff"
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Templates

### Template CRUD Operations

#### List Templates
```http
GET /stores/{store_pk}/templates/
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `theme` - Filter by theme ID
- `key` - Filter by template key
- `template_role` - Filter by template role (`body`, `header`, `footer`, `partial`, `section`)
- `template_type` - Filter by template type (PostType key or 'any')
- `is_active` - Filter by active status (`true`/`false`)
- `search` - Search in name, key
- `ordering` - Sort by `name`

#### Create Template
```http
POST /stores/{store_pk}/templates/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "theme": 1,
  "name": "Hero Section",
  "key": "hero-section",
  "template_role": "section",
  "template_type": "any",
  "content": "<section class=\"hero-section bg-primary text-white py-20\">\n  <div class=\"container mx-auto px-4 text-center\">\n    <h1 class=\"text-4xl font-bold mb-4\">{{ hero.title }}</h1>\n    <p class=\"text-xl mb-8\">{{ hero.subtitle }}</p>\n    <a href=\"{{ hero.cta_link }}\" class=\"btn-primary\">{{ hero.cta_text }}</a>\n  </div>\n</section>",
  "content_type": "html",
  "is_active": true
}
```

**Notes:**
- `template_type` accepts any PostType key (e.g., 'page', 'post', 'blog') or 'any' for generic templates
- New PostTypes created in the system automatically work as valid template_type values
- `template_type` must follow slug format (lowercase, numbers, hyphens) or be 'any'
- For body templates, template_type affects which post types can use the template

#### Update Template
```http
PATCH /stores/{store_pk}/templates/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "is_active": false
}
```

#### Delete Template
```http
DELETE /stores/{store_pk}/templates/{id}/
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "theme": 1,
  "name": "Product Page",
  "key": "product-page",
  "template_role": "body",
  "content": "<div class=\"product-page\">\n  <header>\n    <h1>{{ product.name }}</h1>\n  </header>\n  <main>\n    <div class=\"product-image\">\n      <img src=\"{{ product.image }}\" alt=\"{{ product.name }}\">\n    </div>\n    <div class=\"product-details\">\n      <p>{{ product.description }}</p>\n      <p>Price: ${{ product.price }}</p>\n    </div>\n  </main>\n</div>",
  "content_type": "html",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

## Default Color Schemes

The themes app includes two pre-defined color schemes that are automatically created with each theme:

### Default Color Scheme
- **Key**: `default`
- **Name**: "Default"
- **Is Default**: `true`
- **Colors**: Light mode with blue primary colors
- **Dark Colors**: Dark mode with blue accents

### Schema 1 Color Scheme
- **Key**: `schema-1`
- **Name**: "Schema 1"
- **Is Default**: `false`
- **Colors**: Light mode with green primary colors
- **Dark Colors**: Dark mode with green accents

## Typography Structure

All themes include a comprehensive typography configuration:

### Headings Typography
```json
{
  "headings": {
    "font_family": "Inter, sans-serif",
    "weights": {
      "h1": "700",
      "h2": "600",
      "h3": "600",
      "h4": "600",
      "h5": "500",
      "h6": "500"
    },
    "sizes": {
      "h1": "2.25rem",
      "h2": "1.875rem",
      "h3": "1.5rem",
      "h4": "1.25rem",
      "h5": "1.125rem",
      "h6": "1rem"
    },
    "line_heights": {
      "h1": "1.2",
      "h2": "1.3",
      "h3": "1.4",
      "h4": "1.5",
      "h5": "1.5",
      "h6": "1.6"
    }
  }
}
```

### Body Typography
```json
{
  "body": {
    "font_family": "Inter, sans-serif",
    "size": "1rem",
    "line_height": "1.6",
    "weight": "400"
  }
}
```

### Button Typography
```json
{
  "buttons": {
    "font_family": "Inter, sans-serif",
    "weight": "500",
    "size": "0.875rem",
    "letter_spacing": "0.025em"
  }
}
```

### Input Typography
```json
{
  "inputs": {
    "font_family": "Inter, sans-serif",
    "size": "0.875rem",
    "weight": "400"
  }
}
```

## Permissions

### Theme Access Control
- **Store Owners**: Full CRUD access to their store's themes and all related components
- **Store Admins**: Full CRUD access to themes for stores they administer
- **Store Members**: Read access to themes, limited write access based on role permissions
- **System Admin**: Full access to all themes across all stores

### CRUD Operations Available
All theme endpoints now support full CRUD operations:
- **Create**: POST requests to create new themes, color schemes, layouts, style classes, and templates
- **Read**: GET requests to retrieve theme data
- **Update**: PATCH requests for partial updates, PUT for full updates
- **Delete**: DELETE requests with validation (cannot delete last theme per store)

### Data Access
- Users can only access themes for stores they have permissions for
- All theme operations are validated against store membership
- Theme data includes sensitive configuration stored in JSON fields
- Cross-store access is prevented by URL scoping and permission checks

## Error Responses

### Authentication Errors
```json
{
  "detail": "Authentication credentials were not provided."
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
  "error": "Cannot delete the last theme for this store. At least one theme must exist."
}
```

### Theme Not Found Errors
```json
{
  "detail": "Not found."
}
```

## Filtering and Searching

### Filter Parameters
All list endpoints support Django-filter filtering:

```http
GET /themes/list/?store=1&is_default=true
GET /themes/color-schemes/?theme=1&is_default=false
GET /themes/layouts/?theme=1&key=default
```

### Search
All endpoints support full-text search:

```http
GET /themes/list/?search=dark
GET /themes/color-schemes/?search=blue
GET /themes/layouts/?search=sidebar
```

### Ordering
All endpoints support ordering:

```http
GET /themes/list/?ordering=-is_default,name
GET /themes/color-schemes/?ordering=name
GET /themes/layouts/?ordering=name
```

## Examples

### Get All Themes for a Store
```bash
curl -X GET http://localhost:8000/stores/1/themes/ \
  -H "Authorization: Bearer {access_token}"
```

### Create a New Theme for a Store
```bash
curl -X POST http://localhost:8000/stores/1/themes/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dark Theme",
    "key": "dark-theme",
    "description": "A dark theme variant",
    "typography": {
      "body": {
        "font_family": "Inter, sans-serif"
      }
    }
  }'
```

### Update a Theme
```bash
curl -X PATCH http://localhost:8000/stores/1/themes/1/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated theme description"
  }'
```

### Get Default Color Scheme
```bash
curl -X GET http://localhost:8000/stores/1/color-schemes/?theme=1&is_default=true \
  -H "Authorization: Bearer {access_token}"
```

### Create a Color Scheme
```bash
curl -X POST http://localhost:8000/stores/1/color-schemes/ \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "theme": 1,
    "name": "Ocean Blue",
    "key": "ocean-blue",
    "colors": {
      "background": "#f0f9ff",
      "headings": "#0c4a6e",
      "text": "#374151",
      "links": "#0369a1",
      "borders": "#bae6fd",
      "primary_button": {
        "background": "#0369a1",
        "text": "#ffffff"
      }
    }
  }'
```

### Search Themes
```bash
curl -X GET http://localhost:8000/stores/1/themes/?search=dark \
  -H "Authorization: Bearer {access_token}"
```

### Get All Theme Components
```bash
# Get theme with all nested data (recommended approach)
curl -X GET http://localhost:8000/stores/1/themes/1/ \
  -H "Authorization: Bearer {access_token}"

# Or get components separately
curl -X GET http://localhost:8000/stores/1/color-schemes/?theme=1 \
  -H "Authorization: Bearer {access_token}"

curl -X GET http://localhost:8000/stores/1/layouts/?theme=1 \
  -H "Authorization: Bearer {access_token}"

curl -X GET http://localhost:8000/stores/1/style-classes/?theme=1 \
  -H "Authorization: Bearer {access_token}"

curl -X GET http://localhost:8000/stores/1/templates/?theme=1 \
  -H "Authorization: Bearer {access_token}"
```

## Integration Examples

### Frontend Integration

```javascript
// Get all themes for a store
const response = await fetch('/themes/list/?store=1', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const themes = await response.json();

// Get theme with all nested data (recommended)
const themeResponse = await fetch('/themes/list/1/', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
const theme = await themeResponse.json();

// Access nested data
console.log('Theme:', theme.name);
console.log('Color Schemes:', theme.color_schemes);
console.log('Layouts:', theme.layouts);
console.log('Style Classes:', theme.style_classes);
console.log('Templates:', theme.templates);

// Apply color scheme to app
const applyColorScheme = (colorScheme) => {
  const root = document.documentElement;

  // Apply light mode colors
  root.style.setProperty('--background', colorScheme.colors.background);
  root.style.setProperty('--text-color', colorScheme.colors.text);
  root.style.setProperty('--primary-color', colorScheme.colors.primary_button.background);

  // Apply dark mode colors if available
  if (colorScheme.dark_colors) {
    root.style.setProperty('--background-dark', colorScheme.dark_colors.background);
    root.style.setProperty('--text-color-dark', colorScheme.dark_colors.text);
  }
};

// Apply default color scheme
const defaultColorScheme = theme.color_schemes.find(cs => cs.is_default);
if (defaultColorScheme) {
  applyColorScheme(defaultColorScheme);
}
```

### Mobile App Integration

```javascript
// Get default color scheme
const getDefaultColorScheme = async (themeId) => {
  const response = await fetch(`/themes/color-schemes/?theme=${themeId}&is_default=true`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  const schemes = await response.json();
  return schemes[0];
};

// Apply color scheme to app
const applyColorScheme = (colorScheme) => {
  const root = document.documentElement;

  // Apply light mode colors
  root.style.setProperty('--background', colorScheme.colors.background);
  root.style.setProperty('--text-color', colorScheme.colors.text);
  root.style.setProperty('--primary-color', colorScheme.colors.primary_button.background);

  // Apply dark mode colors if available
  if (colorScheme.dark_colors) {
    root.style.setProperty('--background-dark', colorScheme.dark_colors.background);
    root.style.setProperty('--text-color-dark', colorScheme.dark_colors.text);
  }
};
```

## Theme Initialization

### Automatic Theme Creation
When a new store is created, a complete default theme system is automatically created with:

1. **Default Theme**: Name "Default Theme", key "default"
2. **Default Color Schemes**: Both "default" and "schema-1" color schemes with light/dark mode support
3. **Typography Configuration**: Complete typography settings for headings, body, buttons, and inputs
4. **Theme Protection**: Cannot delete the last theme for a store (at least one theme always exists)

### Automatic Setup Details
- **Theme Creation**: Triggered automatically in `StoreService.create_store()`
- **Color Schemes**: Two pre-configured schemes (default blue theme and green schema-1)
- **Typography**: Inter font family with proper sizing and weights
- **Validation**: Ensures store-theme relationships are maintained
- **Uniqueness**: Each store gets its own independent theme system

### Default Theme Structure
```
Store
├── Theme (auto-created)
│   ├── ColorScheme "default" (light/dark colors)
│   ├── ColorScheme "schema-1" (alternative colors)
│   ├── Layout (future: auto-created layouts)
│   ├── StyleClass (future: auto-created classes)
│   └── Template (future: auto-created templates)
```

### Manual Theme Management
After automatic setup, store owners can:
- Create additional themes
- Modify existing themes and color schemes
- Update typography settings
- Add custom layouts, style classes, and templates
- Switch between themes (future feature)

## Data Structure

### Theme Relationships
```
Store (from stores app)
├── Theme (1:many)
│   ├── ColorScheme (1:many)
│   ├── Layout (1:many)
│   ├── StyleClass (1:many)
│   └── Template (1:many)
│   └── typography (JSONField)
```

### Unique Constraints
- Each store can have unique theme keys and names
- Each theme can have unique color scheme keys and names
- Each theme can have unique layout keys and names
- Each theme can have unique style class keys and names
- Each theme can have unique template keys and names

### Default Behavior
- Only one theme per store can be marked as `is_default`
- Only one color scheme per theme can be marked as `is_default`
- When a new theme is created, it's not set as default (manual process)
- When a new color scheme is created, it's not set as default (manual process)

## Security Considerations

### Data Access
- Users can only access themes for stores they have permissions for
- Theme data is read-only through API
- Sensitive configuration data is stored in JSON fields

### Rate Limiting
- Apply standard Django REST framework rate limiting
- Consider implementing custom rate limiting for theme endpoints
- Monitor API usage for potential abuse

### Data Validation
- All JSON fields are validated by Django's JSONField
- Slug fields ensure URL-safe keys
- Foreign key constraints ensure data integrity

## Performance Considerations

### Database Optimization
- Use `select_related` for theme queries with related data
- Implement pagination for large theme lists
- Consider database indexing for frequently queried fields

### Caching
- Consider caching theme data for frequently accessed themes
- Cache color scheme data for performance
- Implement cache invalidation when themes are updated

### API Optimization
- Use viewsets for consistent API patterns
- Implement proper filtering and pagination
- Consider response compression for large JSON data
