import logging
import sys

import json_log_formatter  # For structured logging in JSON format
from fastapi import FastAPI

app = FastAPI()

# Log formatter for JSON logs
formatter = json_log_formatter.JSONFormatter()

json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(formatter)

app_logger = logging.getLogger("fastapi_logger")
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

@app.get("/")
async def root():
    return {"message": "Logging with Elasticsearch, Kibana, and Filebeat"}
