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

    bounds = None
    try:
        bounds = {
            'lat_min': float(request.args['lat_min']),
            'lat_max': float(request.args['lat_max']),
            'lon_min': float(request.args['lon_min']),
            'lon_max': float(request.args['lon_max']),
        }
    except (KeyError, ValueError):
        pass  # no bounds → return all

    rows = get_latest_prices(fuel, bounds)
    return jsonify(rows)


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
    app.run(host='0.0.0.0', port=5000, debug=False)
