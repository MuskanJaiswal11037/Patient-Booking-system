# Frontend Architecture

This Streamlit application has been refactored into a modular component-based architecture for better maintainability and scalability.

## Directory Structure

```
frontend/
├── streamlit_app.py           # Main entry point (orchestrator)
├── components/                # Reusable utility components
│   ├── __init__.py
│   ├── config.py              # Configuration constants
│   ├── utils.py               # Session state & helper functions
│   ├── api.py                 # API client functions
│   ├── auth.py                # Login & register forms
│   └── sidebar.py             # Sidebar navigation
├── pages_components/          # Page-specific components
│   ├── __init__.py
│   ├── patient_chat.py        # Patient chat interface
│   ├── patient_appointments.py # Patient appointment management
│   ├── patient_feedback.py    # Patient feedback form
│   └── schedule.py            # Doctor/Nurse schedule view
└── ARCHITECTURE.md            # This file
```

## Component Breakdown

### Core Components (`components/`)

#### `config.py`
- **Purpose**: Centralized configuration constants
- **Exports**:
  - `BACKEND_URL`: Backend API endpoint
  - `STATE_KEYS`: Session state default values
  - `ROLE_NAVIGATION`: Role-based navigation options
  - `STATUS_COLORS`: Status color mapping
  - `BLOOD_GROUPS`: Blood group options

#### `utils.py`
- **Purpose**: Session state management and utilities
- **Key Functions**:
  - `init_session_state()`: Initialize session state
  - `is_logged_in()`: Check authentication
  - `set_user()`: Set user info
  - `logout()`: Clear session
  - `add_chat_message()`: Manage chat history

#### `api.py`
- **Purpose**: Backend API communication
- **Key Functions**:
  - `api_request()`: Generic HTTP request handler
  - `login()`: User login
  - `register()`: User registration
  - `send_chat_message()`: Send chat message
  - `get_appointments()`: Fetch appointments
  - `submit_feedback()`: Submit appointment feedback

#### `auth.py`
- **Purpose**: Authentication UI components
- **Functions**:
  - `render_login_page()`: Login form
  - `render_register_page()`: Registration form

#### `sidebar.py`
- **Purpose**: Navigation and user menu
- **Functions**:
  - `render_sidebar()`: Render sidebar with navigation

### Page Components (`pages_components/`)

#### `patient_chat.py`
- **Purpose**: Patient appointment booking via chat
- **Functions**:
  - `render_patient_chat_page()`: Main chat interface
  
#### `patient_appointments.py`
- **Purpose**: View and manage patient appointments
- **Functions**:
  - `render_patient_appointments_page()`: List appointments
  - `_render_appointment_item()`: Single appointment with actions

#### `patient_feedback.py`
- **Purpose**: Submit feedback for completed appointments
- **Functions**:
  - `render_patient_feedback_page()`: Feedback interface
  - `_render_feedback_form()`: Feedback submission form

#### `schedule.py`
- **Purpose**: Doctor/Nurse schedule view
- **Functions**:
  - `render_schedule_page()`: Appointment schedule
  - `_render_grouped_appointments()`: Group by date
  - `_render_appointment_row()`: Single appointment row

## Main App Flow (`streamlit_app.py`)

```
1. Initialize page configuration
2. Initialize session state
3. Render sidebar (returns current page)
4. Route to appropriate component based on:
   - Authentication status
   - User role
   - Selected page
```

## Data Flow

```
User Action
    ↓
Component (e.g., patient_chat.py)
    ↓
API Call (components/api.py)
    ↓
Backend (FastAPI)
    ↓
Response
    ↓
Component updates UI & session state
```

## Usage Example

### Adding a New Page Component

1. Create file `pages_components/new_feature.py`:
```python
def render_new_feature_page():
    """New feature page."""
    st.title("✨ New Feature")
    
    # Your component logic here
```

2. Import in `streamlit_app.py`:
```python
from pages_components.new_feature import render_new_feature_page
```

3. Add routing:
```python
elif page == "✨ New Feature":
    render_new_feature_page()
```

### Adding a New API Function

1. Add to `components/api.py`:
```python
def get_new_data():
    """Fetch new data."""
    return api_request("GET", "/api/new-endpoint")
```

2. Use in components:
```python
from components.api import get_new_data

response = get_new_data()
if response and response.status_code == 200:
    data = response.json()
    # Use data
```

## Benefits of This Architecture

✅ **Modularity**: Each component has single responsibility
✅ **Reusability**: Components can be easily reused
✅ **Testability**: Smaller components are easier to test
✅ **Scalability**: Easy to add new features
✅ **Maintainability**: Clear structure and separation of concerns
✅ **Readability**: Clean, well-documented code

## Key Improvements Over Original

| Aspect | Before | After |
|--------|--------|-------|
| File Size | 400+ lines | ~60 lines (main) |
| Code Duplication | High | Low |
| Testability | Difficult | Easy |
| New Features | Time-consuming | Quick |
| Code Navigation | Challenging | Clear |

## Session State Management

All session state is managed through `components/utils.py`:

```python
# Initialize
init_session_state()

# Check login
if is_logged_in():
    # User is authenticated

# Set user after login
set_user(token, role, full_name, user_id)

# Logout
logout()

# Chat history
add_chat_message(role, content)
get_chat_history()
```

## Error Handling

All API calls include error handling:
- Connection errors → User-friendly error message
- HTTP errors → Display error detail from backend
- Form validation → Client-side validation before submission

## Future Enhancements

- [ ] Add unit tests for components
- [ ] Add integration tests for API calls
- [ ] Add type hints to all functions
- [ ] Add docstrings to all functions
- [ ] Create component testing utilities
- [ ] Add caching for API calls
- [ ] Add logging throughout
