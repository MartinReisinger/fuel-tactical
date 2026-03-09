"""
api_server.py  –  Lightweight Flask REST API consumed by fuel.html
"""

import os
import logging
import requests
from datetime import datetime, timezone

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from backend.db import get_latest_prices, get_price_history, init_db, upsert_station, insert_price

log = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')


# ── Static ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'fuel.html')


# ── /api/stations (SMART LIVE-RADAR MIT CACHE) ────────────────────────────────
@app.route('/api/stations')
def stations():
    fuel = request.args.get('fuel', 'SUP').upper()

    try:
        lat = float(request.args['lat'])
        lon = float(request.args['lon'])
        bounds = {
            'lat_min': float(request.args['lat_min']),
            'lat_max': float(request.args['lat_max']),
            'lon_min': float(request.args['lon_min']),
            'lon_max': float(request.args['lon_max']),
        }
    except (KeyError, ValueError):
        return jsonify({'error': 'Missing coordinates'}), 400

    # 1. DATEN AUS LOKALER DATENBANK HOLEN
    db_stations = get_latest_prices(fuel, bounds)

    # 2. PRÜFEN: SIND DIE DATEN ZU ALT? (Älter als 1 Stunde / 3600 Sekunden)
    needs_update = True
    if db_stations:
        # Den neuesten Zeitstempel aus den gefundenen Stationen suchen
        newest_record_str = max(s['recorded_at'] for s in db_stations)
        newest_record_time = datetime.strptime(newest_record_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)

        # Wenn der neueste Eintrag jünger als 1 Stunde ist, machen wir KEIN Update!
        if (now - newest_record_time).total_seconds() < 3600:
            needs_update = False

    # 3. E-CONTROL API NUR ANFUNKEN, WENN NÖTIG
    if needs_update:
        log.info(f"Daten im Sektor veraltet oder leer. Starte Live-Ping für {lat}, {lon}...")
        url = "https://api.e-control.at/sprit/1.0/search/gas-stations/by-address"
        try:
            r = requests.get(url, params={"latitude": lat, "longitude": lon, "fuelType": fuel, "includeClosed": "false"}, headers={"User-Agent": "FuelTactical/1.0"}, timeout=5)
            if r.status_code == 200:
                now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                for s in r.json():
                    upsert_station({
                        "id": s["id"], "name": s.get("name", ""),
                        "address": s.get("location", {}).get("address", ""),
                        "city": s.get("location", {}).get("city", ""),
                        "postal_code": s.get("location", {}).get("postalCode", ""),
                        "latitude": s.get("location", {}).get("latitude", 0),
                        "longitude": s.get("location", {}).get("longitude", 0),
                        "telephone": s.get("contact", {}).get("telephone", ""),
                        "website": s.get("contact", {}).get("website", ""),
                    })
                    for p in s.get("prices", []):
                        if p.get("fuelType") == fuel:
                            insert_price(s["id"], fuel, p.get("amount"), now_str)
                            break

                # Nach dem Update die frischen Daten erneut aus der DB laden
                db_stations = get_latest_prices(fuel, bounds)
        except Exception as e:
            log.error(f"Live-Update fehlgeschlagen: {e}")

    # 4. DATEN ANS FRONTEND SCHICKEN
    return jsonify(db_stations)


# ── /api/history ──────────────────────────────────────────────────────────────
@app.route('/api/history')
def history():
    try:
        station_id = int(request.args['station_id'])
    except (KeyError, ValueError):
        return jsonify({'error': 'station_id required'}), 400

    fuel   = request.args.get('fuel',   'SUP').upper()
    period = request.args.get('period', '24h')

    if period not in ('24h', '7d', '30d', '365d'):
        return jsonify({'error': 'period must be 24h|7d|30d|365d'}), 400

    data = get_price_history(station_id, fuel, period)
    return jsonify(data)


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5005, debug=False)