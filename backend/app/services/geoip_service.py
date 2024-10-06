import geoip2.database
import os
import requests

# Path to the GeoLite2 City database
GEOIP_DB_PATH = os.path.join(os.path.dirname(__file__), "data/geoip/GeoLite2-City.mmdb")

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_location_by_ip(ip_address: str) -> dict | None:
    """Get geographical location information from an IP address."""
    try:
        # Open the GeoLite2 database
        with geoip2.database.Reader(GEOIP_DB_PATH) as reader:
            response = reader.city(ip_address)
            location_data = {
                "country": response.country.name,
                "country_iso_code": response.country.iso_code,
                "region": response.subdivisions.most_specific.name,
                "city": response.city.name,
                "postal_code": response.postal.code,
                "latitude": response.location.latitude,
                "longitude": response.location.longitude,
            }
            return location_data
    except geoip2.errors.AddressNotFoundError:
        print(f"IP address {ip_address} not found in GeoIP database.")
        return None
    except Exception as e:
        print(f"Error retrieving location for {ip_address}: {e}")
        return None

def geocode_address(address: dict) -> dict | None:
    """Geocode the user-provided address to latitude and longitude using Google Maps API."""
    if not GOOGLE_MAPS_API_KEY:
        raise ValueError("Google Maps API key not configured.")

    address_str = f"{address['address_line_1']}, {address.get('city', '')}, {address.get('state', '')}, {address['country']}, {address.get('postal_code', '')}"
    try:
        response = requests.get(
            f"https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address_str, "key": GOOGLE_MAPS_API_KEY},
        )
        response_data = response.json()

        if response_data['status'] == 'OK':
            location = response_data['results'][0]['geometry']['location']
            return {
                "latitude": location['lat'],
                "longitude": location['lng'],
                "formatted_address": response_data['results'][0]['formatted_address'],
            }
        else:
            print(f"Error geocoding address: {response_data['status']}")
            return None
    except Exception as e:
        print(f"Error occurred while geocoding address: {e}")
        return None
