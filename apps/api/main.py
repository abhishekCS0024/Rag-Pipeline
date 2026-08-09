# FastAPI application factory: configures CORS/middleware and registers route routers.
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.middleware.request_id import RequestIdMiddleware
from apps.api.routes import documents, health
from src.shared.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    docs_url="/docs" if settings.enable_api_docs else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.include_router(health.router)
app.include_router(documents.router)
