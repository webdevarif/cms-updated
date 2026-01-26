# 03-Views Rules v1.0

## Authority
- Owner: Ecommerce Lead
- Enforced By: App-level view permissions, service validations, model constraints
- Scope: Application Layer - Ecommerce Module
- Authority Level: APPLICATION RULES
- Core Compliance: Must adhere to @backend/rules/core.md and infrastructure standards
- Infrastructure Dependencies: @backend/rules/cache.md, @backend/rules/search.md

## Purpose
This document defines APPLICATION-LEVEL API endpoints and view implementations for the **ecommerce** module, providing clean V2-only APIs for product management, orders, and customer interactions while leveraging core infrastructure.

---

## Structure
### **Application API Structure**
```python
apps/ecommerce/
├── public/v2/               # Public APIs (no auth required)
│   ├── urls.py             # Public URL patterns
│   ├── views.py            # Public ViewSets
│   └── serializers.py      # Public serializers
├── customer/v2/            # Customer APIs (customer auth required)
│   ├── urls.py             # Customer URL patterns
│   ├── views.py            # Customer ViewSets
│   └── serializers.py      # Customer serializers
└── dashboard/v2/           # Dashboard APIs (staff auth required)
    ├── urls.py             # Dashboard URL patterns
    ├── views.py            # Dashboard ViewSets
    └── serializers.py      # Dashboard serializers
```

---

## Data Model
[Core implementation patterns and code examples]

## Implementation
### **Application API Endpoints**

#### Public Ecommerce Endpoints
```python
GET    /v2/products/              # List products
GET    /v2/products/{id}/         # Get product details
GET    /v2/products/search/       # Search products
GET    /v2/categories/            # List categories
GET    /v2/cart/                  # Get cart (if authenticated)
```

#### Customer Ecommerce Endpoints
```python
GET    /v2/customer/orders/        # List customer orders
GET    /v2/customer/orders/{id}/   # Get order details
POST   /v2/customer/orders/        # Create order
PUT    /v2/customer/orders/{id}/cancel/ # Cancel order
GET    /v2/customer/profile/       # Get customer profile
PUT    /v2/customer/profile/       # Update customer profile
```

#### Dashboard Ecommerce Endpoints
```python
GET    /v2/dashboard/products/     # List all products
POST   /v2/dashboard/products/     # Create product
GET    /v2/dashboard/products/{id}/ # Get product details
PUT    /v2/dashboard/products/{id}/ # Update product
DELETE /v2/dashboard/products/{id}/ # Delete product

GET    /v2/dashboard/orders/       # List all orders
GET    /v2/dashboard/orders/{id}/  # Get order details
PUT    /v2/dashboard/orders/{id}/status/ # Update order status

GET    /v2/dashboard/customers/    # List customers
GET    /v2/dashboard/analytics/    # Sales analytics
```

### **Application ViewSet Examples**

#### Public Product ViewSet
```python
# apps/public/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import AllowAny

class PublicProductViewSet(TenantViewSet):
    """
    Public product catalog endpoints
    No authentication required for browsing products
    """
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(status='published')
    serializer_class = PublicProductSerializer
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get product variants"""
        product = self.get_object()
        variants = product.variants.all()
        serializer = PublicProductVariantSerializer(variants, many=True)
        return Response(serializer.data)
```

#### Customer Order ViewSet
```python
# apps/customer/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsAuthenticated, IsStoreUser

class CustomerOrderViewSet(TenantViewSet):
    """
    Customer order management endpoints
    Requires customer authentication
    """
    permission_classes = [IsAuthenticated, IsStoreUser]
    serializer_class = CustomerOrderSerializer
    
    def get_queryset(self):
        return Order.objects.filter(
            store=self.get_store(),
            customer=self.request.user
        )
    
    def perform_create(self, serializer):
        """Create order with customer assignment"""
        serializer.save(customer=self.request.user)
```

#### Dashboard Product ViewSet
```python
# apps/dashboard/ecommerce/v2/views.py
from core.viewsets import TenantViewSet
from core.permissions import IsAuthenticated, IsStoreStaff

class DashboardProductViewSet(TenantViewSet):
    """
    Dashboard product management endpoints
    Requires staff authentication
    """
    permission_classes = [IsAuthenticated, IsStoreStaff]
    serializer_class = DashboardProductSerializer
    
    def get_queryset(self):
        return Product.objects.filter(store=self.get_store())
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get product analytics"""
        product = self.get_object()
        
        # Calculate analytics
        total_sales = OrderItem.objects.filter(
            product=product,
            order__status__in=['delivered', 'shipped']
        ).aggregate(total=models.Sum('total'))['total'] or 0
        
        return Response({
            'product_id': product.id,
            'total_sales': float(total_sales),
            'total_orders': OrderItem.objects.filter(
                product=product,
                order__status__in=['delivered', 'shipped']
            ).count()
        })
```

---

## Permissions
[Access control rules and authorization matrix]

## Testing
[Testing requirements with code examples]

## Services
[Service classes and methods with interfaces]

## Dependencies
```tree
[Related components with @path references]
```
- core.md for TenantViewSet and permission classes
- search.md for product search functionality
- cache.md for product caching
- notifications.md for order notifications

## Migration
[Upgrade paths from previous versions]

## Benefits
[Value proposition and technical advantages]

---
**Version**: 1.0  
**Last Updated**: 2026-01-26
**Next Review**: 2026-02-25
