# Django CMS with RBAC and API Keys

A clean, minimal Django CMS backend with role-based access control (RBAC) and API key management for multi-tenant store functionality.

## Features

- 🔐 **Authentication**: JWT-based authentication with email/password and social login
- 🏪 **Multi-tenant Stores**: Users can create and manage multiple stores
- 👥 **Role-Based Access Control**: Custom roles with granular permissions per store
- 🔑 **API Key Management**: Store-specific API keys with action-based permissions
- 📊 **Extensible**: Clean architecture for adding new features

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
# At minimum, set:
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 2. Install Dependencies

```bash
# Install Python packages
pip install django djangorestframework djoser django-allauth django-filter
pip install rest-framework-roles djangorestframework-api-key
pip install python-dotenv psycopg2-binary  # or use sqlite by default
```

### 3. Database Setup

```bash
# Create and apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 4. Run Development Server

```bash
python manage.py runserver 8000
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Authentication
- `POST /api/auth/users/` - User registration
- `POST /api/auth/jwt/create/` - JWT login
- `POST /api/token/refresh/` - Refresh JWT token

### Stores
- `GET/POST /api/stores/` - List/create stores
- `GET/PUT/DELETE /api/stores/{id}/` - Store CRUD operations

### Roles (nested under stores)
- `GET/POST /api/stores/{id}/roles/` - List/create store roles
- `GET/PUT/DELETE /api/stores/{id}/roles/{role_id}/` - Role management
- `GET /api/stores/{id}/roles/{role_id}/users/` - Users assigned to role

### User Roles (nested under stores)
- `GET/POST /api/stores/{id}/user-roles/` - List/assign user roles
- `DELETE /api/stores/{id}/user-roles/{user_id}/` - Remove user role

### API Keys (nested under stores)
- `GET/POST /api/stores/{id}/api-keys/` - List/create API keys
- `PUT/DELETE /api/stores/{id}/api-keys/{key_id}/` - API key management
- `POST /api/stores/{id}/api-keys/{key_id}/revoke/` - Revoke API key
- `GET /api/stores/{id}/api-keys/available-actions/` - List available actions

## Available Actions for Roles & API Keys

- `manage_products` - Create, update, delete products
- `view_orders` - View orders and order details
- `manage_orders` - Update order status, process refunds
- `manage_settings` - Store settings, configurations
- `manage_staff` - Assign/remove roles, manage staff
- `view_analytics` - View store analytics and reports
- `manage_content` - Manage pages, blog posts, content
- `view_customers` - View customer information
- `manage_inventory` - Manage stock levels, inventory
- `manage_discounts` - Create and manage discount codes

## Usage Examples

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepass123",
    "re_password": "securepass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/api/auth/jwt/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### 3. Create a Store

```bash
curl -X POST http://localhost:8000/api/stores/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Store",
    "description": "A test store"
  }'
```

### 4. Create a Store Role

```bash
curl -X POST http://localhost:8000/api/stores/1/roles/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Manager",
    "description": "Store manager with product access",
    "actions": ["manage_products", "view_orders", "view_analytics"]
  }'
```

### 5. Create an API Key

```bash
curl -X POST http://localhost:8000/api/stores/1/api-keys/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Integration API Key",
    "actions": ["view_orders", "manage_products"]
  }'
```

## Architecture

### Apps Structure
```
apps/
├── accounts/          # User management, authentication, roles
│   ├── models.py       # User, Store, StoreRole, StoreUserRole, StoreAPIKey
│   ├── views.py        # ViewSets for all account-related endpoints
│   ├── serializers.py   # DRF serializers
│   ├── permissions.py   # Custom permission classes
│   ├── permissions_api_keys.py  # API key permissions
│   ├── roles.py        # Role definitions and checkers
│   └── services/
│       ├── roles.py    # Role management business logic
│       └── auth_service.py  # Authentication helpers
└── stores/            # Store-specific functionality
    ├── models.py       # Store models (if needed)
    ├── views.py        # Store-specific views
    └── urls.py         # Store URL configuration
```

### Key Components

1. **Custom User Model**: Extends Django's AbstractUser with email as username
2. **Store Model**: Multi-tenant store with owner and access control
3. **StoreRole Model**: Custom roles per store with JSONField for actions
4. **StoreUserRole Model**: Links users to stores with specific roles
5. **StoreAPIKey Model**: Store-specific API keys with action permissions

### Permission System

- **Store Owners**: Full access to their stores
- **Role-Based**: Users get permissions based on assigned roles
- **API Keys**: External integrations with restricted permissions
- **Action-Based**: Fine-grained control over specific operations

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Enable debug mode (development only)
- `DB_*`: Database configuration
- `FRONTEND_URL`: Frontend application URL
- `*_CLIENT_ID/SECRET`: OAuth provider credentials

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Superuser Creation
```bash
python manage.py createsuperuser
```

## Production Considerations

1. **Security**: Set `DEBUG=False` and use a strong `SECRET_KEY`
2. **Database**: Use PostgreSQL instead of SQLite
3. **CORS**: Configure allowed origins properly
4. **Rate Limiting**: Implement API rate limiting
5. **HTTPS**: Use SSL in production
6. **Environment Variables**: Never commit `.env` file

## License

This project is licensed under the MIT License.
