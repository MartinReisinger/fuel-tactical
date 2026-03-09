# ⛽ Fuel Tactical — Austria Edition

**Fuel Tactical** ist ein hochperformantes, kartenbasiertes Dashboard zur Visualisierung von Treibstoffpreisen in Österreich in Echtzeit. Die Anwendung kombiniert ein modernes "Mobile-First" Frontend mit einem intelligenten Backend-Caching-System, um die offizielle **E-Control API** effizient und konform zu nutzen.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)

---

## 🚀 Key Features

*   **On-Demand Radar:** Lädt Daten dynamisch basierend auf deinem Kartenausschnitt. Bewege das Fadenkreuz, und das System holt automatisch die aktuellsten Preise.
*   **Smart Cache (60 Min):** Schont die API-Ressourcen der E-Control. Daten im selben Sektor werden nur aktualisiert, wenn sie älter als eine Stunde sind.
*   **Intelligentes Dossier:** Detaillierte Ansicht jeder Tankstelle inklusive:
    *   **Stufen-Graphen (Chart.js):** Realitätsnahe Preisverläufe (24h bis 1 Jahr), die Preissprünge als Treppen darstellen.
    *   **Direkt-Kontakt:** Klickbare Telefonnummern und Webseiten für mobile Nutzer.
*   **Palantir-Style UI:** Hover-Effekte mit Verbindungslinien zwischen Liste und Karten-Marker für maximale Übersicht.
*   **Auto-Maintenance:** Ein integrierter Scheduler bereinigt die SQLite-Datenbank jede Nacht um 03:00 Uhr von Daten, die älter als 365 Tage sind.
*   **Responsive Design:** Nahtloser Wechsel zwischen Desktop-Sidebar und mobilem Bottom-Sheet.

---

## 🛠 Tech Stack

*   **Backend:** Python 3.10+, Flask, Flask-CORS, APScheduler
*   **Datenbank:** SQLite (mit automatischer Bereinigungslogik)
*   **Frontend:** HTML5, CSS3 (Modern Flex/Grid), Vanilla JavaScript
*   **Maps & Charts:** Leaflet.js, Chart.js
*   **Datenquelle:** Offizielle REST-API der [E-Control Österreich](https://www.e-control.at/)

---

## 📁 Projektstruktur

```text
fuel_tactical/
├── backend/
│   ├── db.py           # SQLite Datenbank & Auto-Cleanup Logik
│   └── api_server.py   # Flask REST API (Caching & Proxy)
├── frontend/
│   └── fuel.html       # Interaktives UI (Single-Page-App)
├── data/
│   └── fuel.db         # Persistente Speicherung (wird auto-generiert)
├── scheduler.py        # Main Entry Point (Server + Hausmeister-Job)
├── requirements.txt    # Abhängigkeiten
└── README.md
