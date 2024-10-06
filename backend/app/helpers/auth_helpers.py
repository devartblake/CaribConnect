from typing import Optional

from sqlmodel import Session, select

from app.models import SocialConnection, User, UserCreate


async def get_user_by_email(session: Session, email: str) -> Optional[User]:
    """Retrieve a user by email."""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

async def get_social_connection(session: Session, provider: str, provider_user_id: str) -> Optional[SocialConnection]:
    """Retrieve a social connection by provider and provider user ID."""
    statement = select(SocialConnection).where(
        SocialConnection.provider == provider,
        SocialConnection.provider_user_id == provider_user_id
    )
    connection = session.exec(statement).first()
    return connection

async def create_user(session: Session, user_create: 'UserCreate') -> User:
    """Create a new user."""
    hashed_password = hash_password(user_create.password)  # Implement your password hashing
    user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        full_name=user_create.full_name,
        address_line_1=user_create.address_line_1,
        address_line_2=user_create.address_line_2,
        city=user_create.city,
        state=user_create.state,
        country=user_create.country,
        postal_code=user_create.postal_code,
        latitude=user_create.latitude,
        longitude=user_create.longitude
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

async def create_social_connection(session: Session, user: User, provider: str, provider_user_id: str, access_token: str, refresh_token: Optional[str], expires_in: Optional[int]) -> SocialConnection:
    """Create a new social connection for a user."""
    connection = SocialConnection(
        user_id=user.id,
        provider=provider,
        provider_user_id=provider_user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in
    )
    session.add(connection)
    session.commit()
    session.refresh(connection)
    return connection

def hash_password(password: str) -> str:
    """Hash the password using a secure hashing algorithm."""
    import bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')
