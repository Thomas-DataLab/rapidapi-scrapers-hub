"""Export RapidAPI-compliant OpenAPI 3.0 specification from FastAPI application."""
import json
import os
import sys

# Ensure local app is on sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app.main import app


def export_rapidapi_openapi() -> str:
    """Generate and enrich OpenAPI JSON schema for RapidAPI Hub listing."""
    schema = app.openapi()

    # Enrich metadata for RapidAPI
    schema["info"]["title"] = "ScrapersHub API - TikTok Top Ads, Shopee SEA Pricing & B2B Leads"
    schema["info"]["version"] = "1.0.0"
    schema["info"]["description"] = (
        "Enterprise-grade scraping & intelligence Micro-SaaS. "
        "Provides 3 unified endpoints for TikTok Top Ads creative performance, "
        "Shopee Southeast Asia live pricing & sales velocity, and B2B local business leads."
    )

    # Server definitions
    schema["servers"] = [
        {
            "url": "https://scrapers-hub.p.rapidapi.com",
            "description": "RapidAPI Production Gateway",
        },
        {
            "url": "http://localhost:8000",
            "description": "Local Development Server",
        },
    ]

    # RapidAPI Security Schemes
    if "components" not in schema:
        schema["components"] = {}

    schema["components"]["securitySchemes"] = {
        "RapidAPIKey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-RapidAPI-Key",
            "description": "Your RapidAPI Subscription Secret Key",
        },
        "RapidAPIHost": {
            "type": "apiKey",
            "in": "header",
            "name": "X-RapidAPI-Host",
            "description": "RapidAPI Host Identifier (e.g. scrapers-hub.p.rapidapi.com)",
        },
    }

    # Apply security globally
    schema["security"] = [
        {
            "RapidAPIKey": [],
            "RapidAPIHost": [],
        }
    ]

    out_file = os.path.join(CURRENT_DIR, "rapidapi_openapi.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)

    print(f"✅ RapidAPI OpenAPI schema successfully exported to: {out_file}")
    return out_file


if __name__ == "__main__":
    export_rapidapi_openapi()
