"""API Routes definition for RapidAPI Scrapers Hub."""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models import (
    HealthResponse,
    TikTokTopAdsResponse,
    ShopeePricingResponse,
    B2BLeadsResponse,
    ErrorResponse,
)
from app.services import (
    TikTokAdsService,
    ShopeePricingService,
    B2BLeadsService,
)

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check & System Status",
    description="Returns service availability, active version, current timestamp, and registered endpoints.",
)
async def health_check() -> HealthResponse:
    """Retrieve operational status of the Scrapers Hub."""
    return HealthResponse(
        status="healthy",
        service="rapidapi-scrapers-hub",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        endpoints_available=[
            "/health",
            "/api/v1/tiktok/top-ads",
            "/api/v1/shopee/pricing",
            "/api/v1/b2b/leads",
        ],
    )


@router.get(
    "/api/v1/tiktok/top-ads",
    response_model=TikTokTopAdsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"description": "Pydantic validation failure"},
    },
    tags=["TikTok Ads"],
    summary="Discover TikTok Top Performing Ads",
    description=(
        "Extract high-converting TikTok Top Ad creatives with full engagement metrics (CTR, CVR, likes, shares), "
        "landing page destinations, and video assets across multiple countries and vertical industries."
    ),
)
async def get_tiktok_top_ads(
    country: str = Query(
        "US",
        min_length=2,
        max_length=5,
        description="2-letter ISO country code (e.g. US, VN, SG, GB, ID, TH, MY)",
        examples=["US"],
    ),
    industry: Optional[str] = Query(
        None,
        description="Industry filter (e.g. Beauty & Personal Care, Electronics, Fashion, E-Commerce, App & Games)",
        examples=["Beauty & Personal Care"],
    ),
    objective: Optional[str] = Query(
        None,
        description="Campaign objective (e.g. Conversions, Traffic, Lead Generation, Reach)",
        examples=["Conversions"],
    ),
    period: int = Query(
        30,
        ge=7,
        le=180,
        description="Lookback window in days (7, 30, or 180)",
        examples=[30],
    ),
    sort_by: str = Query(
        "like",
        pattern="^(like|ctr|cvr|shares|impressions)$",
        description="Rank sorting criteria: 'like', 'ctr', 'cvr', 'shares', 'impressions'",
        examples=["like"],
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Results per page (min: 1, max: 50)",
        examples=[10],
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page index offset (min: 1)",
        examples=[1],
    ),
) -> TikTokTopAdsResponse:
    """Query top performing TikTok ads with CTR, CVR, and creative metadata."""
    return await TikTokAdsService.get_top_ads(
        country=country,
        industry=industry,
        objective=objective,
        period=period,
        sort_by=sort_by,
        limit=limit,
        page=page,
    )


@router.get(
    "/api/v1/shopee/pricing",
    response_model=ShopeePricingResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid price boundary filter"},
        422: {"description": "Pydantic validation failure"},
    },
    tags=["Shopee E-Commerce"],
    summary="Scrape Shopee SEA Product Pricing & Benchmarks",
    description=(
        "Scrape real-time product prices, historical sales velocity, review ratings, and discount rates "
        "across Southeast Asian Shopee marketplaces (Vietnam, Singapore, Malaysia, Thailand, Philippines, Indonesia)."
    ),
)
async def get_shopee_pricing(
    query: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Target search keywords (e.g. 'wireless headphones', 'skincare serum')",
        examples=["wireless headphones"],
    ),
    country: str = Query(
        "VN",
        min_length=2,
        max_length=5,
        description="Shopee SEA country code: VN, SG, MY, TH, PH, ID, BR",
        examples=["VN"],
    ),
    sort_by: str = Query(
        "sales",
        pattern="^(sales|relevance|price_asc|price_desc|rating)$",
        description="Sort ranking: 'sales', 'relevance', 'price_asc', 'price_desc', 'rating'",
        examples=["sales"],
    ),
    min_price: Optional[float] = Query(
        None,
        ge=0,
        description="Minimum price threshold in target market currency",
        examples=[100000.0],
    ),
    max_price: Optional[float] = Query(
        None,
        ge=0,
        description="Maximum price threshold in target market currency",
        examples=[2000000.0],
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Results per page (min: 1, max: 50)",
        examples=[10],
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page index offset (min: 1)",
        examples=[1],
    ),
) -> ShopeePricingResponse:
    """Query Shopee product listings with benchmark analytics and price distribution."""
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parameter 'min_price' cannot be greater than 'max_price'.",
        )

    return await ShopeePricingService.get_pricing(
        query=query,
        country=country,
        sort_by=sort_by,
        min_price=min_price,
        max_price=max_price,
        limit=limit,
        page=page,
    )


@router.get(
    "/api/v1/b2b/leads",
    response_model=B2BLeadsResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query parameters"},
        422: {"description": "Pydantic validation failure"},
    },
    tags=["B2B Local Leads"],
    summary="Extract Local B2B Business Leads & Contact Info",
    description=(
        "Discover targeted local commercial leads filtered by niche and geography. "
        "Extracts phone numbers, verified emails, domains, social profiles, review ratings, and coordinates."
    ),
)
async def get_b2b_leads(
    query: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Business industry or specialty keywords (e.g. 'marketing agency', 'dental clinic')",
        examples=["marketing agency"],
    ),
    location: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Target city or metro region (e.g. 'Ho Chi Minh City', 'Austin, TX', 'Singapore')",
        examples=["Ho Chi Minh City"],
    ),
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Results per page (min: 1, max: 50)",
        examples=[10],
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page index offset (min: 1)",
        examples=[1],
    ),
    has_website: Optional[bool] = Query(
        None,
        description="Filter for businesses with an active verified website",
        examples=[True],
    ),
    has_phone: Optional[bool] = Query(
        None,
        description="Filter for businesses with a direct phone number",
        examples=[True],
    ),
    min_rating: Optional[float] = Query(
        None,
        ge=0.0,
        le=5.0,
        description="Minimum review rating filter (0.0 - 5.0)",
        examples=[4.5],
    ),
) -> B2BLeadsResponse:
    """Query verified local business leads with contact intelligence."""
    return await B2BLeadsService.get_leads(
        query=query,
        location=location,
        limit=limit,
        page=page,
        has_website=has_website,
        has_phone=has_phone,
        min_rating=min_rating,
    )
