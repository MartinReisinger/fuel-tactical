# ⛽ Fuel Tactical — Austria Edition

Ein einfaches Dashboard zur Visualisierung von Treibstoffpreisen in Österreich auf Basis der E-Control API.

![License](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Framework-Flask-lightgrey.svg)

## 🌐 Live Demo
Das Dashboard ist unter folgender Adresse öffentlich erreichbar:
**[Working Demo: Fuel Tactical Österreich](http://fuel-tactical.site/)**

---

## 🛠 Server Maintenance & Update Guide (Ubuntu)

Um die Website auf dem Server zu aktualisieren und neu zu starten, verwende diese Befehlsfolge:

### 1. In das Projektverzeichnis wechseln
```bash
cd /home/fuel-tactical/
```

### 2. Code aktualisieren & Server neu starten
Kopiere diesen Block, um den alten Prozess zu beenden, den neuen Code zu ziehen und den Server im Hintergrund neu zu starten:
```bash
pkill -f scheduler.py
git pull origin main
source venv/bin/activate
nohup python scheduler.py > fuel.log 2>&1 &
```

---

## 📁 Projektstruktur

```text
fuel_tactical/
├── backend/
│   ├── db.py           # SQLite Datenbanklogik & Auto-Cleanup
│   └── api_server.py   # Flask REST API (Smart Cache & Live-Ping)
├── frontend/
│   └── fuel.html       # Das interaktive Frontend (Mobile-First)
├── data/
│   └── fuel.db         # Wird automatisch beim Start erstellt
├── scheduler.py        # Einstiegspunkt — Server & Maintenance-Job
├── requirements.txt
└── README.md
```

---

## 💻 PyCharm Setup (Lokale Entwicklung)

### 1. Projekt anlegen
- PyCharm öffnen → **New Project**
- Location: `fuel_tactical`
- **New environment using: Virtualenv**
- Python version: 3.10+
- → **Create**

### 2. Abhängigkeiten installieren
Im PyCharm Terminal ausführen:
```bash
pip install -r requirements.txt
```

### 3. Run Configuration
- Oben rechts: **Add Configuration** → **+** → **Python**
- Name: `Fuel Tactical`
- Script path: `scheduler.py`
- Working directory: Dein Projektpfad
- → **OK**

---

## ⚙️ Funktionsweise (Live-Radar & Smart Cache)

Das System wurde so konzipiert, dass es die E-Control API maximal schont und zu 100 % konform mit den Nutzungsbedingungen arbeitet.

### 1. Das On-Demand Radar
- Wenn du die Karte bewegst, sendet das Frontend die Mittelpunkt-Koordinaten an das Backend (maximal 1 Anfrage pro 0,2 Sekunden, gedrosselt).
- Das Backend prüft die lokale Datenbank (`fuel.db`).
- **Cache:** Sind die Daten in diesem Bereich jünger als 60 Minuten, werden sofort die lokalen Daten ans Frontend geschickt. Sind die Daten älter oder nicht vorhanden, macht das Backend einen "Live-Ping" an die E-Control API, speichert die frischen Preise ab und liefert sie aus.

### 2. Der Scheduler (Hausmeister-Job)
- `scheduler.py` startet nicht nur den Webserver, sondern auch einen Hintergrund-Job.
- Jeden Tag um 03:00 Uhr nachts wird die Datenbank bereinigt (Daten > 365 Tage werden gelöscht).

### 3. Frontend & UI
- **Responsive:** Desktop Sidebar vs. Mobile Bottom-Sheet.
- **Top 5:** Zeigt die günstigsten Tankstellen im aktuellen Ausschnitt.
- **Dossier:** Chart.js Preisverlauf (Stufen-Graph) für 24h / 7 Tage / Monat / Jahr.

---

## 📄 Rechtliche Hinweise / Impressum

Dieses Projekt ist eine private, nicht-kommerzielle Web-Applikation. Es besteht keine Gewinnerzielungsabsicht.

* **Betreiber:** Martin Reisinger, Linz, Österreich
* **Datenquelle:** [E-Control Österreich](https://www.e-control.at/)
* **Hinweis:** Die Identifizierung des Urhebers erfolgt gemäß den gesetzlichen Informationspflichten für private Webseiten.

