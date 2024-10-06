from fastapi import APIRouter, FastAPI, HTTPException, Request
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.endpoints import (
    graphql,
    items,
    login,
    notifications,
    payments,
    services,
    social_auth,
    users,
    utils,
)
from app.core.db import engine
from app.middleware.geoipMiddleware import GeoIPMiddleware
from app.models import SQLModel

app = FastAPI()

# Define API router
api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])

api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
# api_router.include_router(predictions.router, prefix="/predictions", tags=["predictions"])
# api_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(graphql.router, prefix="/graphql", tags=["graphql"])

# Include social media login router
api_router.include_router(social_auth.router, prefix="/social_auth", tags=["social_auth"])

# Add Session Middleware (required for OAuth)
app.add_middleware(SessionMiddleware, secret_key="SECRET_KEY")  # Replace with your secret key

# Add GeoIP Middleware
app.add_middleware(GeoIPMiddleware)

# Create database tables
def create_tables():
    SQLModel.metadata.create_all(engine)

# Example protected route (ensure authentication middleware sets request.state.user)
@api_router.get("/profile", tags=["profile"])
def get_profile(request: Request):
    user = getattr(request.state, 'user', None)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"email": user.email, "full_name": user.full_name, "social_connections": user.social_connections}
