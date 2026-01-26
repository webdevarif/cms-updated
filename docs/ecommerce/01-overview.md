# Ecommerce Module Rules

## 1. Overview

### 1.1 Purpose
The ecommerce module provides comprehensive product catalog management, shopping cart functionality, order processing, and customer management for multi-tenant stores.

### 1.2 Scope
- Product and variant management
- Shopping cart and checkout
- Order processing and fulfillment
- Customer management
- Discount and coupon system
- Collection management
- Inventory tracking
- Payment integration
- Shipping and tax calculations

### 1.3 Architecture Principles
- **Store-scoped**: All models must have explicit `ForeignKey` to `stores.Store`
- **V2-only**: Clean implementation without legacy compatibility
- **Service layer**: Business logic centralized in `services.py`
- **Auto-logging**: Integration with `logs` app for audit trails
- **Multi-tenant**: Strict data isolation between stores

### 1.4 Directory Structure
```
apps/
├── public/                    # Public APIs (no authentication)
│   └── ecommerce/             # Public ecommerce APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       ├── models/             # Shared models across versions
│       │   ├── __init__.py
│       │   ├── products.py      # Product, ProductVariant, ProductCategory
│       │   ├── cart.py         # Cart, CartItem
│       │   ├── orders.py        # Order, OrderItem
│       │   ├── customers.py    # Customer
│       │   ├── collections.py   # Collection, CollectionCondition
│       │   ├── coupons.py       # CouponCampaign, Coupon
│       │   ├── inventory.py    # Inventory, InventoryTransaction
│       │   └── payments.py     # PaymentMethod, Payment
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── customer/                  # Customer APIs (customer authentication)
│   └── ecommerce/             # Customer ecommerce APIs
│       ├── v2/               # Version 2 (Current Only)
│       │   ├── urls.py
│       │   ├── views.py
│       │   ├── serializers.py
│       │   ├── services.py
│       │   └── tests.py
│       └── models/             # Same shared models
└── dashboard/                 # Dashboard APIs (admin authentication)
    └── ecommerce/             # Dashboard ecommerce APIs
        ├── v2/               # Version 2 (Current Only)
        │   ├── urls.py
        │   ├── views.py
        │   ├── serializers.py
        │   ├── services.py
        │   └── tests.py
        └── models/             # Same shared models
```

### 1.5 Integration Points
- **Media**: Product images, variant images, category images
- **Accounts**: Customer profiles, user management
- **Stores**: Multi-tenant store scoping
- **Logs**: Auto-logging for all ecommerce activities
- **Translations**: Product/content internationalization
- **SMTP**: Order confirmations, notifications

### 1.6 API Versioning
- **V1**: Not implemented (clean V2-only approach)
- **V2**: Current version with full feature set
- **Future**: V3 planned for breaking changes

### 1.7 Security Requirements
- Store isolation mandatory
- Input validation on all endpoints
- Rate limiting on public APIs
- PCI compliance for payment processing
- GDPR compliance for customer data

### 1.8 Performance Requirements
- Optimized database queries with proper indexing
- Caching strategies for product data
- Efficient cart operations
- Scalable inventory management

### 1.9 Testing Requirements
- 95% model coverage
- 90% API endpoint coverage
- 100% service layer coverage
- Integration tests for critical flows

---

## 2. Core Models

### 2.1 Model Inheritance
All ecommerce models must inherit from `TenantModel` for store scoping:

```python
from core.models import TenantModel

class Product(TenantModel):
    # Store-scoped product model
    pass
```
