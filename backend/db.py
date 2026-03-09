import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'fuel.db')

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS stations (
                id          INTEGER PRIMARY KEY,
                name        TEXT NOT NULL,
                address     TEXT,
                city        TEXT,
                postal_code TEXT,
                latitude    REAL,
                longitude   REAL,
                telephone   TEXT,
                website     TEXT
            );

            CREATE TABLE IF NOT EXISTS prices (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id  INTEGER NOT NULL,
                fuel_type   TEXT NOT NULL,
                amount      REAL NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (station_id) REFERENCES stations(id)
            );

            CREATE INDEX IF NOT EXISTS idx_prices_station_fuel_time
                ON prices(station_id, fuel_type, recorded_at);
        """)
    print(f"[DB] Initialized at {DB_PATH}")

def upsert_station(s: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO stations (id, name, address, city, postal_code, latitude, longitude, telephone, website)
            VALUES (:id, :name, :address, :city, :postal_code, :latitude, :longitude, :telephone, :website)
            ON CONFLICT(id) DO UPDATE SET
                name        = excluded.name,
                address     = excluded.address,
                city        = excluded.city,
                postal_code = excluded.postal_code,
                latitude    = excluded.latitude,
                longitude   = excluded.longitude,
                telephone   = excluded.telephone,
                website     = excluded.website
        """, s)

def insert_price(station_id: int, fuel_type: str, amount: float, recorded_at: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO prices (station_id, fuel_type, amount, recorded_at)
            VALUES (?, ?, ?, ?)
        """, (station_id, fuel_type, amount, recorded_at))

def get_latest_prices(fuel_type: str, bounds: dict = None):
    """
    Returns the latest price per station for the given fuel type.
    bounds = {lat_min, lat_max, lon_min, lon_max}
    """
    query = """
        SELECT s.id, s.name, s.address, s.city, s.postal_code,
               s.latitude, s.longitude, s.telephone, s.website,
               p.amount, p.recorded_at
        FROM stations s
        JOIN prices p ON p.station_id = s.id
        WHERE p.fuel_type = ?
          AND p.recorded_at = (
              SELECT MAX(p2.recorded_at) FROM prices p2
              WHERE p2.station_id = s.id AND p2.fuel_type = ?
          )
    """
    params = [fuel_type, fuel_type]

    if bounds:
        query += """
          AND s.latitude  BETWEEN ? AND ?
          AND s.longitude BETWEEN ? AND ?
        """
        params += [bounds['lat_min'], bounds['lat_max'],
                   bounds['lon_min'], bounds['lon_max']]

    query += " ORDER BY p.amount ASC"

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]

def get_price_history(station_id: int, fuel_type: str, period: str):
    """
    period: '24h' | '7d' | '30d' | '365d'
    Returns averaged prices bucketed per hour/day/week.
    """
    bucket_map = {
        '24h': ("strftime('%Y-%m-%d %H:00', recorded_at)", "-1 day"),
        '7d': ("strftime('%Y-%m-%d %H:00', recorded_at)", "-7 days"),
        '30d': ("strftime('%Y-%m-%d', recorded_at)", "-30 days"),
        '365d': ("strftime('%Y-%m-%d', recorded_at)", "-365 days"),  # <--- Hier geändert
    }
    bucket_expr, interval = bucket_map.get(period, bucket_map['24h'])
    sql = f"""
        SELECT {bucket_expr} AS bucket,
               AVG(amount) AS avg_price,
               MIN(amount) AS min_price,
               MAX(amount) AS max_price,
               COUNT(*)    AS samples
        FROM prices
        WHERE station_id = ?
          AND fuel_type  = ?
          AND recorded_at >= datetime('now', ?)
        GROUP BY bucket
        ORDER BY bucket ASC
    """
    with get_conn() as conn:
        rows = conn.execute(sql, (station_id, fuel_type, interval)).fetchall()
    return [dict(r) for r in rows]

def cleanup_old_prices(days=365):
    """Löscht Preise, die älter als X Tage sind, um die DB klein zu halten."""
    with get_conn() as conn:
        cursor = conn.execute(f"DELETE FROM prices WHERE recorded_at < datetime('now', '-{days} days')")
        deleted = cursor.rowcount
        print(f"[DB] Cleanup: {deleted} alte Preise gelöscht.")