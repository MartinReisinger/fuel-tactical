"""
collector.py  –  Fetches all gas stations for OÖ, Salzburg, NÖ, Wien
                 using the e-control /by-region API.
                 Self-rate-limited: max 1 request per 2 seconds.
"""

import time
import logging
import requests
from datetime import datetime, timezone
from backend.db import upsert_station, insert_price, init_db

log = logging.getLogger(__name__)

# Bundesland codes as used by e-control (type=BL)
BUNDESLAENDER = {
    "OÖ":   4,
    "Sbg":  5,
    "NÖ":   3,
    "Wien": 9,
}

FUEL_TYPES = ["SUP", "DIE", "GAS"]

BASE_URL = "https://api.e-control.at/sprit/1.0"
HEADERS  = {"Accept": "application/json", "User-Agent": "FuelTactical/1.0"}

# Rate limiting: 1 request every N seconds
RATE_LIMIT_SECONDS = 2.5


def _fetch_by_region(bl_code: str, fuel_type: str) -> list:
    url = f"{BASE_URL}/search/gas-stations/by-region"
    params = {
        "code":         bl_code,
        "type":         "BL",
        "fuelType":     fuel_type,
        "includeClosed": "false",
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"[Collector] Fetch failed {bl_code}/{fuel_type}: {e}")
        return []


def run_collection():
    """
    Full collection run across all regions and fuel types.
    Takes ~12 region×fuel combos × 2.5s ≈ ~30 seconds total.
    """
    init_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    total_prices = 0

    log.info(f"[Collector] Starting collection run at {now}")

    for bl_name, bl_code in BUNDESLAENDER.items():
        for fuel in FUEL_TYPES:
            log.info(f"  → {bl_name} / {fuel}")
            stations = _fetch_by_region(bl_code, fuel)

            for s in stations:
                # Upsert station metadata
                upsert_station({
                    "id":          s["id"],
                    "name":        s.get("name", ""),
                    "address":     s.get("location", {}).get("address", ""),
                    "city":        s.get("location", {}).get("city", ""),
                    "postal_code": s.get("location", {}).get("postalCode", ""),
                    "latitude":    s.get("location", {}).get("latitude", 0),
                    "longitude":   s.get("location", {}).get("longitude", 0),
                    "telephone":   s.get("contact", {}).get("telephone", ""),
                    "website":     s.get("contact", {}).get("website", ""),
                })

                # Insert price(s)
                for p in s.get("prices", []):
                    if p.get("amount") and p.get("fuelType"):
                        insert_price(s["id"], p["fuelType"], p["amount"], now)
                        total_prices += 1

            # Rate limit between each API call
            time.sleep(RATE_LIMIT_SECONDS)

    log.info(f"[Collector] Done. {total_prices} price records inserted.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run_collection()
