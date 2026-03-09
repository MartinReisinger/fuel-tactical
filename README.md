# Fuel Tactical — Setup Guide

## Projektstruktur

```
fuel_tactical/
├── backend/
│   ├── __init__.py
│   ├── db.py           # SQLite Datenbanklogik
│   ├── collector.py    # e-control API Abfragen
│   └── api_server.py   # Flask REST API
├── frontend/
│   └── fuel.html       # Das Frontend
├── data/
│   └── fuel.db         # Wird automatisch erstellt
├── scheduler.py        # Einstiegspunkt — startet alles
├── requirements.txt
└── README.md
```

## PyCharm Setup (Schritt für Schritt)

### 1. Projekt anlegen
- PyCharm öffnen → **New Project**
- Location: `fuel_tactical` (oder beliebiger Pfad)
- **New environment using: Virtualenv** (empfohlen)
- Python version: 3.10+ empfohlen
- → **Create**

### 2. Abhängigkeiten installieren
Öffne das **Terminal** in PyCharm (unten) und führe aus:

```bash
pip install -r requirements.txt
```

### 3. Run Configuration anlegen
- Oben rechts: **Add Configuration** → **+** → **Python**
- Name: `Fuel Tactical`
- Script path: `scheduler.py`  (aus dem Projektroot)
- Working directory: `<dein Projektpfad>/fuel_tactical`
- → **OK**

### 4. Starten
- Auf den grünen **Play-Button** klicken
- Beim ersten Start:
  - DB wird in `data/fuel.db` angelegt
  - Sofort ein erster Collection-Run startet (dauert ~30–60s)
  - Flask läuft auf http://localhost:5000

### 5. Browser öffnen
→ http://localhost:5000

---

## Wie es funktioniert

### Daten-Sammlung
- `scheduler.py` startet APScheduler + Flask gleichzeitig
- Jede Stunde um **:30** (00:30, 01:30, ..., 23:30) wird `run_collection()` aufgerufen
- Abgedeckte Bundesländer: **OÖ, Salzburg, NÖ, Wien**
- Kraftstofftypen: **SUP, DIE, GAS** (3 × 4 Bundesländer = 12 API-Calls)
- Rate-Limit: **2,5 Sekunden** zwischen jedem API-Call → ~30s Gesamtdauer pro Run

### Frontend
- Karte zeigt alle Tankstellen im aktuellen Kartenfenster (farbcodiert grün→rot)
- Rechte Sidebar: Top 5 günstigste im Blickfeld
- Hover auf Sidebar-Karte → gestrichelte Linie zur Tankstelle auf der Karte
- Klick → Dossier mit Preisverlauf (24h / 7 Tage / Monat / Jahr)

### API Endpoints
```
GET /api/stations?fuel=SUP&lat_min=47&lat_max=49&lon_min=13&lon_max=16
GET /api/history?station_id=1234&fuel=SUP&period=24h
```

---

## Erstes Datenproblem?
Falls die Karte leer ist, läuft die erste Sammlung noch.
Manuell triggern: Im Terminal:

```bash
python -c "from backend.collector import run_collection; run_collection()"
```

---

## Optional: Als Dienst starten (immer im Hintergrund)

### Windows (Task Scheduler)
Aufgabe anlegen die `python scheduler.py` beim Login startet.

### macOS/Linux (systemd oder launchd)
```bash
# Simpelste Lösung:
nohup python scheduler.py > fuel.log 2>&1 &
```
