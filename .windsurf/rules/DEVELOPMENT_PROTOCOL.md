---
trigger: always_on
---
# DFCMS Development Protocol

## 🔄 1. Atomic Commits

### Commit Message Format
```
[Module] Brief description

Detailed explanation if needed:
- What was changed
- Why it was changed
- Any breaking changes
- Related issues

Closes #123
```

### Examples
```
[Theme/Layout] Add default header template

- Added header_template field to Layout model
- Created default header template with navigation
- Added migration for new field
- Updated LayoutService to handle header rendering

Closes #45

[Theme/Template] Add template_role validation

- Added template_role choices (body, header, footer, partial)
- Added validation in clean() method
- Updated serializer with role constraints
- Added tests for role validation

Closes #46
```

### One Task Per Commit
- ✅ Good: Single model change
- ✅ Good: Single API endpoint
- ❌ Bad: Model + API + Tests in one commit
- ❌ Bad: Multiple unrelated features

### Branch Strategy
```
main (production)
├── develop (staging)
├── feature/theme-layout-system
├── feature/ecommerce-cart
└── hotfix/security-patch
```

## 🔍 2. Code Review Checklist

### Before Submitting PR
- [ ] Code follows project standards
- [ ] All tests pass locally
- [ ] Documentation updated
- [ ] No TODO/FIXME comments
- [ ] No hardcoded values
- [ ] Proper error handling
- [ ] Input validation
- [ ] Security considerations

### Review Focus Areas

#### Model Relationships
```python
# Check these patterns:
class Layout(models.Model):
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    header_template = models.ForeignKey(
        Template, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='layout_headers'
    )
    
# Verify:
- ✓ Correct on_delete behavior
- ✓ Related names are descriptive
- ✓ Null/blank appropriate
- ✓ Indexes on foreign keys
```

#### Template Render Pipeline
```python
# Check rendering logic:
def render_page(page, layout=None):
    if layout is None:
        layout = page.theme.default_layout
    
    context = {
        'page': page,
        'layout': layout,
        'request': request
    }
    
    return render_to_string('themes/page.html', context)

# Verify:
- ✓ Fallback logic exists
- ✓ Context is complete
- ✓ Template path is correct
- ✓ Error handling
```

#### Default/Fallback Logic
```python
# Check fallback chains:
def get_template_for_role(layout, role):
    # 1. Try layout-specific template
    template = getattr(layout, f'{role}_template')
    if template:
        return template
    
    # 2. Try theme default
    template = layout.theme.templates.filter(
        role=role, 
        is_default=True
    ).first()
    if template:
        return template
    
    # 3. Use system default
    return Template.objects.get(
        role=role, 
        is_system=True
    )

# Verify:
- ✓ Multiple fallback levels
- ✓ System defaults exist
- ✓ Graceful degradation
```

#### Naming & Consistency
- Models: PascalCase (Layout, Template)
- Fields: snake_case (header_template, created_at)
- Methods: snake_case (get_default_layout)
- Classes: PascalCase (LayoutService)
- Constants: UPPER_SNAKE_CASE (TEMPLATE_ROLES)

## 🧪 3. Post-Code-Update Protocol

### Immediate Actions After Code Update

#### 1. Run Tests
```bash
# Run all tests
python manage.py test

# Run specific module
python manage.py test themes.tests

# Run with coverage
coverage run --source='.' manage.py test
coverage report
```

#### 2. Update STATUS.md
```markdown
# Before
| Layout resolution logic | You | ⬜ Pending | Layout model |

# After
| Layout resolution logic | You | ✅ Done | Layout model | Added fallback logic, tests pass |
```

#### 3. Document Issues in TEST_LOG.md
```markdown
## 2024-01-23 - Layout Resolution Tests

### Issues Found
- [⚠️] Template variable not rendering in header
- [✅] Default layout fallback working
- [⚠️] Performance issue with nested templates

### Fixes Applied
- Fixed variable context passing
- Added template caching
- Optimized database queries

### Test Results
- Unit Tests: 15/15 passing
- Integration Tests: 8/10 passing
- Performance: Within acceptable limits
```

### Quality Gates
Before marking task as "Done":
- [ ] All tests pass
- [ ] Code coverage ≥ 85%
- [ ] No security vulnerabilities
- [ ] Documentation updated
- [ ] STATUS.md updated
- [ ] TEST_LOG.md updated

## 📝 4. Documentation Standards

### Code Comments
```python
class Layout(models.Model):
    """
    Layout model for page structure composition.
    
    A Layout defines the overall page structure including
    header, footer, and content slots. Each Theme can have
    multiple layouts for different page types.
    
    Attributes:
        theme: The theme this layout belongs to
        name: Human-readable layout name
        header_template: Template for page header
        footer_template: Template for page footer
        content_slots: JSON configuration for content areas
    """
    
    def get_rendered_header(self, context=None):
        """
        Render the header template with given context.
        
        Args:
            context: Template context dictionary
            
        Returns:
            str: Rendered HTML or empty string if no template
            
        Raises:
            TemplateSyntaxError: If template has invalid syntax
        """
        if not self.header_template:
            return ""
            
        return self.header_template.render(context or {})
```

### API Documentation
```python
class LayoutViewSet(TenantViewSet):
    """
    Layout management API endpoints.
    
    Provides CRUD operations for layouts within a store's theme.
    Supports layout creation, updating, and deletion with proper
    validation and permissions.
    """
    
    @extend_schema(
        summary="Create Layout",
        description="Create a new layout for the store's theme",
        responses={201: LayoutSerializer},
        request=CreateLayoutSerializer
    )
    def create(self, request, *args, **kwargs):
        """Create a new layout instance."""
        # Implementation
```

## 🚀 5. Development Workflow

### Daily Workflow
1. **Morning Standup**
   - Review yesterday's progress
   - Plan today's tasks
   - Identify blockers

2. **Development**
   - Pick next task from STATUS.md
   - Check dependencies
   - Write code
   - Write tests
   - Update documentation

3. **End of Day**
   - Commit work
   - Update STATUS.md
   - Note blockers
   - Plan tomorrow

### Task Lifecycle
```
⬜ Pending → 🔄 In Progress → ✅ Review → ✅ Done
                    ↓
                 ⚠️ Blocked
```

### Pull Request Process
1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit PR with description
5. Code review
6. Address feedback
7. Merge to develop
8. Deploy to staging

## 🔧 6. Tools & Configuration

### Required Tools
- **IDE**: VS Code with Python extensions
- **Git**: Version control
- **Docker**: Local development environment
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

### VS Code Settings
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true
}
```

## 📊 7. Performance Guidelines

### Database Optimization
- Use `select_related` for forward relationships
- Use `prefetch_related` for reverse relationships
- Add database indexes on query fields
- Use `bulk_create` for multiple inserts

### Caching Strategy
- Cache frequently accessed data
- Use cache invalidation on updates
- Implement cache warming strategies
- Monitor cache hit rates

### API Performance
- Implement pagination
- Use efficient serializers
- Add rate limiting
- Monitor response times

## 🛡️ 8. Security Guidelines

### Input Validation
- Validate all user inputs
- Sanitize HTML content
- Use parameterized queries
- Implement CSRF protection

### Authentication & Authorization
- Use JWT tokens
- Implement proper permissions
- Secure password storage
- Session management

### Data Protection
- Encrypt sensitive data
- Implement audit logging
- Regular security updates
- Vulnerability scanning
