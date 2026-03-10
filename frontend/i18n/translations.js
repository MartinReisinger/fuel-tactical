// i18n/translations.js
// All UI strings for DE and EN

const TRANSLATIONS = {
    de: {
        brand: 'FUEL <span>TACTICAL</span>',
        fuelLabel: 'TREIBSTOFF',
        fuels: { SUP: 'SUPER 95', DIE: 'DIESEL', GAS: 'CNG GAS' },
        plzPlaceholder: 'PLZ eingeben…',
        queryBtn: 'SUCHEN',
        queryError: 'PLZ nicht gefunden.',
        dbLabel: 'DB',
        topFive: 'TOP 5 IM BLICKFELD',
        movemap: '— bewege die karte —',
        noData: 'KEINE DATEN',
        noStations: 'Keine Tankstellen in diesem Bereich',
        apiError: 'API FEHLER',
        topPrices: 'TOP 5 PREISE',
        stationsVisible: (n) => `${n} TANKSTELLEN IM BILD`,
        topRegion: 'TOP 5 (REGION)',
        zoomIn: (n) => `Zoom rein für Marker (${n} gefunden)`,
        priceScale: 'PREIS-SKALA',
        nodeId: 'NODE ID',
        tabs: { '24h': '24H', '7d': '7 TAGE', '30d': 'MONAT', '365d': 'JAHR' },
        tableKeys: {
            fuel: 'TREIBSTOFF',
            price: 'PREIS',
            address: 'ADRESSE',
            city: 'ORT',
            coords: 'KOORDINATEN',
            phone: 'TELEFON',
            website: 'WEBSITE',
        },
        googleMaps: 'GOOGLE MAPS',
        appleMaps: 'APPLE MAPS',
        close: 'CLOSE',
        impressum: 'IMPRESSUM',
        impressumTitle: 'Impressum',
        noHistData: 'KEINE HISTORISCHEN DATEN',
        impContent: `
            <strong>Betreiber</strong><br>
            Martin Reisinger<br>
            Linz, Österreich<br>
            <a href="mailto:rezepte.home.web@gmail.com" style="color: var(--accent); text-decoration: none;">rezepte.home.web@gmail.com</a><br><br>
            <strong>Was ist das hier?</strong><br>
            Ein privates Hobbyprojekt – keine Werbung, kein Abo, kein Gewinn.
            Die Spritpreise kommen direkt von der offiziellen
            <a href="https://api.e-control.at/sprit/1.0/doc/" target="_blank" style="color: var(--accent); text-decoration: none;">E-Control API ↗</a>.<br><br>
            <strong>Datenschutz</strong><br>
            Zur Analyse der Nutzung verwende ich
            <a href="https://www.goatcounter.com" target="_blank" style="color: var(--accent); text-decoration: none;">GoatCounter</a>.
            Es werden keine Cookies gesetzt und keine personenbezogenen Daten gespeichert.<br><br>
            <strong>Quellcode</strong><br>
            <a href="https://github.com/MartinReisinger/fuel-tactical" target="_blank" style="color: var(--accent); text-decoration: none;">GitHub ↗</a><br><br>
            <span style="font-size:9px;color:var(--text-dim);">Offenlegung gem. § 25 MedienG. Privates, nicht-kommerzielles Informationsangebot.</span>
        `,
    },
    en: {
        brand: 'FUEL <span>TACTICAL</span>',
        fuelLabel: 'FUEL TYPE',
        fuels: { SUP: 'SUPER 95', DIE: 'DIESEL', GAS: 'CNG GAS' },
        plzPlaceholder: 'Enter postcode…',
        queryBtn: 'SEARCH',
        queryError: 'Postcode not found.',
        dbLabel: 'DB',
        topFive: 'TOP 5 IN VIEW',
        movemap: '— move the map —',
        noData: 'NO DATA',
        noStations: 'No stations in this area',
        apiError: 'API ERROR',
        topPrices: 'TOP 5 PRICES',
        stationsVisible: (n) => `${n} STATIONS IN VIEW`,
        topRegion: 'TOP 5 (REGION)',
        zoomIn: (n) => `Zoom in for markers (${n} found)`,
        priceScale: 'PRICE SCALE',
        nodeId: 'NODE ID',
        tabs: { '24h': '24H', '7d': '7 DAYS', '30d': 'MONTH', '365d': 'YEAR' },
        tableKeys: {
            fuel: 'FUEL',
            price: 'PRICE',
            address: 'ADDRESS',
            city: 'CITY',
            coords: 'COORDINATES',
            phone: 'PHONE',
            website: 'WEBSITE',
        },
        googleMaps: 'GOOGLE MAPS',
        appleMaps: 'APPLE MAPS',
        close: 'CLOSE',
        impressum: 'LEGAL NOTICE',
        impressumTitle: 'Legal Notice',
        noHistData: 'NO HISTORICAL DATA',
        impContent: `
            <strong>Operator</strong><br>
            Martin Reisinger<br>
            Linz, Austria<br>
            <a href="mailto:rezepte.home.web@gmail.com" style="color: var(--accent); text-decoration: none;">rezepte.home.web@gmail.com</a><br><br>
            <strong>What is this?</strong><br>
            A private hobby project – no ads, no subscriptions, no profit.
            Fuel prices come directly from the official
            <a href="https://api.e-control.at/sprit/1.0/doc/" target="_blank" style="color: var(--accent); text-decoration: none;">E-Control API ↗</a>.<br><br>
            <strong>Privacy</strong><br>
            I use the privacy-friendly analytics tool
            <a href="https://www.goatcounter.com" target="_blank" style="color: var(--accent); text-decoration: none;">GoatCounter</a>.
            No cookies are set and no personal data is stored.<br><br>
            <strong>Source Code</strong><br>
            <a href="https://github.com/MartinReisinger/fuel-tactical" target="_blank" style="color: var(--accent); text-decoration: none;">GitHub ↗</a><br><br>
            <span style="font-size:9px;color:var(--text-dim);">Private, non-commercial information service.</span>
        `,
    }
};

// Detect browser language; fall back to 'de'
function detectLang() {
    const lang = (navigator.language || navigator.userLanguage || 'de').substring(0, 2).toLowerCase();
    return lang === 'en' ? 'en' : 'de';
}

let currentLang = detectLang();
const t = () => TRANSLATIONS[currentLang];
