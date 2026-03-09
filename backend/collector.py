"""
collector.py  –  Tactical Grid-Scanner (Full Austria)
                 Legt ein Gitternetz über ganz Österreich und schneidet
                 das Ausland ab, um API-Calls zu sparen.
"""

import time
import logging
import requests
from datetime import datetime, timezone
from backend.db import upsert_station, insert_price, init_db

log = logging.getLogger(__name__)

# Bounding Box für GANZ Österreich
LAT_MIN, LAT_MAX = 46.3, 49.1  # Von Kärnten (Süd) bis Waldviertel (Nord)
LON_MIN, LON_MAX = 9.5, 17.2   # Von Vorarlberg (West) bis Burgenland (Ost)

# Schrittweite des Rasters (ca. 20-25 km)
LAT_STEP = 0.20
LON_STEP = 0.30

FUEL_TYPES = ["SUP", "DIE", "GAS"]
BASE_URL = "https://api.e-control.at/sprit/1.0"
HEADERS  = {"Accept": "application/json", "User-Agent": "FuelTactical/1.0"}

# 1 Sekunde Pause zwischen den Calls ist schonend genug
RATE_LIMIT_SECONDS = 1.0


def is_in_austria(lat: float, lon: float) -> bool:
    """
    Grob-Filter, um API-Calls im Ausland (Bayern, Italien, Schweiz) zu sparen.
    Passt das Such-Rechteck an die reale Form Österreichs an.
    """
    if lon < 11.0:
        # Vorarlberg & Tirol West (schmaler Streifen)
        return 46.8 <= lat <= 47.6
    elif lon < 13.0:
        # Tirol Ost & Salzburg
        return 46.7 <= lat <= 47.8
    else:
        # Rest von Österreich (OÖ, NÖ, Wien, Bgld, Stmk, Ktn)
        return 46.3 <= lat <= 49.1


def _fetch_by_address(lat: float, lon: float, fuel_type: str) -> list:
    url = f"{BASE_URL}/search/gas-stations/by-address"
    params = {
        "latitude": lat,
        "longitude": lon,
        "fuelType": fuel_type,
        "includeClosed": "false"
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.warning(f"[Grid] API Fehler an Koordinate {lat}/{lon}: {e}")
        return []


def generate_grid():
    """Erzeugt die GPS-Punkte für unser Gitternetz."""
    points = []
    lat = LAT_MIN
    while lat <= LAT_MAX:
        lon = LON_MIN
        while lon <= LON_MAX:
            if is_in_austria(lat, lon):
                points.append((round(lat, 3), round(lon, 3)))
            lon += LON_STEP
        lat += LAT_STEP
    return points


def run_collection():
    """Fährt das gefilterte Österreich-Raster ab."""
    init_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    grid = generate_grid()
    total_prices = 0
    unique_stations = set()

    log.info(f"[Collector] Starte FULL AUSTRIA SCAN. Rasterpunkte: {len(grid)}")

    for idx, (lat, lon) in enumerate(grid, 1):
        for fuel in FUEL_TYPES:
            stations = _fetch_by_address(lat, lon, fuel)

            for s in stations:
                if s["id"] not in unique_stations:
                    # Station speichern
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
                    unique_stations.add(s["id"])

                # Preis eintragen
                for p in s.get("prices", []):
                    if p.get("amount") and p.get("fuelType") == fuel:
                        insert_price(s["id"], p["fuelType"], p["amount"], now)
                        total_prices += 1

            time.sleep(RATE_LIMIT_SECONDS)

        if idx % 20 == 0:
            log.info(f"[Grid] {idx}/{len(grid)} Sektoren gescannt. Bisher {total_prices} Preise geloggt.")

    log.info(f"[Collector] GRID SCAN BEENDET. {total_prices} Preise von {len(unique_stations)} Stationen geloggt.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run_collection()