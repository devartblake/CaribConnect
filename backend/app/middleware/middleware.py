from fastapi import FastAPI

from app.middleware.geoipMiddleware import GeoIPMiddleware

app = FastAPI()

# Add the GeoUP middleware
app.add_middleware(GeoIPMiddleware)
