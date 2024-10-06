from app.models import UserBase
from app.services.geoip_service import geocode_address, get_location_by_ip


def get_user_location(ip_address: str, user: UserBase) -> dict | None:
    """Get user location based on IP address and user-provided address."""
    # First, check if the user has provided an address with valid latitude and longitude
    if user.latitude and user.longitude:
        return {
            "latitude": user.latitude,
            "longitude": user.longitude,
            "source": "user_address",
        }

    # If latitude/longitude are not provided, try geocoding the address
    if user.address_line_1 and user.city and user.country:
        location_data = geocode_address({
            "address_line_1": user.address_line_1,
            "city": user.city,
            "state": user.state,
            "country": user.country,
            "postal_code": user.postal_code,
        })
        if location_data:
            return {
                "latitude": location_data['latitude'],
                "longitude": location_data['longitude'],
                "formatted_address": location_data['formatted_address'],
                "source": "geocoded_address",
            }

    # Fallback to IP-based geolocation
    location_data = get_location_by_ip(ip_address)
    if location_data:
        return {
            "latitude": location_data['latitude'],
            "longitude": location_data['longitude'],
            "city": location_data['city'],
            "country": location_data['country'],
            "source": "ip_address",
        }

    return None
