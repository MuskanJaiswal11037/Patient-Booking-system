"""Google OAuth integration for authentication."""
import os
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.models import User, Patient
from backend.auth import create_access_token


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

def verify_google_token(token: str) -> dict:
    """
    Verify Google OAuth token and return user info.
    
    Parameters
    ----------
    token : str
        Google ID token from frontend
    
    Returns
    -------
    dict
        User info from Google (email, name, picture, etc.)
    
    Raises
    ------
    HTTPException
        If token is invalid
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth not configured"
        )
    
    try:
        # Verify and decode token
        idinfo = verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        return idinfo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


def handle_google_signin(google_token: str, db: Session) -> dict:
    """
    Handle Google sign-in: create user if needed and return auth token.
    
    Parameters
    ----------
    google_token : str
        Google ID token
    db : Session
        Database session
    
    Returns
    -------
    dict
        Token response with access_token, role, etc.
    """
    # Verify token
    idinfo = verify_google_token(google_token)
    
    email = idinfo.get("email")
    full_name = idinfo.get("name", "")
    picture = idinfo.get("picture", "")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    # Check if user exists
    result = db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user (default as patient)
        user = User(
            email=email,
            password_hash="",  # No password for OAuth users
            full_name=full_name or email.split("@")[0],
            role="patient",
            phone=None,
            is_active=True,
        )
        db.add(user)
        db.flush()
        
        # Create patient profile
        db.add(Patient(
            user_id=user.id,
            date_of_birth=None,
            blood_group=None,
        ))
        db.commit()
    
    # Create access token
    token = create_access_token({"sub": user.id, "role": user.role})
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "full_name": user.full_name,
        "user_id": user.id,
    }
