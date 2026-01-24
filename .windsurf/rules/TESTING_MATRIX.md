---
trigger: always_on
---
# DFCMS Testing Matrix

## 🎯 Theme System Testing

| Feature | Unit Test | Integration Test | E2E Test | Notes |
| --- | --- | --- | --- | --- |
| Default header/footer | ✅ | ⬜ | ⬜ | Check if all pages without override use default |
| Custom header/footer | ✅ | ⬜ | ⬜ | Page-level override works |
| Template variables | ✅ | ⬜ | ⬜ | Variables render correctly in body |
| Layout + Template render | ⬜ | ⬜ | ⬜ | Full page rendering |
| StoreBootstrap integration | ⬜ | ⬜ | ⬜ | Defaults created on store creation |
| Template validation | ⬜ | ⬜ | ⬜ | Missing variables, syntax errors |
| Layout resolution logic | ⬜ | ⬜ | ⬜ | Fallback to default layout |
| Multi-language support | ⬜ | ⬜ | ⬜ | Translations in templates |

## 🏗️ Core Infrastructure Testing

| Feature | Unit Test | Integration Test | E2E Test | Notes |
| --- | --- | --- | --- | --- |
| Store model | ✅ | ✅ | ⬜ | Multi-tenancy isolation |
| User authentication | ⬜ | ⬜ | ⬜ | JWT tokens, permissions |
| Media upload/download | ⬜ | ⬜ | ⬜ | Cloudflare R2 integration |
| Cache operations | ⬜ | ⬜ | ⬜ | Redis get/set/delete |
| Queue tasks | ⬜ | ⬜ | ⬜ | Celery task execution |
| Search indexing | ⬜ | ⬜ | ⬜ | Elasticsearch sync |

## 🛒 E-commerce Testing

| Feature | Unit Test | Integration Test | E2E Test | Notes |
| --- | --- | --- | --- | --- |
| Product CRUD | ⬜ | ⬜ | ⬜ | Create, read, update, delete |
| Shopping cart | ⬜ | ⬜ | ⬜ | Add/remove items, persistence |
| Checkout flow | ⬜ | ⬜ | ⬜ | Multi-step process |
| Payment processing | ⬜ | ⬜ | ⬜ | Multiple providers |
| Order management | ⬜ | ⬜ | ⬜ | Status updates, tracking |
| Inventory management | ⬜ | ⬜ | ⬜ | Stock levels, reservations |

## 📝 Content Management Testing

| Feature | Unit Test | Integration Test | E2E Test | Notes |
| --- | --- | --- | --- | --- |
| Page builder | ⬜ | ⬜ | ⬜ | Drag & drop functionality |
| Navigation menus | ⬜ | ⬜ | ⬜ | Menu hierarchy, links |
| Blog articles | ⬜ | ⬜ | ⬜ | CRUD, publishing workflow |
| Form submissions | ⬜ | ⬜ | ⬜ | Validation, email notifications |
| SEO metadata | ⬜ | ⬜ | ⬜ | Meta tags, sitemaps |

## 📢 Advanced Features Testing

| Feature | Unit Test | Integration Test | E2E Test | Notes |
| --- | --- | --- | --- | --- |
| Email notifications | ⬜ | ⬜ | ⬜ | SMTP integration |
| Webhook delivery | ⬜ | ⬜ | ⬜ | Event triggers, retries |
| Analytics tracking | ⬜ | ⬜ | ⬜ | Event logging, reports |
| Multi-language | ⬜ | ⬜ | ⬜ | Translation switching |
| API rate limiting | ⬜ | ⬜ | ⬜ | Throttling, abuse prevention |

## 🧪 Test Categories Explained

### Unit Tests
- **Purpose**: Test individual components in isolation
- **Scope**: Models, services, utilities
- **Tools**: pytest, unittest.mock
- **Coverage**: Minimum 80% per module

### Integration Tests
- **Purpose**: Test component interactions
- **Scope**: API endpoints, database operations
- **Tools**: pytest-django, test database
- **Coverage**: Critical user flows

### E2E Tests
- **Purpose**: Test complete user journeys
- **Scope**: Browser automation, full workflows
- **Tools**: Playwright, Selenium
- **Coverage**: Critical business paths

## 📋 Test Requirements

### Theme System Test Cases

#### Layout Model Tests
```python
# Unit Tests
- test_layout_creation_with_theme()
- test_layout_uniqueness_per_theme()
- test_layout_header_footer_templates()
- test_layout_content_slots()
- test_layout_default_fallback()
```

#### Template Model Tests
```python
# Unit Tests
- test_template_role_validation()
- test_template_content_rendering()
- test_template_variable_extraction()
- test_template_layout_relationship()
- test_template_versioning()
```

#### Layout Resolution Tests
```python
# Integration Tests
- test_default_layout_resolution()
- test_page_specific_layout_override()
- test_layout_fallback_chain()
- test_template_role_assignment()
- test_rendering_with_layout()
```

### Store Bootstrap Tests
```python
# Integration Tests
- test_bootstrap_creates_default_theme()
- test_bootstrap_creates_default_layout()
- test_bootstrap_creates_default_templates()
- test_bootstrap_with_custom_initialization()
- test_bootstrap_rollback_on_failure()
```

## 🚨 Test Status Indicators

- ✅ = Tests written and passing
- ⬜ = Tests not yet written
- ⚠️ = Tests written but failing
- 🔄 = Tests in progress

## 📊 Coverage Requirements

### Minimum Coverage by Module
- **Models**: 90%
- **Views/API**: 85%
- **Services**: 95%
- **Utilities**: 80%
- **Overall**: 85%

### Critical Path Coverage
- **Theme System**: 95%
- **E-commerce**: 90%
- **Authentication**: 95%
- **Payment Processing**: 100%

## 🔧 Test Environment Setup

### Required Test Services
- PostgreSQL (test database)
- Redis (cache testing)
- Elasticsearch (search testing)
- Cloudflare R2 mock (media testing)

### Test Data Management
```python
# Fixtures for common test data
@pytest.fixture
def test_store():
    """Create test store with theme"""

@pytest.fixture
def test_user():
    """Create test user with permissions"""

@pytest.fixture
def test_theme():
    """Create test theme with layout"""
```

## 📝 Test Documentation

### Test Case Format
```python
def test_feature_scenario():
    """
    Test: Feature should behave in specific way
    
    Given: Precondition
    When: Action taken
    Then: Expected result
    
    Tags: unit, integration, critical
    """
    # Test implementation
```

### Test Results Tracking
- All test results logged to TEST_LOG.md
- Failed tests create GitHub issues
- Coverage reports uploaded to CI/CD
- Performance benchmarks tracked

## 🔄 Continuous Testing

### Pre-commit Hooks
- Run unit tests on changed files
- Check code coverage
- Lint code quality
- Validate models

### CI/CD Pipeline
- Run full test suite on PR
- Generate coverage reports
- Run security scans
- Performance regression tests

### Staging Environment
- Deploy to staging first
- Run integration tests
- Manual QA verification
- Performance testing
