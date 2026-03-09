"""
scheduler.py  –  Starts the Flask API and a daily DB cleanup job.
                 Run this file to start the whole stack.

    python scheduler.py
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

# WICHTIG: collector.py ist weg, stattdessen laden wir cleanup_old_prices
from backend.db import init_db, cleanup_old_prices
from backend.api_server import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Europe/Vienna")

    # Cleanup jeden Tag um 03:00 Uhr nachts (behält historische Daten für 365 Tage)
    scheduler.add_job(
        cleanup_old_prices,
        args=[365],
        trigger=CronTrigger(hour=3, minute=0, timezone="Europe/Vienna"),
        id="cleanup_db",
        name="Daily DB Cleanup",
        max_instances=1,
    )

    scheduler.start()
    log.info("[Scheduler] Started — DB cleanup fires daily at 03:00 AM")
    return scheduler


if __name__ == "__main__":
    # 1. Datenbank initialisieren (Tabellen erstellen, falls sie fehlen)
    init_db()

    # 2. Starte den Scheduler für die nächtliche Datenbank-Bereinigung
    scheduler = start_scheduler()

    log.info("[Server] Starting Flask on http://0.0.0.0:5005")

    # 3. Flask Server starten (Blockiert hier, Scheduler läuft im Hintergrund weiter)
    try:
        app.run(host="0.0.0.0", port=5005, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        log.info("[Scheduler] Shutting down...")
        scheduler.shutdown()