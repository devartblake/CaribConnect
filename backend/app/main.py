import logging
import sys

import json_log_formatter  # For structured logging in JSON format
import sentry_sdk
from fastapi import Depends, FastAPI, HTTPException
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.security import authenticate_user, create_access_token, decode_token


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"

if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    # Optionally, initialize resources
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # Optionally, close resources
    pass

# Optional: If you need to expose Celery info
# @app.get("/celery-status/")
# def get_celery_status():
#     return {"status": "celery is running"}

# Log formatter for JSON logs
formatter = json_log_formatter.JSONFormatter()

json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(formatter)

app_logger = logging.getLogger(__name__)
app_logger.addHandler(json_handler)
app_logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    app_logger.info({
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
    })
    return response

@app.get("/", tags=["/"])
async def root():
    return {"message": "Logging with Elasticsearch, Kibana, and Filebeat"}

@app.post("/token", tags=["token"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/me", tags=["me"])
async def read_users_me(token: str):
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"user": user}

app.include_router(api_router, prefix=settings.API_V1_STR)
