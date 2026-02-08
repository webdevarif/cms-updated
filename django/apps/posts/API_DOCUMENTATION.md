# Posts API Documentation

## Overview
The posts app provides a flexible content management system with custom post types, posts, and pages per store. It supports blog posts, static pages, and extensible custom content types.

**Important:** All API endpoints require a `Store` header to scope data by store. Missing Store header returns `400 Bad Request`.

## Authentication
All endpoints require authentication via `Authorization: Bearer {token}` header and a `Store` header to scope data by store.

```http
Authorization: Bearer {token}
Store: 1
```

### PostType
Represents a custom post type (blog, page, product, etc.) scoped by store.

**Fields:**
- `store` (FK to Store): The store this post type belongs to
- `name` (string): Human-readable name
- `key` (slug): Unique identifier within store (e.g., 'post', 'page')
- `description` (text): Optional description
- `is_builtin` (boolean): System post types that cannot be deleted
- `is_active` (boolean): Whether this post type is active
- `schema` (JSON): Optional JSON schema for custom fields
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Unique together: `store`, `key`

### Post
Content entry under a PostType, scoped by store.

**Fields:**
- `store` (FK to Store): The store this post belongs to
- `post_type` (FK to PostType): The type of this post
- `title` (string): Post title
- `slug` (slug): URL-friendly identifier
- `excerpt` (text): Optional short summary
- `content` (text): Main content (HTML, Markdown, or JSON)
- `content_type` (choice): 'html', 'markdown', 'json'
- `status` (choice): 'draft', 'published', 'archived'
- `is_featured` (boolean): Whether this post is featured
- `published_at` (datetime): When this post was published
- `created_by` (FK to User): User who created this post (display name shown)
- `updated_by` (FK to User): User who last updated this post (display name shown)
- `template` (object): Selected body template for active theme (read-only)
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Unique together: `store`, `post_type`, `slug`
- Auto-sets `published_at` when status changes to 'published'

### PostMeta
Key/value metadata for posts to support custom fields.

**Fields:**
- `post` (FK to Post): The post this metadata belongs to
- `key` (string): Metadata key
- `value` (JSON): Metadata value (can be string, number, object, etc.)
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Unique together: `post`, `key`

### Category
Hierarchical categories for organizing posts, scoped by store.

**Fields:**
- `store` (FK to Store): The store this category belongs to
- `name` (string): Human-readable name
- `slug` (slug): URL-friendly identifier
- `description` (text): Optional category description
- `parent` (FK to Category): Parent category for hierarchy (nullable)
- `is_active` (boolean): Whether this category is active
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Unique together: `store`, `slug`
- Prevents circular references in parent hierarchy

### Tag
Simple tags for labeling posts, scoped by store.

**Fields:**
- `store` (FK to Store): The store this tag belongs to
- `name` (string): Human-readable name
- `slug` (slug): URL-friendly identifier
- `description` (text): Optional tag description
- `is_active` (boolean): Whether this tag is active
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Unique together: `store`, `slug`

### Comment
Comments on posts with optional threading support.

**Fields:**
- `store` (FK to Store): The store this comment belongs to (matches post.store)
- `post` (FK to Post): The post this comment belongs to
- `user` (FK to User): The user who made this comment
- `parent` (FK to Comment): Parent comment for replies (nullable)
- `content` (text): Comment content
- `is_approved` (boolean): Whether this comment is approved
- `is_public` (boolean): Whether this comment is public
- `created_at`, `updated_at` (datetime): Timestamps

**Constraints:**
- Comments can only be nested one level deep
- Comment store must match post store

### Post Types

