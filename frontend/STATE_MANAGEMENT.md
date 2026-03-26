# Streamlit State Management Utilities

Complete guide for managing Streamlit session state using the enhanced utilities.

## Core State Functions

### Generic State Management

#### `set_state(key, value)`
Set a single state value.

```python
from components.utils import set_state

# Set individual values
set_state("token", "abc123")
set_state("page_count", 5)
set_state("user_preferences", {"theme": "dark"})
```

#### `set_states(state_dict)`
Set multiple state values at once (batch operation).

```python
from components.utils import set_states

# Set multiple values in one call
set_states({
    "token": "abc123",
    "role": "patient",
    "full_name": "John Doe",
    "user_id": "user-123"
})
```

#### `get_state(key, default=None)`
Safely retrieve state value with optional default.

```python
from components.utils import get_state

# Get with default value
token = get_state("token")
role = get_state("role", default="guest")
chat_count = get_state("chat_count", default=0)
```

#### `state_exists(key)`
Check if a state key exists.

```python
from components.utils import state_exists

if state_exists("token"):
    print("User is logged in")
else:
    print("User is not logged in")
```

#### `clear_state(key)`
Delete a single state value.

```python
from components.utils import clear_state

clear_state("chat_history")
clear_state("temporary_data")
```

#### `clear_states(keys)`
Delete multiple state values.

```python
from components.utils import clear_states

clear_states(["token", "role", "user_id"])
clear_states(["temp_var1", "temp_var2"])
```

#### `reset_state()`
Reset all state to default values.

```python
from components.utils import reset_state

reset_state()  # Back to initial state
```

#### `get_all_state()`
Get dictionary of all state values.

```python
from components.utils import get_all_state

all_state = get_all_state()
print(all_state)
# Output: {
#     "token": "...",
#     "role": "patient",
#     "full_name": "John",
#     "user_id": "...",
#     "chat_history": [...]
# }
```

#### `state_snapshot()`
Get a snapshot of current state (useful for debugging).

```python
from components.utils import state_snapshot

snapshot = state_snapshot()
st.write(snapshot)
# Output: {
#     "token": "abc...",
#     "role": "patient",
#     "is_logged_in": True,
#     "chat_history_length": 5
# }
```

---

## User-Specific State Functions

### `set_user(token, role, full_name, user_id)`
Set complete user information after login.

```python
from components.utils import set_user

set_user(
    token="jwt_token_here",
    role="patient",
    full_name="John Doe",
    user_id="user_123"
)
```

### `is_logged_in()`
Check if user is authenticated.

```python
from components.utils import is_logged_in

if is_logged_in():
    st.success("User is logged in")
else:
    st.info("Please login first")
```

### `get_token()`
Retrieve current authentication token.

```python
from components.utils import get_token

token = get_token()
```

### `get_role()`
Get current user's role.

```python
from components.utils import get_role

role = get_role()
if role == "patient":
    show_patient_dashboard()
elif role == "doctor":
    show_doctor_dashboard()
```

### `logout()`
Clear all user data from session.

```python
from components.utils import logout

if st.button("Logout"):
    logout()
    st.rerun()
```

---

## Chat History Management

### `add_chat_message(role, content)`
Add message to chat history.

```python
from components.utils import add_chat_message

add_chat_message("user", "Hello, how are you?")
add_chat_message("assistant", "I'm doing well, thanks for asking!")
```

### `get_chat_history()`
Retrieve entire chat history.

```python
from components.utils import get_chat_history

history = get_chat_history()
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### `get_last_message()`
Get the most recent message.

```python
from components.utils import get_last_message

last_msg = get_last_message()
if last_msg:
    print(f"Last message: {last_msg['content']}")
```

### `reset_chat_history()`
Clear all chat messages.

```python
from components.utils import reset_chat_history

reset_chat_history()
```

### `clear_chat_history()`
Alternative method to clear chat.

```python
from components.utils import clear_chat_history

if st.button("Clear Chat"):
    clear_chat_history()
    st.rerun()
```

---

## Usage Examples

### Complete Login Flow

```python
from components.utils import set_user, is_logged_in, get_role

# After successful login
response = login_api(email, password)
if response.status_code == 200:
    data = response.json()
    set_user(
        token=data["access_token"],
        role=data["role"],
        full_name=data["full_name"],
        user_id=data["user_id"]
    )
    st.success("Login successful!")
    st.rerun()
```

### Conditional Navigation

```python
from components.utils import is_logged_in, get_role

if is_logged_in():
    role = get_role()
    if role == "patient":
        show_patient_menu()
    elif role == "doctor":
        show_doctor_menu()
else:
    show_login_page()
```

### Chat Interface

```python
from components.utils import (
    get_chat_history,
    add_chat_message,
    reset_chat_history
)

# Display chat history
for msg in get_chat_history():
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Add new message
if user_input := st.chat_input("Type message..."):
    add_chat_message("user", user_input)
    # Process and get response...
    add_chat_message("assistant", response)
    st.rerun()

# Reset button
if st.button("Clear Chat"):
    reset_chat_history()
    st.rerun()
```

### Temporary State Management

```python
from components.utils import set_state, get_state, clear_state

# Store temporary form data
set_state("form_data", {"name": "John", "email": "john@example.com"})

# Retrieve when needed
form_data = get_state("form_data", default={})

# Clear when done
clear_state("form_data")
```

### Debugging State

```python
from components.utils import state_snapshot

# Show debug info
if st.checkbox("Show Debug Info"):
    st.json(state_snapshot())
```

---

## Best Practices

✅ **Do:**
- Use `set_state()` for single values
- Use `set_states()` for multiple values
- Use `get_state()` with defaults for safety
- Clear unused state to avoid memory leaks
- Use `state_snapshot()` for debugging

❌ **Don't:**
- Access `st.session_state` directly (use utils instead)
- Store large objects without cleanup
- Mix state management patterns
- Forget to clear unused state

---

## State Lifecycle

```
1. Initialize
   init_session_state()

2. Set user (after login)
   set_user(token, role, full_name, user_id)

3. Use state throughout app
   get_state(), get_token(), get_role(), etc.

4. Clear state (on logout)
   logout()
   or reset_state()
```

---

## Reference Table

| Function | Purpose | Returns |
|----------|---------|---------|
| `set_state(k, v)` | Set single value | None |
| `set_states(d)` | Set multiple values | None |
| `get_state(k, d)` | Get value safely | Any |
| `state_exists(k)` | Check if exists | bool |
| `clear_state(k)` | Delete single value | None |
| `clear_states(ks)` | Delete multiple | None |
| `reset_state()` | Reset to defaults | None |
| `get_all_state()` | Get all state | Dict |
| `state_snapshot()` | Get debug snapshot | Dict |
| `is_logged_in()` | Check authentication | bool |
| `get_token()` | Get auth token | str |
| `get_role()` | Get user role | str |
| `set_user(...)` | Set user data | None |
| `logout()` | Clear user data | None |
| `add_chat_message(r, c)` | Add chat msg | None |
| `get_chat_history()` | Get all messages | List |
| `get_last_message()` | Get last message | Dict |
| `reset_chat_history()` | Clear chat | None |

---

## Migration from Direct Access

### Before (old way)
```python
st.session_state.token = "abc123"
token = st.session_state.token
if "token" in st.session_state:
    ...
del st.session_state.token
```

### After (new way)
```python
set_state("token", "abc123")
token = get_state("token")
if state_exists("token"):
    ...
clear_state("token")
```

**Benefits:**
- Cleaner code
- Built-in error handling
- Type hints
- Better documentation
- Easier to debug
