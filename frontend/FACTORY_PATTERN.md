# Factory Pattern Implementation - Streamlit Pages

## Before: If/Else Routing (14 lines)

```python
# Authentication Pages
if not is_logged_in() and page == "🔑 Login":
    render_login_page()

elif not is_logged_in() and page == "📝 Register":
    render_register_page()

# Patient Pages
if  page == "💬 Book via Chat":
    render_patient_chat_page()

elif not is_logged_in():
    st.info("👈 Please login or register to get started.")
```

**Problems:**
- ❌ Repeating conditions (`if not is_logged_in()`)
- ❌ Hard to add new pages
- ❌ Logic scattered across file
- ❌ Difficult to maintain
- ❌ No centralized access control

---

## After: Factory Pattern (6 lines)

```python
# Try to render the selected page
if page:
    page_rendered = render_page(page)
    
    if not page_rendered:
        if is_logged_in():
            st.error(f"❌ Access denied to page: {page}")
        else:
            st.info("👈 Please login or register to get started.")
else:
    st.info("👈 Please login or register to get started.")
```

**Benefits:**
- ✅ Clean, simple, readable
- ✅ Centralized page registration
- ✅ Built-in access control
- ✅ Easy to add/remove pages
- ✅ Role-based authorization
- ✅ No code duplication

---

## How It Works

### Page Registration (automatic in PageFactory)

```python
self.register_page(
    "💬 Book via Chat",
    render_patient_chat_page,
    requires_auth=True,
    allowed_roles=["patient"]
)
```

### Access Control Flow

```
User clicks page
    ↓
Factory checks if page exists
    ↓
Factory checks if user is authenticated (if required)
    ↓
Factory checks if user's role is allowed
    ↓
If all checks pass → Page renders
If any check fails → Access denied
```

---

## Usage Examples

### Adding a New Page

**Before (modify main app):**
```python
elif st.session_state.role == "doctor" and page == "📊 Analytics":
    render_doctor_analytics()
```

**After (just register it):**
```python
register_page(
    "📊 Analytics",
    render_doctor_analytics,
    requires_auth=True,
    allowed_roles=["doctor"]
)
```

### Custom Page Access Control

```python
register_page(
    "🔐 Admin Panel",
    render_admin_panel,
    requires_auth=True,
    allowed_roles=["admin"]  # Only admins can access
)
```

### Public Pages

```python
register_page(
    "📖 Help",
    render_help_page,
    requires_auth=False  # Anyone can access
)
```

---

## Architecture

### PageHandler Class

Represents a single page with:
- `name`: Page identifier
- `render_func`: Function to render
- `requires_auth`: Authentication requirement
- `allowed_roles`: Role-based access control
- `can_access()`: Check current user access
- `render()`: Render the page

### PageFactory Class

Manages all pages:
- `register_page()`: Add new page
- `get_page()`: Retrieve page by name
- `render_page()`: Render if accessible
- `get_accessible_pages()`: List user's allowed pages
- `_register_default_pages()`: Initialize all default pages

### Global Functions

```python
render_page(page_name)        # Render with factory
register_page(...)            # Register new page
get_page_factory()            # Get factory instance
```

---

## Comparison Table

| Aspect | If/Else | Factory |
|--------|---------|---------|
| **Lines of Code** | 14 | 6 |
| **Adding New Page** | 5+ lines | 1 register call |
| **Access Control** | Inline | Centralized |
| **Scalability** | Poor | Excellent |
| **Maintainability** | Hard | Easy |
| **Testing** | Difficult | Simple |
| **Code Reuse** | Low | High |
| **Readability** | Complex | Clear |

---

## Current Pages Registered

### Authentication
- 🔑 Login (no auth required)
- 📝 Register (no auth required)

### Patient Pages
- 💬 Book via Chat (auth + patient role)
- 📋 My Appointments (auth + patient role)
- ⭐ Leave Feedback (auth + patient role)

### Doctor Pages
- 📅 My Schedule (auth + doctor role)

### Nurse Pages
- 📅 Appointments (auth + nurse role)

---

## Design Patterns Used

1. **Factory Pattern** - `PageFactory` creates and manages page instances
2. **Strategy Pattern** - Each page has its own render strategy
3. **Builder Pattern** - PageHandler builds page configuration
4. **Role-Based Access Control** - Permission checking is responsibility of PageHandler

---

## Future Enhancements

```python
# Add middleware for logging
# Add caching for page rendering
# Add dynamic page loading
# Add page templates
# Add permission decorators
```