#### List Post Types
```http
GET /posts/post-types/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `is_builtin` (boolean): Filter by builtin status
- `search` (string): Search in name, key, description

**Response:**
```json
[
  {
    "id": 1,
    "store": 1,
    "name": "Post",
    "key": "post",
    "description": "Standard blog posts",
    "is_builtin": true,
    "is_active": true,
    "schema": null,
    "post_count": 5,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Post Type
```http
POST /posts/post-types/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "name": "Product",
  "key": "product",
  "description": "Product pages",
  "is_active": true
}
```

**Response:**
```json
{
  "id": 2,
  "store": 1,
  "name": "Product",
  "key": "product",
  "description": "Product pages",
  "is_builtin": false,
  "is_active": true,
  "schema": null,
  "post_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### Get Post Type
```http
GET /posts/post-types/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Post Type
```http
PATCH /posts/post-types/{id}/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Product",
  "description": "Updated description"
}
```

#### Delete Post Type
```http
DELETE /posts/post-types/{id}/?store=1
Authorization: Bearer {token}
```

**Note:** Builtin post types cannot be deleted.

### Posts

#### List Posts
```http
GET /posts/posts/
Authorization: Bearer {token}
```

**Query Parameters:**
- `store` (int): Filter by store ID
- `post_type` (int): Filter by post type ID
- `post_type_key` (string): Filter by post type key (e.g., 'post', 'page')
- `status` (string): Filter by status ('draft', 'published', 'archived')
- `is_featured` (boolean): Filter by featured status
- `content_type` (string): Filter by content type ('html', 'markdown', 'json')
- `search` (string): Search in title, slug, excerpt, content

**Response:**
```json
[
  {
    "id": 1,
    "store": 1,
    "post_type": 1,
    "post_type_name": "Post",
    "post_type_key": "post",
    "title": "My First Blog Post",
    "slug": "my-first-blog-post",
    "excerpt": "This is my first blog post",
    "content": "<p>Hello world!</p>",
    "content_type": "html",
    "status": "published",
    "is_featured": false,
    "published_at": "2024-01-01T00:00:00Z",
    "meta": [
      {
        "id": 1,
        "key": "seo_title",
        "value": "Custom SEO Title",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ],
    "created_by": "John Doe",
    "updated_by": "John Doe",
    "template": {
      "id": 5,
      "name": "Blog Standard Template",
      "key": "blog-standard",
      "template_role": "body",
      "template_type": "post",
      "theme_id": 2
    },
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
]
```

#### Create Post
```http
POST /posts/posts/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "post_type": 1,
  "title": "New Blog Post",
  "content": "<p>This is a new blog post.</p>",
  "content_type": "html",
  "status": "draft",
  "meta": [
    {"key": "author", "value": "John Doe"},
    {"key": "tags", "value": ["blog", "news"]}
  ]
}
```

#### Get Post
```http
GET /posts/posts/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Post
```http
PATCH /posts/posts/{id}/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "title": "Updated Title",
  "status": "published"
}
```

#### Delete Post
```http
DELETE /posts/posts/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Get Published Posts
```http
GET /posts/posts/published/
Authorization: Bearer {token}
Store: 1&post_type_key=post
```

### Pages

Pages are posts with `post_type.key = 'page'`. They can be accessed through the dedicated pages endpoint or filtered through the posts endpoint.

#### List Pages
```http
GET /posts/pages/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:** Same as posts, but automatically filtered to pages.

#### Create Page
```http
POST /posts/pages/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "title": "About Us",
  "slug": "about-us",
  "content": "<h1>About Our Company</h1><p>Welcome to our website...</p>",
  "status": "published"
}
```

**Note:** `post_type` is automatically set to the "page" post type and should not be included in the request.

### Post Type Templates

Manages which template is selected for each post type under each theme.

#### List Post Type Templates
```http
GET /posts/post-type-templates/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `post_type` (int): Filter by post type ID
- `theme` (int): Filter by theme ID
- `template` (int): Filter by template ID

**Response:**
```json
[
  {
    "id": 1,
    "store": 1,
    "post_type": 1,
    "post_type_name": "Page",
    "theme": 2,
    "theme_name": "Default Theme",
    "template": 5,
    "template_name": "Page Hero Template",
    "template_key": "page-hero",
    "template_role": "body",
    "template_type": "page"
  }
]
```

#### Create Post Type Template
```http
POST /posts/post-type-templates/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "post_type": 1,
  "theme": 2,
  "template": 5
}
```

**Response:**
```json
{
  "id": 1,
  "store": 1,
  "post_type": 1,
  "post_type_name": "Page",
  "theme": 2,
  "theme_name": "Default Theme",
  "template": 5,
  "template_name": "Page Hero Template",
  "template_key": "page-hero",
  "template_role": "body",
  "template_type": "page"
}
```

