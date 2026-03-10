// js/modal.js — Dossier modal + chart logic

let activeChart    = null;
let currentStation = null;
let currentPeriod  = '24h';

async function openDossier(s) {
    currentStation = s;
    currentPeriod  = '24h';

    document.getElementById('modal').style.display = 'flex';
    document.getElementById('d-id').textContent    = `${t().nodeId}: ${s.id}`;
    document.getElementById('d-title').textContent = s.name;

    const fuel  = document.getElementById('fuelSelect').selectedOptions[0].text;
    const price = s.amount ? `€ ${s.amount.toFixed(3)}` : '—';

    document.getElementById('link-google').href = `https://www.google.com/maps/dir/?api=1&destination=${s.latitude},${s.longitude}`;
    document.getElementById('link-apple').href  = `http://maps.apple.com/?daddr=${s.latitude},${s.longitude}`;
    document.getElementById('link-google').textContent = t().googleMaps;
    document.getElementById('link-apple').textContent  = t().appleMaps;
    document.getElementById('btn-close-modal').textContent = t().close;

    const phoneVal = s.telephone
        ? `<a href="tel:${s.telephone}" style="color:var(--accent);text-decoration:none">${s.telephone}</a>`
        : '—';
    const webVal = s.website
        ? `<a href="${s.website.startsWith('http') ? s.website : 'http://' + s.website}" target="_blank" style="color:var(--accent);text-decoration:none">${s.website}</a>`
        : '—';

    const keys = t().tableKeys;
    const rows = [
        [keys.fuel,    fuel],
        [keys.price,   price],
        [keys.address, s.address],
        [keys.city,    `${s.postal_code} ${s.city}`],
        [keys.coords,  `${s.latitude?.toFixed(5)}, ${s.longitude?.toFixed(5)}`],
        [keys.phone,   phoneVal],
        [keys.website, webVal],
    ];

    document.getElementById('d-table').innerHTML = rows
        .map(([k, v]) => `<div class="d-row"><span class="d-key">${k}</span><span class="d-val">${v}</span></div>`)
        .join('');

    // Reset tabs
    document.querySelectorAll('.chart-tab').forEach((tab, i) => {
        tab.classList.toggle('active', i === 0);
        const periods = ['24h', '7d', '30d', '365d'];
        tab.textContent = t().tabs[periods[i]];
    });

    await loadChart('24h');
}

function closeModal() {
    document.getElementById('modal').style.display = 'none';
    if (activeChart) { activeChart.destroy(); activeChart = null; }
}

async function switchPeriod(period, btn) {
    document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    currentPeriod = period;
    await loadChart(period);
}

async function loadChart(period) {
    if (!currentStation) return;
    const fuel   = document.getElementById('fuelSelect').value;
    const params = new URLSearchParams({ station_id: currentStation.id, fuel, period });

    let history = [];
    try {
        const r = await fetch(`/api/history?${params}`);
        history  = await r.json();
    } catch(e) {}

    if (activeChart) { activeChart.destroy(); activeChart = null; }

    const now     = new Date();
    const minDate = new Date();
    if (period === '24h')  minDate.setHours(now.getHours() - 24);
    else if (period === '7d')  minDate.setDate(now.getDate() - 7);
    else if (period === '30d') minDate.setDate(now.getDate() - 30);
    else if (period === '365d') minDate.setDate(now.getDate() - 365);

    const formatData = (valKey) => history.map(h => ({
        x: new Date(h.bucket.replace(' ', 'T') + 'Z'),
        y: h[valKey]
    }));

    const canvas = document.getElementById('price-chart');
    activeChart  = new Chart(canvas, {
        type: 'line',
        data: {
            datasets: [{
                label: t().tableKeys.price,
                data: formatData('avg_price'),
                borderColor: '#2979ff',
                backgroundColor: 'rgba(41,121,255,0.08)',
                pointRadius: 2,
                fill: true,
                borderWidth: 2,
                stepped: 'middle'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            plugins: {
                legend: { labels: { color: '#555', font: { family: 'IBM Plex Mono', size: 9 }, boxWidth: 20 } },
                tooltip: {
                    backgroundColor: '#111', borderColor: '#222', borderWidth: 1,
                    titleColor: '#2979ff', bodyColor: '#e8e8e8',
                    titleFont: { family: 'IBM Plex Mono', size: 10 },
                    bodyFont:  { family: 'IBM Plex Mono', size: 10 },
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: €${ctx.parsed.y?.toFixed(3) ?? '—'}`
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    min: minDate, max: now,
                    time: {
                        tooltipFormat: 'yyyy-MM-dd HH:00',
                        displayFormats: { hour: 'HH:00', day: 'MMM dd', week: 'MMM dd', month: 'MMM yyyy' }
                    },
                    ticks: { color: '#444', font: { family: 'IBM Plex Mono', size: 8 }, maxTicksLimit: 6 },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                },
                y: {
                    min: 1.0, max: 3.0,
                    ticks: { color: '#444', font: { family: 'IBM Plex Mono', size: 9 }, callback: v => `€${v.toFixed(3)}` },
                    grid: { color: 'rgba(255,255,255,0.04)' }
                }
            }
        }
    });

    if (history.length === 0) {
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#333';
        ctx.font = '11px IBM Plex Mono';
        ctx.textAlign = 'center';
        ctx.fillText(t().noHistData, canvas.width / 2, canvas.height / 2);
    }
}
