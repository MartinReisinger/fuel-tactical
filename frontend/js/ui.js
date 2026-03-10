// js/ui.js — PLZ search, impressum, language switcher, UI init

// ── THEME TOGGLE ──────────────────────────────────────────────────────────────
function setTheme(theme) {
    if (theme === 'light') {
        document.documentElement.classList.add('light');
    } else {
        document.documentElement.classList.remove('light');
    }
    localStorage.setItem('ft-theme', theme);
    setMapTheme(theme);

    document.getElementById('theme-dark').classList.toggle('active',  theme === 'dark');
    document.getElementById('theme-light').classList.toggle('active', theme === 'light');
}

// Restore saved theme on load
(function () {
    const saved = localStorage.getItem('ft-theme') || 'dark';
    if (saved === 'light') {
        document.documentElement.classList.add('light');
        // map tiles will be set after map.js initialises — call after DOM ready
        document.addEventListener('DOMContentLoaded', () => setMapTheme('light'));
        setTimeout(() => {
            document.getElementById('theme-dark').classList.remove('active');
            document.getElementById('theme-light').classList.add('active');
        }, 0);
    }
})();


async function queryPostcode() {
    const raw = document.getElementById('plzInput').value.trim();
    const errEl = document.getElementById('plz-error');
    errEl.textContent = '';

    if (!raw) return;

    // Nominatim geocoding — Austria only, structured query
    const url = `https://nominatim.openstreetmap.org/search?postalcode=${encodeURIComponent(raw)}&countrycodes=at&format=json&limit=1`;
    try {
        const r = await fetch(url, { headers: { 'Accept-Language': 'de', 'User-Agent': 'FuelTactical/1.0' } });
        const data = await r.json();
        if (!data.length) {
            errEl.textContent = t().queryError;
            return;
        }
        const { lat, lon } = data[0];
        map.setView([parseFloat(lat), parseFloat(lon)], 12);
    } catch(e) {
        errEl.textContent = t().queryError;
    }
}

// Allow Enter key in postcode field
document.getElementById('plzInput').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') queryPostcode();
});

// ── IMPRESSUM ─────────────────────────────────────────────────────────────────
function openImpressum() {
    document.getElementById('impressum-modal').style.display = 'flex';
}
function closeImpressum() {
    document.getElementById('impressum-modal').style.display = 'none';
}

// ── LANGUAGE SWITCHER ─────────────────────────────────────────────────────────
function setLang(lang) {
    currentLang = lang;
    document.documentElement.lang = lang;
    applyTranslations();

    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // Reload stations so sidebar strings update
    loadVisibleStations();
}

function applyTranslations() {
    const tr = t();

    // Header labels
    document.getElementById('fuel-label').textContent   = tr.fuelLabel;
    document.getElementById('plzInput').placeholder     = tr.plzPlaceholder;
    document.getElementById('plz-btn').textContent      = tr.queryBtn;
    document.getElementById('impressum-link').textContent = tr.impressum;

    // Fuel select options
    const sel = document.getElementById('fuelSelect');
    [...sel.options].forEach(opt => {
        if (tr.fuels[opt.value]) opt.textContent = tr.fuels[opt.value];
    });

    // Legend label
    const legLabel = document.getElementById('leg-label');
    if (legLabel) legLabel.textContent = tr.priceScale;

    // Sidebar header defaults
    document.getElementById('visible-count').textContent = tr.topFive;
    document.getElementById('visible-sub').textContent   = tr.movemap;

    // Impressum modal
    document.getElementById('impressum-title').textContent = tr.impressumTitle;
    document.getElementById('impressum-body').innerHTML    = tr.impContent;
    document.getElementById('btn-close-impressum').textContent = tr.close;
}

// ── INIT ──────────────────────────────────────────────────────────────────────
applyTranslations();
loadVisibleStations();
