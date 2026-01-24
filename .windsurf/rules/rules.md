# CMS-Updated Backend Development Rules v1.0

## 🎯 Purpose

This document defines strict development rules for the CMS-Updated backend to ensure consistency, maintainability, and quality across all code. These rules support all existing DFCMS functionality while enforcing a clean, API-only architecture.

---

## 🏗️ Project Structure v1.0

### **Fixed Directory Structure**
```
cms-updated/backend/
├── core/                       # Main project configuration
│   ├── settings/              # Django settings
│   ├── middleware/            # Custom middleware
│   ├── urls/                  # URL routing
│   ├── libs/                  # Core utilities
│   └── exceptions/            # Custom exceptions
├── apps/                      # All feature apps
│   ├── accounts/              # User management
│   │   ├── v2/                # V2 APIs only
│   │   │   ├── urls.py
│   │   │   ├── views.py
│   │   │   ├── serializers.py
│   │   │   ├── services.py
│   │   │   └── tests.py
│   │   ├── models/            # Shared models
│   │   │   ├── user.py
│   │   │   └── store_user.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── stores/                # Store management
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── ecommerce/             # E-commerce features
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── themes/                # Theme system
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── media/                 # Media management
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── logs/                  # Activity logging
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── metafields/            # Custom fields
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── entities/              # Entity actions
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── giftcards/             # Gift cards
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── forms/                 # Forms system
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   ├── smtp/                  # Email services
│   │   ├── v2/
│   │   ├── models/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── migrations/
│   └── translations/          # Multi-language
│       ├── v2/
│       ├── models/
│       ├── admin.py
│       ├── apps.py
│       └── migrations/
├── services/                  # Shared business logic
│   ├── auth.py
│   ├── email.py
│   ├── payment.py
│   └── media.py
├── manage.py
├── wsgi.py
└── asgi.py
```

---

## 🔧 Multi-Tenant Architecture

### **Store-Scoped Models**
All models must use explicit `store` ForeignKey:

```python
from django.db import models

class Product(models.Model):
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)
    # ... other fields
    
    class Meta:
        indexes = [
            models.Index(fields=['store', 'created_at']),
        ]
```

### **Store Detection**
- URL path: `/store/[slug]/`
- Header: `X-Store-Slug`
- Session: `store_id`

---

## 📋 Development Rules

### **V2 Only Implementation**
- No V1 backward compatibility
- Clean API-only architecture
- Explicit store scoping

### **Model Standards**
- All models have explicit `store` ForeignKey
- Proper indexes for store queries
- Consistent naming conventions

### **API Standards**
- RESTful design
- JWT authentication
- Store context validation
- Proper error handling

---

Last Updated: January 23, 2026
- [ ] Database is accessible
- [ ] Tests can be created
- [ ] Documentation can be generated

### **AI MUST Follow:**
- [ ] Exact folder structure
- [ ] Standard naming conventions
- [ ] Service layer for business logic
- [ ] Base classes for inheritance
- [ ] Proper error handling
- [ ] Comprehensive testing
- [ ] Swagger documentation

---

**🚨 THESE RULES ARE MANDATORY - NO EXCEPTIONS!**

Every command must follow these rules exactly. Any deviation will result in inconsistent code and potential system failures.

**Version: 1.0**  
**Last Updated: 2024-01-22**  
**Next Review: 2024-02-22**
