"""Comprehensive test suite for RapidAPI Scrapers Hub."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# ---------------------------------------------------------------------------
# Health Endpoint Tests
# ---------------------------------------------------------------------------

def test_health_check():
    """Verify health endpoint returns 200 and accurate service metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "rapidapi-scrapers-hub"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data
    assert "/health" in data["endpoints_available"]
    assert "/api/v1/tiktok/top-ads" in data["endpoints_available"]
    assert "/api/v1/shopee/pricing" in data["endpoints_available"]
    assert "/api/v1/b2b/leads" in data["endpoints_available"]


# ---------------------------------------------------------------------------
# TikTok Top Ads Endpoint Tests
# ---------------------------------------------------------------------------

def test_tiktok_top_ads_defaults():
    """Test TikTok Top Ads endpoint with default query parameters."""
    response = client.get("/api/v1/tiktok/top-ads")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["country"] == "US"
    assert data["page"] == 1
    assert data["limit"] == 10
    assert data["period_days"] == 30
    assert isinstance(data["data"], list)
    assert len(data["data"]) > 0

    first_item = data["data"][0]
    assert "ad_id" in first_item
    assert "title" in first_item
    assert "advertiser_name" in first_item
    assert "ctr" in first_item
    assert "cvr" in first_item
    assert "likes" in first_item
    assert "landing_page_url" in first_item
    assert "video_url" in first_item


