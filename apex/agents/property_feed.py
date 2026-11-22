"""Source-backed property research loader.

No network calls, scraping, simulated properties or automatic outreach.
A stale or invalid feed produces no executable opportunities.
"""
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

DEFAULT_FEED = Path(__file__).resolve().parents[2] / "data" / "johnson_county_verified_properties.json"
MAX_BYTES = 128_000
MAX_AGE_DAYS = 7


def _valid_https(url):
    if not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password


def load_property_feed(path=None, today=None):
    """Return bounded evidence-backed research rows or []; no authorization to trade."""
    location = Path(path or os.getenv("APEX_PROPERTY_FEED_PATH") or DEFAULT_FEED)
    today = today or datetime.now(timezone.utc).date()
    try:
        if location.stat().st_size > MAX_BYTES:
            return []
        payload = json.loads(location.read_text(encoding="utf-8"))
        if payload.get("schema_version") != 1 or not isinstance(payload.get("properties"), list):
            return []
        feed_date = date.fromisoformat(payload["reviewed_on"])
        age = (today - feed_date).days
        if age < 0 or age > MAX_AGE_DAYS:
            return []
        rows = []
        seen = set()
        for row in payload["properties"]:
            if not isinstance(row, dict):
                return []
            required = ("id", "address", "kind", "asking_price_usd", "status",
                        "listing_url", "reviewed_on", "occupancy")
            if any(field not in row for field in required):
                return []
            row_date = date.fromisoformat(row["reviewed_on"])
            if (today - row_date).days < 0 or (today - row_date).days > MAX_AGE_DAYS:
                return []
            if row["id"] in seen or not isinstance(row["id"], str) or not row["id"].strip():
                return []
            seen.add(row["id"])
            if not _valid_https(row["listing_url"]):
                return []
            if row["kind"] not in ("vacant_land", "house_rehab_candidate"):
                return []
            if row["status"] != "active_as_reported":
                return []
            if not isinstance(row["asking_price_usd"], int) or isinstance(row["asking_price_usd"], bool) or row["asking_price_usd"] <= 0:
                return []
            if not isinstance(row["address"], str) or not row["address"].strip():
                return []
            if row["kind"] == "house_rehab_candidate" and row["occupancy"] != "unknown":
                return []  # No vacant-home claim without separately checked occupancy
            buyer = row.get("buyer_candidate")
            if buyer is not None:
                if not isinstance(buyer, dict) or not _valid_https(buyer.get("criteria_url")):
                    return []
                if buyer.get("match_status") not in ("partial_published_criteria", "unverified_candidate"):
                    return []
            rows.append(dict(row))
        return rows
    except (OSError, ValueError, KeyError, TypeError, OverflowError):
        return []
