"""Page factory for routing and rendering pages with factory pattern."""
import streamlit as st
from typing import Callable, Optional, Tuple
from components.utils import is_logged_in, get_state_manager
from components.auth import render_login_page, render_register_page
from pages_components.patient_chat import render_patient_chat_page
from pages_components.queue_real_time_status import page_dashboard
# from pages_components.patient_appointments import render_patient_appointments_page
# from pages_components.patient_feedback import render_patient_feedback_page
# from pages_components.schedule import render_schedule_page


class PageHandler:
    """Represents a page with its requirements and render function."""
    
    def __init__(self, 
                 name: str,
                 render_func: Callable,
                 requires_auth: bool = False,
                 allowed_roles: Optional[list] = None):
        """
        Initialize page handler.
        
        Parameters
        ----------
        name : str
            Page identifier
        render_func : Callable
            Function to render the page
        requires_auth : bool
            Whether authentication is required
        allowed_roles : Optional[list]
            List of roles allowed to access this page
        """
        self.name = name
        self.render_func = render_func
        self.requires_auth = requires_auth
        self.allowed_roles = allowed_roles
    
    def can_access(self) -> bool:
        """Check if current user can access this page."""
        # Check authentication
        if self.requires_auth and not is_logged_in():
            return False
        
        # Check role-based access
        if self.allowed_roles and is_logged_in():
            state = get_state_manager()
            if state.get('role') not in self.allowed_roles:
                return False
        
        return True
    
    def render(self, *args, **kwargs):
        """Render the page."""
        self.render_func(*args, **kwargs)


class PageFactory:
    """Factory for creating and managing page routing."""
    
    def __init__(self):
        """Initialize page factory."""
        self._pages = {}
        self._register_default_pages()
    
    def _register_default_pages(self):
        """Register all default pages."""
        # Authentication pages (no auth required)
        self.register_page(
            "🔑 Login",
            render_login_page,
            requires_auth=False
        )
        
        self.register_page(
            "📝 Register",
            render_register_page,
            requires_auth=False
        )
        
        # Patient pages (requires auth)
        self.register_page(
            "💬 Book via Chat",
            render_patient_chat_page,
            requires_auth=True,
            allowed_roles=["patient"]
        )

        self.register_page(
            "Live Queue Status 📊",
            page_dashboard,
            requires_auth=True,
            allowed_roles=["patient"]
        )
    
    def register_page(self,
                      page_name: str,
                      render_func: Callable,
                      requires_auth: bool = False,
                      allowed_roles: Optional[list] = None):
        """
        Register a new page.
        
        Parameters
        ----------
        page_name : str
            Page identifier
        render_func : Callable
            Function to render the page
        requires_auth : bool
            Whether authentication is required
        allowed_roles : Optional[list]
            List of roles allowed to access this page
        """
        self._pages[page_name] = PageHandler(
            name=page_name,
            render_func=render_func,
            requires_auth=requires_auth,
            allowed_roles=allowed_roles
        )
    
    def get_page(self, page_name: str) -> Optional[PageHandler]:
        """
        Get a page by name.
        
        Parameters
        ----------
        page_name : str
            Page identifier
        
        Returns
        -------
        Optional[PageHandler]
            Page handler if found, None otherwise
        """
        return self._pages.get(page_name)
    
    def render_page(self, page_name: str, *args, **kwargs) -> bool:
        """
        Render a page if it exists and user has access.
        
        Parameters
        ----------
        page_name : str
            Page identifier
        *args, **kwargs
            Arguments to pass to render function
        
        Returns
        -------
        bool
            True if page was rendered, False otherwise
        """
        page = self.get_page(page_name)
        
        if not page:
            return False
        
        if not page.can_access():
            return False
        
        # Pass role for schedule page
        if page_name in ("📅 My Schedule", "📅 Appointments"):
            state = get_state_manager()
            page.render(state.get('role'))
        else:
            page.render(*args, **kwargs)
        
        return True
    
    def get_all_pages(self) -> list:
        """Get all registered page names."""
        return list(self._pages.keys())
    
    def get_accessible_pages(self) -> list:
        """Get all pages accessible by current user."""
        return [
            page_name for page_name, page in self._pages.items()
            if page.can_access()
        ]


# Global factory instance
_page_factory = PageFactory()


def get_page_factory() -> PageFactory:
    """Get global page factory instance."""
    return _page_factory


def render_page(page_name: str, *args, **kwargs) -> bool:
    """
    Render a page using the factory.
    
    Parameters
    ----------
    page_name : str
        Page identifier
    *args, **kwargs
        Arguments to pass to render function
    
    Returns
    -------
    bool
        True if page was rendered, False otherwise
    """
    factory = get_page_factory()
    return factory.render_page(page_name, *args, **kwargs)


def register_page(page_name: str,
                  render_func: Callable,
                  requires_auth: bool = False,
                  allowed_roles: Optional[list] = None):
    """
    Register a new page with the factory.
    
    Parameters
    ----------
    page_name : str
        Page identifier
    render_func : Callable
        Function to render the page
    requires_auth : bool
        Whether authentication is required
    allowed_roles : Optional[list]
        List of roles allowed to access this page
    """
    factory = get_page_factory()
    factory.register_page(page_name, render_func, requires_auth, allowed_roles)