def test_tiktok_top_ads_country_and_industry_filters():
    """Test TikTok Top Ads filtering by specific country and industry."""
    response = client.get(
        "/api/v1/tiktok/top-ads",
        params={
            "country": "VN",
            "industry": "Beauty & Personal Care",
            "objective": "Conversions",
            "limit": 5,
            "page": 1,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["country"] == "VN"
    assert data["industry"] == "Beauty & Personal Care"
    assert data["objective"] == "Conversions"
    assert len(data["data"]) <= 5
    for item in data["data"]:
        assert item["country"] == "VN"


def test_tiktok_top_ads_sorting():
    """Test sorting criteria: like, ctr, cvr."""
    for sort_key in ["like", "ctr", "cvr"]:
        response = client.get(f"/api/v1/tiktok/top-ads?sort_by={sort_key}&limit=5")
        assert response.status_code == 200
        data = response.json()
        items = data["data"]
        assert len(items) > 0
        if len(items) >= 2:
            val_0 = items[0]["likes"] if sort_key == "like" else items[0][sort_key]
            val_1 = items[1]["likes"] if sort_key == "like" else items[1][sort_key]
            assert val_0 >= val_1


def test_tiktok_top_ads_validation_errors():
    """Test input validation for boundary limits and invalid sort keys."""
    # Exceed limit
    resp_limit = client.get("/api/v1/tiktok/top-ads?limit=100")
    assert resp_limit.status_code == 422
    assert resp_limit.json()["error"] == "Validation Error"

    # Zero limit
    resp_zero = client.get("/api/v1/tiktok/top-ads?limit=0")
    assert resp_zero.status_code == 422

    # Invalid sort option
    resp_sort = client.get("/api/v1/tiktok/top-ads?sort_by=unknown_sort")
    assert resp_sort.status_code == 422


# ---------------------------------------------------------------------------
# Shopee SEA Pricing Endpoint Tests
# ---------------------------------------------------------------------------

def test_shopee_pricing_success():
    """Test Shopee pricing scraping endpoint with valid search query."""
    response = client.get(
        "/api/v1/shopee/pricing",
        params={
            "query": "tai nghe bluetooth",
            "country": "VN",
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query"] == "tai nghe bluetooth"
    assert data["country"] == "VN"
    assert data["currency"] == "VND"
    assert data["total_found"] > 0
    assert len(data["data"]) <= 5
    assert data["average_price"] > 0
    assert data["min_price"] <= data["average_price"] <= data["max_price"]

    first_item = data["data"][0]
    assert "item_id" in first_item
    assert "shop_id" in first_item
    assert "name" in first_item
    assert "price" in first_item
    assert "rating_star" in first_item
    assert "product_url" in first_item


def test_shopee_pricing_missing_required_query():
    """Test that missing required query parameter triggers 422 validation error."""
    response = client.get("/api/v1/shopee/pricing")
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Validation Error"


def test_shopee_pricing_price_filters():
    """Test price filtering with min_price and max_price boundaries."""
    response = client.get(
        "/api/v1/shopee/pricing",
        params={
            "query": "wireless keyboard",
            "country": "SG",
            "min_price": 40.0,
            "max_price": 90.0,
            "limit": 10,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["currency"] == "SGD"
    for item in data["data"]:
        assert 40.0 <= item["price"] <= 90.0


def test_shopee_pricing_invalid_price_range():
    """Test that min_price > max_price triggers 400 Bad Request."""
    response = client.get(
        "/api/v1/shopee/pricing",
        params={
            "query": "laptop stand",
            "min_price": 500000,
            "max_price": 100000,
        },
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "cannot be greater than" in data["detail"]


def test_shopee_pricing_multiple_countries():
    """Test currency detection across Southeast Asian countries."""
    countries_currencies = [
        ("VN", "VND"),
        ("SG", "SGD"),
        ("MY", "MYR"),
        ("TH", "THB"),
        ("PH", "PHP"),
        ("ID", "IDR"),
    ]
    for country, expected_curr in countries_currencies:
        resp = client.get(
            "/api/v1/shopee/pricing",
            params={"query": "smart watch", "country": country, "limit": 2},
        )
        assert resp.status_code == 200
        assert resp.json()["currency"] == expected_curr


# ---------------------------------------------------------------------------
# B2B Local Leads Endpoint Tests
# ---------------------------------------------------------------------------

def test_b2b_leads_success():
    """Test B2B Leads extraction with valid query and location."""
    response = client.get(
        "/api/v1/b2b/leads",
        params={
            "query": "marketing agency",
            "location": "Ho Chi Minh City",
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["query"] == "marketing agency"
    assert data["location"] == "Ho Chi Minh City"
    assert data["total_found"] > 0
    assert len(data["data"]) <= 5

    lead = data["data"][0]
    assert "lead_id" in lead
    assert "business_name" in lead
    assert "category" in lead
    assert "address" in lead
    assert "city" in lead
    assert "country" in lead
    assert "verified" in lead


def test_b2b_leads_missing_required_params():
    """Test missing query or location triggers 422."""
    # Missing location
    resp_no_loc = client.get("/api/v1/b2b/leads?query=coffee+shop")
    assert resp_no_loc.status_code == 422

    # Missing query
    resp_no_q = client.get("/api/v1/b2b/leads?location=Singapore")
    assert resp_no_q.status_code == 422


def test_b2b_leads_filters():
    """Test B2B filters: has_website, has_phone, min_rating."""
    response = client.get(
        "/api/v1/b2b/leads",
        params={
            "query": "dental clinic",
            "location": "Ho Chi Minh City",
            "has_website": True,
            "has_phone": True,
            "min_rating": 4.5,
            "limit": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    for lead in data["data"]:
        assert lead["website"] is not None
        assert lead["phone"] is not None
        assert (lead["rating"] or 0) >= 4.5


# ---------------------------------------------------------------------------
# Middleware, Security & Error Handling Tests
# ---------------------------------------------------------------------------

def test_rapidapi_middleware_headers():
    """Test RapidAPI context header parsing and response timing header."""
    headers = {
        "X-RapidAPI-Key": "test-subscriber-key-9988",
        "X-RapidAPI-User": "test_subscriber_user",
    }
    response = client.get("/health", headers=headers)
    assert response.status_code == 200
    assert "X-Response-Time" in response.headers
    assert "ms" in response.headers["X-Response-Time"]
    assert response.headers.get("X-RapidAPI-Version") == "1.0.0"


def test_proxy_secret_protection(monkeypatch):
    """Test optional RAPIDAPI_PROXY_SECRET enforcement."""
    # Enable proxy secret in env
    monkeypatch.setenv("RAPIDAPI_PROXY_SECRET", "super-secret-rapidapi-token")

    # 1. Health check should still pass without secret
    health_resp = client.get("/health")
    assert health_resp.status_code == 200

    # 2. Protected endpoint without secret -> 403 Forbidden
    no_secret_resp = client.get("/api/v1/tiktok/top-ads")
    assert no_secret_resp.status_code == 403
    assert no_secret_resp.json()["error"] == "Forbidden"

    # 3. Protected endpoint with invalid secret -> 403 Forbidden
    bad_secret_resp = client.get(
        "/api/v1/tiktok/top-ads",
        headers={"X-RapidAPI-Proxy-Secret": "wrong-secret"},
    )
    assert bad_secret_resp.status_code == 403

    # 4. Protected endpoint with correct secret -> 200 OK
    good_secret_resp = client.get(
        "/api/v1/tiktok/top-ads",
        headers={"X-RapidAPI-Proxy-Secret": "super-secret-rapidapi-token"},
    )
    assert good_secret_resp.status_code == 200


def test_404_not_found():
    """Test custom JSON response for non-existent routes."""
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "Not Found"
    assert data["status_code"] == 404
