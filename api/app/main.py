import datetime

from app.core.config import settings
from fastapi import FastAPI

print(datetime.datetime.now())

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)
