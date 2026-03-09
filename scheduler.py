"""
scheduler.py  –  Starts both the Flask API and the APScheduler.
                 Collection fires every hour at minute :30.
                 Run this file to start the whole stack.

    python scheduler.py
"""

import logging
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.db import init_db
from backend.collector import run_collection
from backend.api_server import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def start_scheduler():
    scheduler = BackgroundScheduler(timezone="Europe/Vienna")

    # Fire at XX:30 every hour
    scheduler.add_job(
        run_collection,
        trigger=CronTrigger(minute=30, timezone="Europe/Vienna"),
        id="collect_prices",
        name="Hourly price collection",
        max_instances=1,          # never overlap
        coalesce=True,            # skip missed if system was down
        misfire_grace_time=120,   # allow 2min late start
    )

    scheduler.start()
    log.info("[Scheduler] Started — collection fires every hour at :30")
    return scheduler


if __name__ == "__main__":
    init_db()

    # Run first collection immediately in background so DB is populated fast
    log.info("[Scheduler] Running initial collection on startup...")
    t = threading.Thread(target=run_collection, daemon=True)
    t.start()

    scheduler = start_scheduler()

    log.info("[Server] Starting Flask on http://localhost:5000")
    # Flask blocks here — scheduler runs in background threads
    try:
        app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        log.info("[Scheduler] Shutting down...")
        scheduler.shutdown()
