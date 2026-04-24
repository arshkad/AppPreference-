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