"""Pydantic schemas and models for RapidAPI Scrapers Hub."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class HealthResponse(BaseModel):
    """Health status response schema."""
    status: str = Field(..., description="Service health state", examples=["healthy"])
    service: str = Field(..., description="Service identifier", examples=["rapidapi-scrapers-hub"])
    version: str = Field(..., description="API semantic version", examples=["1.0.0"])
    timestamp: str = Field(..., description="ISO 8601 UTC timestamp", examples=["2026-03-30T12:00:00Z"])
    endpoints_available: List[str] = Field(
        ...,
        description="List of active public endpoints",
        examples=[[
            "/health",
            "/api/v1/tiktok/top-ads",
            "/api/v1/shopee/pricing",
            "/api/v1/b2b/leads"
        ]]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "service": "rapidapi-scrapers-hub",
                "version": "1.0.0",
                "timestamp": "2026-03-30T12:00:00Z",
                "endpoints_available": [
                    "/health",
                    "/api/v1/tiktok/top-ads",
                    "/api/v1/shopee/pricing",
                    "/api/v1/b2b/leads"
                ]
            }
        }
    )


# ---------------------------------------------------------------------------
# TikTok Models
# ---------------------------------------------------------------------------

class TikTokAdItem(BaseModel):
    """Individual TikTok Top Ad performance item."""
    ad_id: str = Field(..., description="Unique ad creative ID", examples=["tt_ad_9842103"])
    title: str = Field(..., description="Ad caption or creative headline", examples=["Viral Lip Gloss Plumper - 50% Off Today!"])
    advertiser_name: str = Field(..., description="Brand or advertiser name", examples=["GlowCosmetics Official"])
    industry: str = Field(..., description="Vertical industry category", examples=["Beauty & Personal Care"])
    country: str = Field(..., description="Target 2-letter country ISO code", examples=["US"])
    objective: str = Field(..., description="Campaign objective", examples=["Conversions"])
    ctr: float = Field(..., description="Click-Through Rate percentage (%)", examples=[3.85])
    cvr: float = Field(..., description="Conversion Rate percentage (%)", examples=[2.14])
    likes: int = Field(..., description="Total likes count", examples=[124500])
    comments: int = Field(..., description="Total comments count", examples=[3420])
    shares: int = Field(..., description="Total shares count", examples=[8900])
    video_duration: int = Field(..., description="Video length in seconds", examples=[23])
    landing_page_url: str = Field(..., description="Target landing page or product URL", examples=["https://brand.com/products/lip-gloss"])
    video_url: str = Field(..., description="Direct video preview URL", examples=["https://v16-webapp-prime.tiktokcdn.com/sample_ad_9842103.mp4"])
    cover_image_url: str = Field(..., description="Creative thumbnail image URL", examples=["https://p16-sign.tiktokcdn-us.com/sample_cover_9842103.jpg"])
    publish_date: str = Field(..., description="Ad first seen date in ISO format", examples=["2026-03-24T08:15:00Z"])
    tags: List[str] = Field(default_factory=list, description="Associated creative tags", examples=[["beauty", "lipgloss", "fyp", "sale"]])


class TikTokTopAdsResponse(BaseModel):
    """TikTok Top Ads query response schema."""
    success: bool = Field(True, description="Query execution status")
    total: int = Field(..., description="Total matching creative records", examples=[45])
    page: int = Field(..., description="Current page number", examples=[1])
    limit: int = Field(..., description="Items per page", examples=[10])
    country: str = Field(..., description="Country queried", examples=["US"])
    industry: Optional[str] = Field(None, description="Industry filter applied", examples=["Beauty & Personal Care"])
    objective: Optional[str] = Field(None, description="Objective filter applied", examples=["Conversions"])
    period_days: int = Field(..., description="Lookback time window in days", examples=[30])
    data: List[TikTokAdItem] = Field(..., description="List of top performing ad creatives")


# ---------------------------------------------------------------------------
# Shopee Models
# ---------------------------------------------------------------------------

class ShopeeProductItem(BaseModel):
    """Shopee SEA e-commerce product pricing item."""
    item_id: str = Field(..., description="Shopee item ID", examples=["21495830112"])
    shop_id: str = Field(..., description="Shopee shop ID", examples=["84920194"])
    name: str = Field(..., description="Product title", examples=["Anker Soundcore Space One Active Noise Cancelling Headphones"])
    price: float = Field(..., description="Current listed price in local currency", examples=[1890000.0])
    original_price: Optional[float] = Field(None, description="Strikethrough original price", examples=[2490000.0])
    currency: str = Field(..., description="3-letter ISO currency code", examples=["VND"])
    discount_percentage: Optional[int] = Field(0, description="Discount percentage off original price", examples=[24])
    rating_star: float = Field(..., description="Average seller rating star (1-5)", examples=[4.88])
    historical_sold: int = Field(..., description="Total units sold all-time", examples=[3420])
    stock: int = Field(..., description="Current stock available", examples=[85])
    shop_location: str = Field(..., description="Province / City of seller warehouse", examples=["TP. Hồ Chí Minh"])
    is_official_shop: bool = Field(..., description="Whether seller is Shopee Mall / Official verified", examples=[True])
    product_url: str = Field(..., description="Full Shopee marketplace URL", examples=["https://shopee.vn/product/84920194/21495830112"])
    image_url: str = Field(..., description="Product high-resolution image URL", examples=["https://cf.shopee.vn/file/vn-11134207-7r98o-lsi3jkl91.jpg"])


class ShopeePricingResponse(BaseModel):
    """Shopee SEA Pricing benchmark response schema."""
    success: bool = Field(True, description="Query execution status")
    query: str = Field(..., description="Keywords searched", examples=["wireless headphones"])
    country: str = Field(..., description="Target Southeast Asian market", examples=["VN"])
    currency: str = Field(..., description="Local currency unit", examples=["VND"])
    total_found: int = Field(..., description="Total matching products identified", examples=[58])
    page: int = Field(..., description="Current page number", examples=[1])
    limit: int = Field(..., description="Returned item count limit", examples=[10])
    average_price: float = Field(..., description="Average price across matching products", examples=[1450000.0])
    min_price: float = Field(..., description="Lowest price among matching products", examples=[650000.0])
    max_price: float = Field(..., description="Highest price among matching products", examples=[2890000.0])
    data: List[ShopeeProductItem] = Field(..., description="List of competitive product pricing items")


# ---------------------------------------------------------------------------
# B2B Leads Models
# ---------------------------------------------------------------------------

class B2BLeadItem(BaseModel):
    """Local business lead item with contact and digital presence info."""
    lead_id: str = Field(..., description="Unique lead identifier", examples=["lead_b2b_77192"])
    business_name: str = Field(..., description="Official business or company name", examples=["Apex Digital Marketing Studio"])
    category: str = Field(..., description="Industry niche or vertical category", examples=["Marketing Agency"])
    address: str = Field(..., description="Physical street address", examples=["128 Nguyen Thi Minh Khai, District 3"])
    city: str = Field(..., description="City or municipality", examples=["Ho Chi Minh City"])
    country: str = Field(..., description="Country code or name", examples=["Vietnam"])
    phone: Optional[str] = Field(None, description="Direct phone contact", examples=["+84 28 3910 8899"])
    email: Optional[str] = Field(None, description="Business contact email", examples=["contact@apexstudio.io"])
    website: Optional[str] = Field(None, description="Official company website URL", examples=["https://apexstudio.io"])
    rating: Optional[float] = Field(None, description="Average review rating (0.0 - 5.0)", examples=[4.9])
    review_count: int = Field(0, description="Total verified reviews count", examples=[87])
    social_profiles: Dict[str, str] = Field(
        default_factory=dict,
        description="Discovered social media channels",
        examples=[{
            "linkedin": "https://linkedin.com/company/apex-digital-marketing",
            "facebook": "https://facebook.com/apexdigitalvn"
        }]
    )
    verified: bool = Field(True, description="Whether business address and presence are verified", examples=[True])
    latitude: Optional[float] = Field(None, description="Geographic latitude coordinate", examples=[10.7769])
    longitude: Optional[float] = Field(None, description="Geographic longitude coordinate", examples=[106.6953])


class B2BLeadsResponse(BaseModel):
    """B2B Local Leads response schema."""
    success: bool = Field(True, description="Query execution status")
    query: str = Field(..., description="Search niche or business type", examples=["marketing agency"])
    location: str = Field(..., description="Geographic target city/region", examples=["Ho Chi Minh City"])
    total_found: int = Field(..., description="Total verified leads discovered", examples=[32])
    page: int = Field(..., description="Current page number", examples=[1])
    limit: int = Field(..., description="Maximum leads returned per page", examples=[10])
    data: List[B2BLeadItem] = Field(..., description="List of structured local business leads")


# ---------------------------------------------------------------------------
# Common Error Models
# ---------------------------------------------------------------------------

class ErrorResponse(BaseModel):
    """Standardized API error response format."""
    success: bool = Field(False, description="Always False for errors", examples=[False])
    error: str = Field(..., description="Error classification title", examples=["Bad Request"])
    detail: Optional[str] = Field(None, description="Actionable error description", examples=["Query parameter 'limit' must be between 1 and 50."])
    status_code: int = Field(..., description="HTTP status code", examples=[400])
