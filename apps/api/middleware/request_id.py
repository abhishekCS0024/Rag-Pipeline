# Middleware that tags each request/response with a correlation ID header for tracing.
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from src.shared.config import get_settings


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        header_name = get_settings().request_id_header
        request_id = request.headers.get(header_name, str(uuid.uuid4()))
        response = await call_next(request)
        response.headers[header_name] = request_id
        return response
