from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: str | None = None  # User identifier (subject)
    exp: int | None = None  # Expiration time
