from fastapi import APIRouter

from app.services.cache import get_cache, set_cache

router = APIRouter()

@router.get("/service/{service_id}")
async def get_service(service_id: str):
    cached_data = get_cache(f"service:{service_id}")
    if cached_data:
        return cached_data

    # Fetch data from DB here and then cache it
    fetched_data = {"service_id": service_id, "data": "Service Data"}
    set_cache(f"service:{service_id}", fetched_data)
    return fetched_data
