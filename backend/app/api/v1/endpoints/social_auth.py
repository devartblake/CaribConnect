from typing import Optional
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from starlette.config import Config
from starlette.responses import RedirectResponse

from app.core.db import get_database_session
from app.core.oauth import oauth
from app.helpers.auth_helpers import (
    create_social_connection,
    create_user,
    get_social_connection,
    get_user_by_email,
)
from app.middleware.authentication import get_current_user
from app.models import User, UserCreate

#from app.schemas import UserPublic  # Assuming you have schemas defined

router = APIRouter()

# Initialize Config to access environment variables
config = Config(".env")

# Middleware should already include SessionMiddleware in main.py


@router.get("/connect/{provider}")
async def connect_social_media(request: Request, provider: str, session: Session = Depends(get_database_session)):
    """Initiate the OAuth2 flow for the given provider."""
    if provider not in ['google', 'facebook', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Redirect URI should match the one registered in oauth.py
    redirect_uri = request.url_for('auth_callback', provider=provider)
    if provider == 'google':
        return await oauth.google.authorize_redirect(request, redirect_uri)
    elif provider == 'facebook':
        return await oauth.facebook.authorize_redirect(request, redirect_uri)
    elif provider == 'github':
        return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/auth/{provider}/callback")
async def auth_callback(request: Request, provider: str, session: Session = Depends(get_database_session)):
    """Handle the OAuth2 callback from the provider."""
    if provider not in ['google', 'facebook', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    try:
        if provider == 'google':
            token = await oauth.google.authorize_access_token(request)
            user_info = await oauth.google.parse_id_token(request, token)
            provider_user_id = user_info['sub']
            email = user_info['email']
            full_name = user_info.get('name', '')
        elif provider == 'facebook':
            token = await oauth.facebook.authorize_access_token(request)
            user_info = await oauth.facebook.parse_id_token(request, token)
            provider_user_id = user_info['id']
            email = user_info.get('email')
            full_name = user_info.get('name', '')
        elif provider == 'github':
            token = await oauth.github.authorize_access_token(request)
            user_info = await oauth.github.parse_id_token(request, token)  # GitHub may not provide ID token
            provider_user_id = user_info.get('id')
            email = user_info.get('email')
            full_name = user_info.get('name', '')

        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by the provider")

        # Check if the social connection already exists
        connection = await get_social_connection(session, provider, str(provider_user_id))

        if connection:
            user = connection.user
        else:
            # Check if a user with this email exists
            user = await get_user_by_email(session, email)
            if not user:
                # Create a new user if not exists
                user_create = UserCreate(
                    email=email,
                    full_name=full_name
                )
                user = await create_user(session, user_create)

            # Create a new social connection
            connection = await create_social_connection(
                session,
                user,
                provider,
                str(provider_user_id),
                token.get('access_token'),
                token.get('refresh_token'),
                token.get('expires_in')
            )

        # Here, you can generate JWT tokens or set session cookies as per your authentication flow
        # For simplicity, we'll redirect to a protected route with a success message

        return RedirectResponse(url="/profile")  # Adjust the redirect as needed

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e}")


@router.delete("/disconnect/{provider}")
async def disconnect_social_media(provider: str, request: Request, session: Session = Depends(get_database_session), user: User = Depends(get_current_user)):
    """Disconnect a social media account from the user's profile."""
    if provider not in ['google', 'facebook', 'github']:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Assuming you have a dependency to get the current authenticated user
    user: User = request.state.user  # Implement authentication middleware to set request.state.user

    connection = await get_social_connection(session, provider, provider_user_id=None)  # Adjust as needed

    if connection and connection.user_id == user.id:
        session.delete(connection)
        session.commit()
        return {"status": "disconnected", "provider": provider}
    else:
        raise HTTPException(status_code=404, detail="Social connection not found")
