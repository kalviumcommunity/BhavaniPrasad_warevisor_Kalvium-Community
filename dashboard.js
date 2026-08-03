// Manager Dashboard Interactive JavaScript Engine

document.addEventListener('DOMContentLoaded', () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    lucide.createIcons();
  }

  // Render Charts
  initStockOverviewChart();
  initCategoryDonutChart();

  // Search Filter Handler
  setupSearchFilter();

  // Export CSV Handler
  document.getElementById('exportBtn')?.addEventListener('click', exportDashboardSummaryCSV);
});

// Chart 1: Stock Overview Line Chart
let stockChartInstance = null;

const chartDataOptions = {
  year: {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
    data: [28000, 32000, 29000, 37000, 34000, 41000, 43500, 45780]
  },
  quarter: {
    labels: ['May', 'Jun', 'Jul', 'Aug'],
    data: [34000, 41000, 43500, 45780]
  },
  month: {
    labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
    data: [42000, 43200, 44800, 45780]
  }
};

function initStockOverviewChart() {
  const ctx = document.getElementById('stockOverviewChart')?.getContext('2d');
  if (!ctx) return;

  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(59, 130, 246, 0.3)');
  gradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

  stockChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: chartDataOptions.year.labels,
      datasets: [{
        label: 'Stock Count',
        data: chartDataOptions.year.data,
        borderColor: '#3b82f6',
        borderWidth: 3,
        backgroundColor: gradient,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleFont: { family: 'Inter', size: 13, weight: 'bold' },
          bodyFont: { family: 'Inter', size: 13 },
          padding: 12,
          cornerRadius: 8,
          displayColors: false,
          callbacks: {
            label: (context) => `Stock: ${context.parsed.y.toLocaleString()} units`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 12 }, color: '#64748b' }
        },
        y: {
          grid: { color: '#f1f5f9' },
          ticks: {
            font: { family: 'Inter', size: 12 },
            color: '#64748b',
            callback: (val) => val >= 1000 ? `${val / 1000}k` : val
          }
        }
      }
    }
  });
}

function updateStockTrendChart() {
  const period = document.getElementById('periodFilter').value;
  if (stockChartInstance && chartDataOptions[period]) {
    stockChartInstance.data.labels = chartDataOptions[period].labels;
    stockChartInstance.data.datasets[0].data = chartDataOptions[period].data;
    stockChartInstance.update();
  }
}

// Chart 2: Category Donut Chart
function initCategoryDonutChart() {
  const ctx = document.getElementById('categoryDonutChart')?.getContext('2d');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Electronics', 'Clothing', 'Home & Kitchen', 'Beauty', 'Others'],
      datasets: [{
        data: [41, 25, 18, 10, 6],
        backgroundColor: [
          '#3b82f6',
          '#f59e0b',
          '#10b981',
          '#ef4444',
          '#8b5cf6'
        ],
        borderWidth: 3,
        borderColor: '#ffffff',
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            label: (ctx) => `${ctx.label}: ${ctx.parsed}%`
          }
        }
      },
      cutout: '72%'
    }
  });
}

// Live Search Filter Handler
function setupSearchFilter() {
  const searchInput = document.getElementById('dashboardSearch');
  if (!searchInput) return;

  searchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    
    // Filter warehouse list
    document.querySelectorAll('.warehouse-item').forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(query) ? 'flex' : 'none';
    });

    // Filter movements feed
    document.querySelectorAll('.movement-item').forEach(item => {
      const text = item.textContent.toLowerCase();
      item.style.display = text.includes(query) ? 'flex' : 'none';
    });
  });
}

// Modal Handlers
function openLowStockModal() {
  document.getElementById('lowStockModal')?.classList.add('active');
}

function closeLowStockModal() {
  document.getElementById('lowStockModal')?.classList.remove('active');
}

function openWarehouseModal() {
  document.getElementById('warehouseModal')?.classList.add('active');
}

function closeWarehouseModal() {
  document.getElementById('warehouseModal')?.classList.remove('active');
}

// Export Summary CSV
function exportDashboardSummaryCSV() {
  const csvContent = "data:text/csv;charset=utf-8," 
    + "Metric,Value,Subtext\n"
    + "Total Products,1248,All Warehouses\n"
    + "Total Stock,45780,All Warehouses\n"
    + "Low Stock Products,86,Reorder Soon\n"
    + "Out of Stock,12,Action Required\n\n"
    + "Warehouse Name,Location,Manager,Total Stock\n"
    + "Central Warehouse,New Delhi,Amit Sen,18500\n"
    + "North Zone Warehouse,Delhi,Simran Kaur,12300\n"
    + "South Zone Warehouse,Bangalore,Suresh Babu,8850\n";

  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "Manager_Dashboard_Summary.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportMovementsCSV() {
  exportDashboardSummaryCSV();
}

function exportCategoryData() {
  alert("Category Breakdown Exported:\n- Electronics: 41%\n- Clothing: 25%\n- Home & Kitchen: 18%\n- Beauty: 10%\n- Others: 6%");
}
