# Fuel Tactical — Setup Guide

Ein einfaches Dashboard zur Visualisierung von Treibstoffpreisen in Österreich auf Basis der E-Control API.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)

## 🌐 Live Demo
Das Dashboard ist unter folgender Adresse öffentlich erreichbar:

**[Working Demo: Fuel Tactical Österreich](http://212.227.93.118:5005/)**

> **Hinweis:** Da dies ein privates Hobbyprojekt auf einem ressourcenschonenden (IONOS) VPS ist, kann es bei hoher Last zu kurzen Verzögerungen kommen.

## Projektstruktur

```text
fuel_tactical/
├── backend/
│   ├── __init__.py
│   ├── db.py           # SQLite Datenbanklogik & Auto-Cleanup
│   └── api_server.py   # Flask REST API (Smart Cache & Live-Ping)
├── frontend/
│   └── fuel.html       # Das interaktive Frontend (Mobile-First)
├── data/
│   └── fuel.db         # Wird automatisch beim Start erstellt
├── scheduler.py        # Einstiegspunkt — Startet Server & Hausmeister-Job
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
*(Stelle sicher, dass `Flask`, `flask-cors`, `requests` und `APScheduler` in der Datei stehen).*

### 3. Run Configuration anlegen
- Oben rechts: **Add Configuration** → **+** → **Python**
- Name: `Fuel Tactical`
- Script path: `scheduler.py` (aus dem Projektroot)
- Working directory: `<dein Projektpfad>/fuel_tactical`
- → **OK**

### 4. Starten
- Auf den grünen **Play-Button** klicken.
- Beim ersten Start:
  - Die Datenbank wird in `data/fuel.db` angelegt.
  - Flask startet sofort auf `http://localhost:5005`.
  - Der Scheduler plant den nächtlichen DB-Cleanup für 03:00 Uhr.

### 5. Browser öffnen
→ http://localhost:5005

---

## Wie es funktioniert (Live-Radar & Smart Cache)

Das System wurde so konzipiert, dass es die E-Control API maximal schont und zu 100 % konform mit den Nutzungsbedingungen arbeitet.

### 1. Das On-Demand Radar
- Wenn du die Karte im Browser bewegst, sendet das Frontend die **Mittelpunkt-Koordinaten** an das Backend (maximal 1 Anfrage pro 0,5 Sekunden, gedrosselt).
- Das Backend prüft die lokale Datenbank (`fuel.db`).
- **Cache:** Sind die Daten in diesem Bereich jünger als 60 Minuten, werden sofort die lokalen Daten ans Frontend geschickt. Sind die Daten älter (oder nicht vorhanden), macht das Backend einen "Live-Ping" an die E-Control API, speichert die frischen Preise in der fuel.db datei ab und liefert sie aus.

### 2. Der Scheduler (Hausmeister-Job)
- `scheduler.py` startet nicht nur den Webserver, sondern auch einen Hintergrund-Job.
- Jeden Tag um **03:00 Uhr nachts** wird die Datenbank bereinigt. Alle historischen Preise, die älter als 365 Tage sind, werden gelöscht, damit die Datenbank über die Jahre nicht zu groß wird.

### 3. Frontend & UI
- **Responsive:** Auf dem Desktop gibt es eine rechte Sidebar. Auf mobilen Geräten (Smartphones) wandert die Liste als "Bottom-Sheet" an den unteren Bildschirmrand.
- **Top 5:** Zeigt immer die 5 günstigsten Tankstellen im aktuellen Kartenausschnitt.
- **Interaktiv:** Ein Hover über die Liste zeichnet eine "Palantir-Style" Verbindungslinie zur Tankstelle auf der Karte.
- **Dossier:** Ein Klick öffnet ein Modal mit exakten Adressdaten, klickbarer Telefonnummer/Website und einem Chart.js Preisverlauf (24h / 7 Tage / Monat / Jahr), der Preissprünge realitätsnah als Stufen-Graph ("Treppen") darstellt.

---

## API Endpoints

**1. Live-Radar & Stationsabruf**
```http
GET /api/stations?fuel=SUP&lat=48.32&lon=14.28&lat_min=48.2&lat_max=48.4&lon_min=14.1&lon_max=14.4
```

**2. Historischer Preisverlauf (Dossier)**
```http
GET /api/history?station_id=1234&fuel=SUP&period=24h
```

---

## Erste Schritte / Kein Daten-Setup nötig
Da das System "On-Demand" funktioniert, ist die Karte beim allerersten Start (und leerer Datenbank) zunächst leer. **Bewege einfach die Karte an den gewünschten Ort.** Das System holt sich die Daten für den anvisierten Bereich automatisch im Hintergrund und die Karte füllt sich in Echtzeit!

---

## Optional: Als Dienst starten (immer im Hintergrund)

### Windows (Task Scheduler)
Aufgabe anlegen, die `python scheduler.py` beim Systemstart/Login ausführt.

### macOS/Linux (systemd oder launchd)
```bash
# Simpelste Lösung (Terminal läuft im Hintergrund weiter):
nohup python scheduler.py > fuel.log 2>&1 &
```
