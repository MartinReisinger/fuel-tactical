"""
api_server.py  –  Lightweight Flask REST API consumed by fuel.html
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os, logging

from backend.db import get_latest_prices, get_price_history, init_db

log = logging.getLogger(__name__)

app = Flask(__name__, static_folder=None)
CORS(app)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')


# ── Static ────────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'fuel.html')


# ── /api/stations ─────────────────────────────────────────────────────────────
# GET /api/stations?fuel=SUP&lat_min=47&lat_max=49&lon_min=13&lon_max=16
@app.route('/api/stations')
def stations():
    fuel = request.args.get('fuel', 'SUP').upper()

    # 1. Koordinaten abgreifen (Mitte für Live-Scan, Bounding-Box für DB-Laden)
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

    # 2. LIVE-ABFRAGE BEI E-CONTROL (Der "Radar-Ping" in der Mitte)
    url = "https://api.e-control.at/sprit/1.0/search/gas-stations/by-address"
    try:
        r = requests.get(url, params={"latitude": lat, "longitude": lon, "fuelType": fuel, "includeClosed": "false"},
                         headers={"User-Agent": "FuelTactical/1.0"}, timeout=5)
        if r.status_code == 200:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            # Frische Daten sofort in die DB schreiben
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
                        insert_price(s["id"], fuel, p.get("amount"), now)
                        break
    except Exception as e:
        log.error(f"Live-Update fehlgeschlagen: {e}")

    # 3. ALLE DATEN AUS DER DB HOLEN (Sichtfeld der Karte)
    db_stations = get_latest_prices(fuel, bounds)

    return jsonify(db_stations)


# ── /api/history ──────────────────────────────────────────────────────────────
# GET /api/history?station_id=1234&fuel=SUP&period=24h
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
