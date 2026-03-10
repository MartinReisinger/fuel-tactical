// js/map.js — Map setup, markers, sidebar, connector

// ── MAP SETUP ─────────────────────────────────────────────────────────────────
const map = L.map('map', {
    center: [48.0, 14.0], zoom: 9,
    zoomControl: false, attributionControl: false,
    keepBuffer: 4
});

const TILES = {
    dark:  'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    light: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
};

let tileLayer = L.tileLayer(TILES.dark, { keepBuffer: 4 }).addTo(map);

function setMapTheme(theme) {
    tileLayer.setUrl(TILES[theme] || TILES.dark);
}

L.control.zoom({ position: 'bottomright' }).addTo(map);

// ── STATE ─────────────────────────────────────────────────────────────────────
let allMarkers  = {};
let hoveredCardId = null;

// ── COLOR SCALE ───────────────────────────────────────────────────────────────
function priceColor(price, min, max) {
    const t = max === min ? 0 : (price - min) / (max - min);
    const r = t < 0.5 ? Math.round(t * 2 * 255) : 255;
    const g = t < 0.5 ? 200 : Math.round((1 - (t - 0.5) * 2) * 200);
    return `rgb(${r},${g},40)`;
}

// ── LOAD STATIONS ─────────────────────────────────────────────────────────────
async function loadVisibleStations() {
    const fuel = document.getElementById('fuelSelect').value;
    const zoom = map.getZoom();
    const center = map.getCenter();
    const b = map.getBounds();

    const params = new URLSearchParams({
        fuel,
        lat: center.lat.toFixed(5),
        lon: center.lng.toFixed(5),
        lat_min: b.getSouth().toFixed(5),
        lat_max: b.getNorth().toFixed(5),
        lon_min: b.getWest().toFixed(5),
        lon_max: b.getEast().toFixed(5),
    });

    let stations;
    try {
        const r = await fetch(`/api/stations?${params}`);
        stations = await r.json();
    } catch(e) {
        document.getElementById('visible-count').textContent = t().apiError;
        return;
    }

    Object.values(allMarkers).forEach(({marker}) => map.removeLayer(marker));
    allMarkers = {};

    if (!stations.length) {
        document.getElementById('visible-count').textContent = t().noData;
        document.getElementById('visible-sub').textContent  = t().noStations;
        document.getElementById('station-list').innerHTML   = '';
        document.getElementById('map-legend').style.display = 'none';
        return;
    }

    const prices = stations.map(s => s.amount).filter(Boolean);
    const minP = Math.min(...prices);
    const maxP = Math.max(...prices);

    document.getElementById('map-legend').style.display = 'block';
    document.getElementById('leg-label').textContent     = t().priceScale;
    document.getElementById('leg-min').textContent       = `€${minP.toFixed(3)}`;
    document.getElementById('leg-max').textContent       = `€${maxP.toFixed(3)}`;

    updateSidebar(stations.slice(0, 5), minP, maxP);

    if (zoom >= 8) {
        document.getElementById('visible-count').textContent = t().topPrices;
        document.getElementById('visible-sub').textContent   = t().stationsVisible(stations.length);

        stations.forEach((s, idx) => {
            if (!s.amount) return;
            const color  = priceColor(s.amount, minP, maxP);
            const isTop5 = idx < 5;

            const marker = L.circleMarker([s.latitude, s.longitude], {
                radius: isTop5 ? 8 : 5,
                fillColor: color,
                color: isTop5 ? '#ffffff' : 'rgba(255,255,255,0.2)',
                weight: isTop5 ? 2 : 1,
                fillOpacity: 0.9
            }).addTo(map);

            marker.on('click', () => openDossier(s));
            marker.on('mouseover', () => marker.setStyle({ radius: 10, weight: 3, color: '#fff' }));
            marker.on('mouseout',  () => marker.setStyle({
                radius: isTop5 ? 8 : 5,
                weight: isTop5 ? 2 : 1,
                color: isTop5 ? '#ffffff' : 'rgba(255,255,255,0.2)'
            }));

            allMarkers[s.id] = { marker, data: s };
        });
    } else {
        document.getElementById('visible-count').textContent = t().topRegion;
        document.getElementById('visible-sub').textContent   = t().zoomIn(stations.length);
    }
}

// ── SIDEBAR ───────────────────────────────────────────────────────────────────
function updateSidebar(top5, minP, maxP) {
    const list = document.getElementById('station-list');
    list.innerHTML = '';

    top5.forEach((s, idx) => {
        const color = priceColor(s.amount, minP, maxP);
        const card  = document.createElement('div');
        card.className  = 'cam-card';
        card.dataset.id = s.id;
        card.innerHTML  = `
            <div class="rank-badge">#${idx + 1}</div>
            <span class="price-text" style="color:${color}">€ ${s.amount.toFixed(3)}</span>
            <div class="cam-label">
                <strong>${s.name}</strong>
                <span>${s.address}, ${s.city}</span>
            </div>
        `;

        card.addEventListener('mouseenter', () => drawConnector(s.id));
        card.addEventListener('mouseleave', clearConnector);
        card.addEventListener('click', () => {
            map.setView([s.latitude, s.longitude], 15);
            openDossier(s);
        });

        list.appendChild(card);
    });
}

// ── CONNECTOR LINE ────────────────────────────────────────────────────────────
const cvs  = document.getElementById('connector-canvas');
const ctx2d = cvs.getContext('2d');

function resizeCanvas() {
    cvs.width  = window.innerWidth;
    cvs.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

function drawConnector(stationId) {
    clearConnector();
    hoveredCardId = stationId;
    const entry = allMarkers[stationId];
    if (!entry) return;

    const mapPt  = map.latLngToContainerPoint([entry.data.latitude, entry.data.longitude]);
    const mapEl  = document.getElementById('map');
    const mapRect = mapEl.getBoundingClientRect();
    const sx = mapRect.left + mapPt.x;
    const sy = mapRect.top  + mapPt.y;

    const card = document.querySelector(`.cam-card[data-id="${stationId}"]`);
    if (!card) return;
    const cRect = card.getBoundingClientRect();
    const ex = cRect.left;
    const ey = cRect.top + cRect.height / 2;

    ctx2d.clearRect(0, 0, cvs.width, cvs.height);
    ctx2d.beginPath();
    ctx2d.moveTo(sx, sy);
    ctx2d.bezierCurveTo(
        sx + (ex - sx) * 0.6, sy,
        ex - (ex - sx) * 0.2, ey,
        ex, ey
    );
    ctx2d.strokeStyle = 'rgba(41,121,255,0.6)';
    ctx2d.lineWidth   = 1.5;
    ctx2d.setLineDash([4, 3]);
    ctx2d.stroke();

    ctx2d.beginPath();
    ctx2d.arc(sx, sy, 5, 0, Math.PI * 2);
    ctx2d.fillStyle = 'rgba(41,121,255,0.9)';
    ctx2d.fill();
}

function clearConnector() {
    ctx2d.clearRect(0, 0, cvs.width, cvs.height);
    hoveredCardId = null;
}

map.on('move zoom', () => {
    if (hoveredCardId) drawConnector(hoveredCardId);
});

// ── MAP EVENTS ────────────────────────────────────────────────────────────────
let moveTimer = null;
map.on('moveend zoomend', () => {
    clearTimeout(moveTimer);
    moveTimer = setTimeout(loadVisibleStations, 200);
});
