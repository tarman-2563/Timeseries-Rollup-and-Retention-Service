// API Base URL
const API_URL = window.location.origin;

// Chart instance
let chart = null;

// DOM Elements
const elements = {
    metricSelect: document.getElementById('metricSelect'),
    rollupSelect: document.getElementById('rollupSelect'),
    timeRangeSelect: document.getElementById('timeRangeSelect'),
    refreshBtn: document.getElementById('refreshBtn'),
    status: document.getElementById('status'),
    dataTable: document.getElementById('dataTable')
};

// Initialize
async function init() {
    await loadMetrics();
    setupEventListeners();
    initChart();
}

// Setup event listeners
function setupEventListeners() {
    elements.metricSelect.addEventListener('change', loadData);
    elements.rollupSelect.addEventListener('change', loadData);
    elements.timeRangeSelect.addEventListener('change', loadData);
    elements.refreshBtn.addEventListener('click', loadData);
}

// Load available metrics
async function loadMetrics() {
    try {
        const response = await fetch(`${API_URL}/metrics/list?page=1&page_size=100`);
        const data = await response.json();
        
        elements.metricSelect.innerHTML = '';
        
        if (data.metrics && data.metrics.length > 0) {
            data.metrics.forEach(metric => {
                const option = document.createElement('option');
                option.value = metric.metric_name;
                option.textContent = metric.metric_name;
                elements.metricSelect.appendChild(option);
            });
            
            // Load data for first metric
            await loadData();
        } else {
            elements.metricSelect.innerHTML = '<option value="">No metrics available</option>';
        }
    } catch (error) {
        console.error('Error loading metrics:', error);
        showStatus('Error loading metrics', 'error');
    }
}

// Load data
async function loadData() {
    const metric = elements.metricSelect.value;
    const rollup = elements.rollupSelect.value;
    const timeRange = elements.timeRangeSelect.value;
    
    if (!metric) return;
    
    showStatus('Loading data...', 'loading');
    
    try {
        const { startTime, endTime } = getTimeRange(timeRange);
        let data;
        
        if (rollup === 'raw') {
            // Query raw data
            const response = await fetch(`${API_URL}/query/raw?metric_name=${metric}&start_time=${startTime}&end_time=${endTime}`);
            data = await response.json();
        } else {
            // Query rollup data
            const response = await fetch(`${API_URL}/query/rollup?metric_name=${metric}&start_time=${startTime}&end_time=${endTime}&window=${rollup}`);
            data = await response.json();
        }
        
        // Update chart
        updateChart(data, rollup);
        
        // Update table
        updateTable(data, rollup);
        
        showStatus(`Loaded ${data.points ? data.points.length : 0} data points`, 'success');
    } catch (error) {
        console.error('Error loading data:', error);
        showStatus('Error loading data', 'error');
    }
}

// Initialize chart
function initChart() {
    const ctx = document.getElementById('chart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Value',
                data: [],
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            }
        }
    });
}

// Update chart
function updateChart(data, rollup) {
    if (!chart || !data.points) return;
    
    const labels = data.points.map(p => formatTime(p.timestamp));
    const values = data.points.map(p => rollup === 'raw' ? p.value : p.avg);
    
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.data.datasets[0].label = `${data.metric_name} (${rollup})`;
    chart.update();
}

// Update table
function updateTable(data, rollup) {
    if (!data.points || data.points.length === 0) {
        elements.dataTable.innerHTML = '<tr><td colspan="2" style="text-align: center; color: #999;">No data available</td></tr>';
        return;
    }
    
    let html = '';
    data.points.forEach(point => {
        const value = rollup === 'raw' ? point.value : point.avg;
        html += `
            <tr>
                <td>${formatFullTime(point.timestamp)}</td>
                <td>${value !== null ? value.toFixed(2) : 'null'}</td>
            </tr>
        `;
    });
    
    elements.dataTable.innerHTML = html;
}

// Get time range
function getTimeRange(range) {
    const endTime = new Date();
    const startTime = new Date();
    
    switch (range) {
        case '1h':
            startTime.setHours(startTime.getHours() - 1);
            break;
        case '24h':
            startTime.setHours(startTime.getHours() - 24);
            break;
        case '7d':
            startTime.setDate(startTime.getDate() - 7);
            break;
    }
    
    return {
        startTime: startTime.toISOString(),
        endTime: endTime.toISOString()
    };
}

// Format time for chart
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format time for table
function formatFullTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

// Show status
function showStatus(message, type) {
    elements.status.textContent = message;
    elements.status.className = `status ${type}`;
    elements.status.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            elements.status.style.display = 'none';
        }, 3000);
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init);
