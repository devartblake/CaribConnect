from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.helpers.location_helpers import get_user_location
from app.middleware.authentication import get_current_user
from app.models import User


class GeoIPMiddleware(BaseHTTPMiddleware):
    """Middleware for detecting and logging user location based on IP or user address."""

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host

        # Assuming you have some method to get the currently authenticated user
        user: User | None = await get_current_user(request)

        if user:
            location_data = get_user_location(client_ip, user)

            if location_data:
                print(f"User {client_ip} is located in {location_data.get('city', 'unknown')} (source: {location_data['source']})")
                # Attach location data to the request
                request.state.location = location_data

        # Continue processing the request
        response = await call_next(request)
        return response
