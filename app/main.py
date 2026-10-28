"""Main FastAPI Application Entrypoint for RapidAPI Scrapers Hub."""
import os
import time
from typing import Callable
from fastapi import FastAPI, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes import router

# API Metadata tailored for RapidAPI Marketplace
API_TITLE = "ScrapersHub API - TikTok Top Ads, Shopee SEA Pricing & B2B Leads"
API_DESCRIPTION = """
# 🚀 RapidAPI Scrapers Hub - Unified Micro-SaaS

The high-performance, real-time scraping and intelligence hub designed for eCommerce operators, 
growth marketers, and lead generation professionals.

### ✨ Key Scraping Capabilities
1. **TikTok Top Ads Intelligence**: Discover high-performing creatives, CTR, CVR, video links, and advertiser benchmarks.
2. **Shopee SEA Pricing & Velocity**: Track competitor pricing, historical sales counts, stock, and seller ratings across Southeast Asia.
3. **B2B Local Commercial Leads**: Extract verified local business leads with direct phone numbers, websites, review ratings, and coordinates.

### 🛡️ Enterprise-Grade Reliability
- Built-in zero-downtime architecture with authentic domain-aware fallbacks.
- Fully compatible with RapidAPI gateway proxy security and rate limiting.
"""

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Response-Time", "X-RapidAPI-Version"],
)


# ---------------------------------------------------------------------------
# RapidAPI Header & Proxy Secret Middleware
# ---------------------------------------------------------------------------
@app.middleware("http")
async def rapidapi_gateway_middleware(request: Request, call_next: Callable) -> Response:
    """Process RapidAPI headers, optional proxy secret verification, and timing."""
    start_time = time.perf_counter()

    # Capture RapidAPI Context Headers
    rapidapi_key = request.headers.get("x-rapidapi-key") or request.headers.get("X-RapidAPI-Key")
    rapidapi_user = request.headers.get("x-rapidapi-user") or request.headers.get("X-RapidAPI-User")
    rapidapi_proxy_secret = (
        request.headers.get("x-rapidapi-proxy-secret")
        or request.headers.get("X-RapidAPI-Proxy-Secret")
    )

    request.state.rapidapi_key = rapidapi_key
    request.state.rapidapi_user = rapidapi_user

    # Optional Proxy Secret Verification (enabled when RAPIDAPI_PROXY_SECRET is set)
    expected_secret = os.getenv("RAPIDAPI_PROXY_SECRET", "").strip()
    bypass_paths = {"/health", "/docs", "/redoc", "/openapi.json"}

    if expected_secret and request.url.path not in bypass_paths:
        if not rapidapi_proxy_secret or rapidapi_proxy_secret != expected_secret:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "success": False,
                    "error": "Forbidden",
                    "detail": "Invalid or missing X-RapidAPI-Proxy-Secret header.",
                    "status_code": 403,
                },
            )

    response = await call_next(request)

    # Attach performance and tracking headers
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    response.headers["X-Response-Time"] = f"{duration_ms}ms"
    response.headers["X-RapidAPI-Version"] = "1.0.0"

    return response


# ---------------------------------------------------------------------------
# Exception Handlers
# ---------------------------------------------------------------------------
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Normalize standard HTTP exceptions to consistent JSON schema."""
    error_title = "Not Found" if exc.status_code == 404 else (
        "Unauthorized" if exc.status_code == 401 else (
            "Forbidden" if exc.status_code == 403 else "HTTP Error"
        )
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": error_title,
            "detail": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Normalize Pydantic request parameter validation errors."""
    error_messages = []
    for error in exc.errors():
        loc = " -> ".join(str(p) for p in error.get("loc", []))
        msg = error.get("msg", "Invalid value")
        error_messages.append(f"{loc}: {msg}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT if hasattr(status, "HTTP_422_UNPROCESSABLE_CONTENT") else 422,
        content={
            "success": False,
            "error": "Validation Error",
            "detail": "; ".join(error_messages),
            "status_code": 422,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all unhandled server error handler."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal Server Error",
            "detail": str(exc),
            "status_code": 500,
        },
    )


# Register all route definitions
app.include_router(router)
