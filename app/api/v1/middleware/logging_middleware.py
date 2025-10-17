from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import json

logger = logging.getLogger("app.middleware.logging")


def _safe_body(body_bytes: bytes) -> str:
    try:
        text = body_bytes.decode("utf-8")
        # Try to pretty-print JSON
        try:
            obj = json.loads(text)
            pretty = json.dumps(obj, ensure_ascii=False)
            # Truncate very large bodies for logs
            return pretty if len(pretty) < 2000 else pretty[:2000] + "...[truncated]"
        except Exception:
            return text if len(text) < 2000 else text[:2000] + "...[truncated]"
    except Exception:
        return "<binary>"


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()

        # Read request body (stream) safely
        body = await request.body()
        # Redact sensitive headers
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "REDACTED"

        request_state = {
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else None,
            "headers": headers,
            "body": _safe_body(body),
        }
        logger.info(f"Incoming request: {request_state}")

        # Call next handler
        response = await call_next(request)

        # Attempt to read response body (may not always be possible)
        resp_body = b""
        try:
            async for chunk in response.body_iterator:
                resp_body += chunk
        except Exception:
            # Some responses (Streaming) might not allow iteration; ignore
            resp_body = b"<streaming>"

        # Recreate response if we captured body so downstream can still send it.
        # Starlette expects an async iterator for response.body_iterator; build one.
        if resp_body:
            async def _aiter():
                yield resp_body

            response.body_iterator = _aiter()

        duration = time.time() - start
        resp_headers = dict(response.headers)
        # redact any set-cookie or auth-like headers in response logs
        for k in list(resp_headers.keys()):
            if k.lower() in ("set-cookie", "authorization"):
                resp_headers[k] = "REDACTED"

        response_state = {
            "status_code": response.status_code,
            "headers": resp_headers,
            "body": _safe_body(resp_body if isinstance(resp_body, (bytes, bytearray)) else str(resp_body)),
            "duration": duration,
        }
        logger.info(f"Outgoing response: {response_state}")

        return response