#### Get Post Type Template
```http
GET /posts/post-type-templates/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Post Type Template
```http
PATCH /posts/post-type-templates/{id}/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "template": 6
}
```

#### Delete Post Type Template
```http
DELETE /posts/post-type-templates/{id}/
Authorization: Bearer {token}
Store: 1
```

### Post Metadata

#### Get Post Metadata
```http
GET /posts/posts/{post_id}/meta/
Authorization: Bearer {token}
Store: 1
```

#### Add Post Metadata
```http
POST /posts/posts/{post_id}/meta/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "key": "custom_field",
  "value": {"nested": "data"}
}
```

#### Update Post Metadata
```http
PUT /posts/posts/{post_id}/meta/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "key": "existing_field",
  "value": "updated value"
}
```

#### Delete Post Metadata
```http
DELETE /posts/posts/{post_id}/meta/?key=custom_field
Authorization: Bearer {token}
Store: 1
```

### Categories

#### List Categories
```http
GET /posts/categories/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `parent` (int): Filter by parent category ID
- `search` (string): Search in name, slug, description

#### Create Category
```http
POST /posts/categories/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "name": "Web Development",
  "description": "Frontend and backend development",
  "parent": 1
}
```

#### Get Category
```http
GET /posts/categories/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Category
```http
PATCH /posts/categories/{id}/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "name": "Updated Category Name",
  "is_active": false
}
```

#### Delete Category
```http
DELETE /posts/categories/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Get Posts by Category
```http
GET /posts/categories/{id}/posts/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `post_type_key` (string): Filter by post type key

### Tags

#### List Tags
```http
GET /posts/tags/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `is_active` (boolean): Filter by active status
- `search` (string): Search in name, slug, description

#### Create Tag
```http
POST /posts/tags/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "name": "Beginner Friendly",
  "description": "Suitable for beginners"
}
```

#### Get Tag
```http
GET /posts/tags/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Tag
```http
PATCH /posts/tags/{id}/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "name": "Advanced",
  "description": "For experienced users"
}
```

#### Delete Tag
```http
DELETE /posts/tags/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Get Posts by Tag
```http
GET /posts/tags/{id}/posts/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `post_type_key` (string): Filter by post type key

### Comments

#### List Comments
```http
GET /posts/comments/
Authorization: Bearer {token}
Store: 1
```

**Query Parameters:**
- `post` (int): Filter by post ID
- `user` (int): Filter by user ID
- `parent` (int): Filter by parent comment ID
- `is_approved` (boolean): Filter by approval status
- `is_public` (boolean): Filter by public status

#### Create Comment
```http
POST /posts/comments/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "post": 1,
  "content": "This is a great article!",
  "is_approved": true,
  "is_public": true
}
```

#### Get Comments for Post
```http
GET /posts/comments/by_post/?post=1
Authorization: Bearer {token}
Store: 1
```

#### Create Reply
```http
POST /posts/comments/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "store": 1,
  "post": 1,
  "parent": 1,
  "content": "I agree with this comment!",
  "is_approved": true,
  "is_public": true
}
```

#### Get Comment
```http
GET /posts/comments/{id}/
Authorization: Bearer {token}
Store: 1
```

#### Update Comment
```http
PATCH /posts/comments/{id}/
Authorization: Bearer {token}
Store: 1
Content-Type: application/json

