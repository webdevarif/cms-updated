---
trigger: always_on
---
# DFCMS Dependency Map

## 🏗️ Core Dependency Flow

```
Stores → Themes → Layout → Template → Rendering → StoreBootstrap
```

### Critical Path Explanation
- **Stores** must exist first (tenant & global users)
- **Themes** are tied to stores
- **Layout** depends on Theme
- **Template** depends on Layout
- **Rendering engine** uses Layout + Template
- **StoreBootstrap** seeds the initial theme/layout/template

⚠️ **If you break this order → integration bugs guaranteed**

## 📊 Detailed Dependency Graph

### Layer 1: Foundation
```
┌─────────────┐
│   Stores    │ ← Base tenant model
└─────────────┘
       ↓
┌─────────────┐
│   Users     │ ← Authentication & permissions
└─────────────┘
```

### Layer 2: Core Services
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Media    │    │    Cache    │    │    Queue    │
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                   ↓                   ↓
┌─────────────────────────────────────────────────┐
│              Search System                      │
└─────────────────────────────────────────────────┘
```

### Layer 3: Content & Presentation
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Themes    │ →  │   Layout    │ →  │  Templates  │
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                   ↓                   ↓
┌─────────────────────────────────────────────────┐
│            Rendering Engine                     │
└─────────────────────────────────────────────────┘
```

### Layer 4: Business Logic
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ E-commerce  │    │   Forms     │    │   Pages     │
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                   ↓                   ↓
┌─────────────────────────────────────────────────┐
│            StoreBootstrap                       │
└─────────────────────────────────────────────────┘
```

### Layer 5: Advanced Features
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Notifications│    │  Webhooks   │    │ Analytics   │
└─────────────┘    └─────────────┘    └─────────────┘
       ↓                   ↓                   ↓
┌─────────────────────────────────────────────────┐
│            Translations                         │
└─────────────────────────────────────────────────┘
```

## 🔗 Cross-Dependencies

### Theme System Dependencies
```
Themes:
├── Stores (tenant)
├── Media (assets)
├── Templates (content)
└── Layout (structure)

Layout:
├── Themes (parent)
├── Templates (header/footer)
└── Pages (overrides)

Templates:
├── Layout (role assignment)
├── Media (assets)
└── Translations (content)
```

### E-commerce Dependencies
```
E-commerce:
├── Stores (tenant)
├── Media (product images)
├── Search (product discovery)
├── Cache (performance)
├── Queue (async processing)
├── Notifications (order updates)
├── Analytics (tracking)
└── Translations (multi-language)
```

## 🚫 Forbidden Implementations

### Never Implement Before Dependencies
1. **Layout before Theme** → No parent relationship
2. **Template before Layout** → Missing role context
3. **StoreBootstrap before all** → Nothing to bootstrap
4. **E-commerce before Media** → No product images
5. **Search before Content** → Nothing to index

### Circular Dependencies to Avoid
```
❌ Themes ↔ Templates (should be Themes → Layout → Templates)
❌ E-commerce ↔ Analytics (should be E-commerce → Analytics)
❌ Notifications ↔ Queue (should be Queue → Notifications)
```

## ✅ Implementation Order Checklist

### Phase 1: Foundation (Week 1-2)
- [ ] Stores model
- [ ] User authentication
- [ ] Media management
- [ ] Cache system
- [ ] Queue system

### Phase 2: Content Layer (Week 3-4)
- [ ] Search system
- [ ] Theme system
- [ ] Layout system
- [ ] Template system
- [ ] Rendering engine

### Phase 3: Business Logic (Week 5-6)
- [ ] Page builder
- [ ] Forms system
- [ ] E-commerce basics
- [ ] StoreBootstrap

### Phase 4: Advanced Features (Week 7-8)
- [ ] Notifications
- [ ] Webhooks
- [ ] Analytics
- [ ] Translations

## 🔍 Dependency Validation

### Before Starting Any Task
1. Check STATUS.md for task status
2. Verify all dependencies are ✅ Done
3. Review DEPENDENCY_MAP.md
4. Confirm no circular dependencies

### After Completing Any Task
1. Run integration tests
2. Update STATUS.md
3. Document any new dependencies
4. Notify dependent task owners

## 📞 Communication Rules

### Dependency Conflicts
- Immediately report to team
- Update STATUS.md with ⚠️ Blocked
- Propose solution or workaround
- Get consensus before proceeding

### Changes to Dependencies
- Document impact analysis
- Update DEPENDENCY_MAP.md
- Notify all affected teams
- Plan migration strategy
