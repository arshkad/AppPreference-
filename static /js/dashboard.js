/* dashboard.js — gets data from /api/data (Flask/Python) and renders all charts */

const CAT_COLORS = {
    Social:        '#378ADD',
    Utility:       '#639922',
    Entertainment: '#EF9F27',
    Productivity:  '#7F77DD',
    Health:        '#1D9E75',
  };
  
  const CAT_TAGS = {
    Social:        ['#E6F1FB', '#0C447C'],
    Utility:       ['#EAF3DE', '#27500A'],
    Entertainment: ['#FAEEDA', '#633806'],
    Productivity:  ['#EEEDFE', '#3C3489'],
    Health:        ['#E1F5EE', '#085041'],
  };
  
  const GROUP_COLORS = ['#378ADD', '#7F77DD', '#1D9E75', '#EF9F27'];
  
  let barChart, pieChart, lineChart;
  let appData = null;
  let currentFilter = 'age';
  // ── Stat cards ─────────────────────────────────────────────────────────────────
function renderStats() {
    const m = appData.meta;
    document.getElementById('s-points').textContent   = m.total_points.toLocaleString();
    document.getElementById('s-nulls').textContent    = m.dropped_nulls.toLocaleString();
    document.getElementById('s-missing').textContent  = m.missing_pct + '% of raw';
    document.getElementById('s-outliers').textContent = m.capped_outliers.toLocaleString();
    document.getElementById('s-cats').textContent     = m.categories;
    document.getElementById('tableCount').textContent = 'n = ' + m.total_points.toLocaleString();
    document.getElementById('footerCount').textContent = m.total_points.toLocaleString() + ' clean records · April 2026';
  }
  
  // ── Bar chart ──────────────────────────────────────────────────────────────────
  function renderBar(filter) {
    const keyMap = { age: 'by_age', gender: 'by_gender', region: 'by_region' };
    const descMap = {
      age:    'Usage share by age group (%)',
      gender: 'Usage share by gender (%)',
      region: 'Usage share by region (%)',
    };
    const d = appData[keyMap[filter]];
    document.getElementById('barDesc').textContent = descMap[filter];
  
    // Legend
    const legEl = document.getElementById('barLegend');
    legEl.innerHTML = d.groups.map((g, i) =>
      `<span class="legend-item"><span class="legend-dot" style="background:${GROUP_COLORS[i]}"></span>${g}</span>`
    ).join('');
  
    const datasets = d.groups.map((g, i) => ({
      label: g,
      data: d.values[i],
      backgroundColor: GROUP_COLORS[i] + 'BB',
      borderColor:     GROUP_COLORS[i],
      borderWidth: 0.5,
    }));
  
    if (barChart) barChart.destroy();
    barChart = new Chart(document.getElementById('barChart'), {
      type: 'bar',
      data: { labels: d.categories, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#888' } },
          y: {
            grid: { color: 'rgba(128,128,128,0.1)' },
            ticks: { font: { size: 10 }, color: '#888', callback: v => v + '%' },
            max: 55,
          },
        },
      },
    });
  }