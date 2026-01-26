# Ecommerce Module Rules

## Overview

This directory contains comprehensive development rules for the ecommerce module in the cms-updated backend project. The ecommerce module provides complete product catalog management, shopping cart functionality, order processing, and customer management for multi-tenant stores.

## File Structure

```
ecommerce/
├── 01-overview.md          # Module overview and architecture
├── 02-models.md            # Core model definitions and relationships
├── 03-views.md             # API endpoints and ViewSets
├── 04-services.md          # Business logic and service layer
├── 05-integration.md       # Integration with other modules
├── 06-security.md          # Security and privacy rules
├── 07-testing.md           # Testing requirements and examples
├── 08-migration.md         # Migration strategy from legacy system
├── 09-improvements.md      # Improvement suggestions for DFCMS
├── 10-ai-guidelines.md     # AI development guidelines
└── README.md               # This file
```

## Key Principles

### Store-Scoped Architecture
- All models must have explicit `ForeignKey` to `stores.Store`
- Data isolation between stores is mandatory
- All ViewSets must inherit from `StoreScopedViewSet`

### V2-Only Implementation
- Clean implementation without legacy compatibility
- Modern Django patterns and best practices
- No backward compatibility concerns

### Service Layer Pattern
- Business logic centralized in `services.py`
- Models only contain data-related logic
- ViewSets handle HTTP concerns only

### Auto-Logging Integration
- All ecommerce activities logged to `logs` app
- Audit trails for all critical operations
- Event-driven architecture for extensibility

## Quick Start

### 1. Model Definitions
See `02-models.md` for complete model definitions including:
- Product and ProductVariant models
- Order and OrderItem models
- Cart and CartItem models
- Customer model linked to GlobalUser
- Collection and Coupon models
- Inventory management models

### 2. API Development
See `03-views.md` for API endpoint patterns:
- StoreScopedViewSet base class
- Product, Order, Cart ViewSets
- Public API endpoints
- Permission and filtering patterns

### 3. Business Logic
See `04-services.md` for service layer implementation:
- ProductService for product operations
- OrderService for order processing
- CartService for cart management
- InventoryService for stock management

### 4. Integration Points
See `05-integration.md` for module integrations:
- Media integration for product images
- Accounts integration for user management
- Stores integration for multi-tenancy
- Logs integration for audit trails
- Translations integration for i18n
- SMTP integration for email notifications

## Development Workflow

### 1. Model Development
```python
# Follow store-scoped pattern
class Product(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    # ... other fields
```

### 2. Service Implementation
```python
# Centralize business logic
class ProductService:
    @staticmethod
    def create_product(store, user, data):
        # Business logic here
        pass
```

### 3. API Development
```python
# Inherit from StoreScopedViewSet
class ProductViewSet(StoreScopedViewSet):
    # API implementation
    pass
```

### 4. Testing
```python
# Comprehensive test coverage
class ProductModelTest(TestCase):
    def test_product_creation(self):
        # Test implementation
        pass
```

## Security Requirements

- Store isolation is mandatory
- Input validation on all endpoints
- Rate limiting on public APIs
- PCI compliance for payment processing
- GDPR compliance for customer data

See `06-security.md` for detailed security guidelines.

## Performance Requirements

- Optimized database queries with proper indexing
- Caching strategies for product data
- Efficient cart operations
- Scalable inventory management

See `07-testing.md` for performance testing requirements.

## Migration Strategy

For migrating from the existing DFCMS ecommerce module, see `08-migration.md` for:
- Legacy data analysis
- Migration phases
- Rollback strategy
- Testing procedures

## AI Development Guidelines

When using AI assistants for ecommerce development, see `10-ai-guidelines.md` for:
- What AI can and cannot do
- Security considerations
- Code quality standards
- Review checklists

## Improvements

For suggested improvements to the existing DFCMS ecommerce module, see `09-improvements.md` for:
- Current issues analysis
- Architecture improvements
- Feature enhancements
- Performance optimizations

## Compliance

This module follows all backend development rules defined in the main `rules.md` file and maintains consistency with other module rules files.

## Support

For questions about ecommerce module development:
1. Check the relevant section in this directory
2. Review the main backend rules
3. Consult with the development team
4. Check existing implementations for patterns

## Version History

- **v1.0**: Initial comprehensive rules documentation
- Based on analysis of existing DFCMS ecommerce module
- Incorporates modern Django best practices
- Includes security and performance considerations