{
  "content": "Updated comment content",
  "is_approved": false
}
```

#### Delete Comment
```http
DELETE /posts/comments/{id}/
Authorization: Bearer {token}
Store: 1
```

## Permissions

- All endpoints require authentication (`IsAuthenticated`) AND a `Store` header
- **Store Header Required**: All endpoints return `400 Bad Request` with `{"store": "This field is required."}` if the `Store` header is missing
- Store scoping: Users can only access posts/post types for stores they have access to
- Future: Implement role-based permissions (admin, editor, contributor)

## Filtering and Searching

### Post Types
- `is_active` (boolean): Filter by active status
- `is_builtin` (boolean): Filter by builtin status
- `search` (string): Search in name, key, description

### Posts
- `post_type` (int): Filter by post type ID
- `post_type_key` (string): Filter by post type key
- `status` (string): Filter by status
- `is_featured` (boolean): Filter by featured status
- `content_type` (string): Filter by content type
- `search` (string): Search in title, slug, excerpt, content
- `ordering`: Order by any field (prefix with `-` for descending)

### Categories
- `is_active` (boolean): Filter by active status
- `parent` (int): Filter by parent category ID
- `search` (string): Search in name, slug, description

### Tags
- `is_active` (boolean): Filter by active status
- `search` (string): Search in name, slug, description

### Comments
- `post` (int): Filter by post ID
- `user` (int): Filter by user ID
- `parent` (int): Filter by parent comment ID
- `is_approved` (boolean): Filter by approval status
- `is_public` (boolean): Filter by public status
- `search` (string): Search in content

## Error Responses

### 400 Bad Request
Missing required parameters or validation errors:
```json
{
  "store": ["This field is required."]
}
```

Or for slug uniqueness validation errors:
```json
{
  "slug": ["A page with this slug already exists for this store."]
}
```

Or for posts:
```json
{
  "slug": ["A post with this slug already exists for this store and post type."]
}
```

Or for template type compatibility errors:
```json
{
  "non_field_errors": ["Template type 'blog' is not compatible with post type 'page'. Template type must be 'page' or 'any'."]
}
```

### 401 Unauthorized
Authentication required:
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
Insufficient permissions:
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
Resource not found:
```json
{
  "detail": "Not found."
}
```

## Examples

### Creating a Blog Post with Categories and Tags
```bash
curl -X POST http://localhost:8000/posts/posts/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "post_type": 1,
    "title": "Welcome to Our Blog",
    "content": "<p>This is our first blog post!</p>",
    "status": "published",
    "categories": [1, 2],
    "tags": [1, 3]
  }'
```

### Creating a Category
```bash
curl -X POST http://localhost:8000/posts/categories/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "name": "Technology",
    "description": "Tech-related articles",
    "is_active": true
  }'
```

### Creating a Tag
```bash
curl -X POST http://localhost:8000/posts/tags/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "name": "Tutorial",
    "description": "Step-by-step guides",
    "is_active": true
  }'
```

### Creating a Comment
```bash
curl -X POST http://localhost:8000/posts/comments/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "post": 1,
    "content": "Great article! Very helpful.",
    "is_approved": true,
    "is_public": true
  }'
```

### Creating a Reply
```bash
curl -X POST http://localhost:8000/posts/comments/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "post": 1,
    "parent": 1,
    "content": "I agree with this comment!",
    "is_approved": true,
    "is_public": true
  }'
```

### Listing Posts by Category
```bash
curl "http://localhost:8000/posts/categories/1/posts/" \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1"
```

### Listing Posts by Tag
```bash
curl "http://localhost:8000/posts/tags/1/posts/" \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1"
```

### Getting Comments for a Post
```bash
curl "http://localhost:8000/posts/comments/by_post/?post=1" \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1"
```

### Creating a Page
```bash
curl -X POST http://localhost:8000/posts/pages/ \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "store": 1,
    "title": "Contact Us",
    "content": "<p>Get in touch with us.</p>",
    "status": "published"
  }'
```

### Listing Published Posts
```bash
curl "http://localhost:8000/posts/posts/published/" \
  -H "Authorization: Bearer {token}" \
  -H "Store: 1"
```

### Frontend Integration
```javascript
// Fetch published posts for a store
const response = await fetch('/posts/posts/published/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Store': '1',
    'Content-Type': 'application/json'
  }
});
const posts = await response.json();

// Create a new post with categories and tags
const newPost = await fetch('/posts/posts/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Store': '1',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    store: 1,
    post_type: 1,
    title: 'New Post',
    content: '<p>Post content</p>',
    status: 'draft',
    categories: [1, 2],
    tags: [3, 4]
  })
});

// Add a comment to a post
const comment = await fetch('/posts/comments/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Store': '1',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    store: 1,
    post: 1,
    content: 'Great post!',
    is_approved: true,
    is_public: true
  })
});

// Fetch categories for a store
const categories = await fetch('/posts/categories/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Store': '1'
  }
});

// Fetch tags for a store
const tags = await fetch('/posts/tags/', {
  headers: {
    'Authorization': `Bearer ${token}`,
    'Store': '1'
  }
});
```
