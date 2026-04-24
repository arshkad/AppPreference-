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
  // ── Donut chart ────────────────────────────────────────────────────────────────
function renderPie() {
    const d = appData.overall_dist;
    const legEl = document.getElementById('pieLegend');
    legEl.innerHTML = d.labels.map((l, i) =>
      `<span class="legend-item"><span class="legend-dot" style="background:${CAT_COLORS[l]}"></span>${l} ${d.values[i]}%</span>`
    ).join('');
  
    if (pieChart) pieChart.destroy();
    pieChart = new Chart(document.getElementById('pieChart'), {
      type: 'doughnut',
      data: {
        labels: d.labels,
        datasets: [{
          data: d.values,
          backgroundColor: d.labels.map(l => CAT_COLORS[l]),
          borderWidth: 1,
          borderColor: 'rgba(255,255,255,0.15)',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: {
          legend: { display: false },
          tooltip: { callbacks: { label: c => ' ' + c.label + ': ' + c.parsed + '%' } },
        },
      },
    });
  }
  
  // ── Line chart ─────────────────────────────────────────────────────────────────
  function renderLine() {
    const t = appData.monthly_trend;
    const cats = Object.keys(t.series);
  
    const legEl = document.getElementById('lineLegend');
    legEl.innerHTML = cats.map(c =>
      `<span class="legend-item"><span class="legend-dot" style="background:${CAT_COLORS[c]}"></span>${c}</span>`
    ).join('');
  
    const datasets = cats.map(c => ({
      label: c,
      data: t.series[c],
      borderColor: CAT_COLORS[c],
      backgroundColor: 'transparent',
      borderWidth: 2,
      pointRadius: 3,
      pointBackgroundColor: CAT_COLORS[c],
      tension: 0.4,
    }));
  
    if (lineChart) lineChart.destroy();
    lineChart = new Chart(document.getElementById('lineChart'), {
      type: 'line',
      data: { labels: t.months, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 10 }, color: '#888' } },
          y: {
            grid: { color: 'rgba(128,128,128,0.1)' },
            ticks: { font: { size: 10 }, color: '#888', callback: v => v.toFixed(1) + 'h' },
            min: 0, max: 2.8,
          },
        },
      },
    });
  }
  
  // ── Data table ─────────────────────────────────────────────────────────────────
  function renderTable() {
    const rows = appData.category_totals;
    const tb = document.getElementById('tableBody');
    tb.innerHTML = rows.map(r => {
      const [bg, fg] = CAT_TAGS[r.category] || ['#eee', '#333'];
      const barW = Math.round(r.engagement_rate * 1.2);
      const barColor = CAT_COLORS[r.category] || '#888';
      return `
        <tr>
          <td><span class="cat-tag" style="background:${bg};color:${fg}">${r.category}</span></td>
          <td class="mono">${r.users.toLocaleString()}</td>
          <td>
            <div class="bar-cell">
              <div class="mini-bar" style="width:${barW}px;background:${barColor}"></div>
              <span class="mono">${r.engagement_rate}%</span>
            </div>
          </td>
          <td class="mono">${r.avg_hours.toFixed(2)}h</td>
          <td class="mono">${r.median_hours.toFixed(2)}h</td>
          <td style="color:var(--text2);font-size:11px">${r.top_group}</td>
        </tr>`;
    }).join('');
  }