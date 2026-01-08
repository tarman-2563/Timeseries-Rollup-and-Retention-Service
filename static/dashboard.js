const API_URL = window.location.origin;

let chart = null;

const elements = {
    metricSelect: document.getElementById('metricSelect'),
    rollupSelect: document.getElementById('rollupSelect'),
    timeRangeSelect: document.getElementById('timeRangeSelect'),
    refreshBtn: document.getElementById('refreshBtn'),
    status: document.getElementById('status'),
    dataTable: document.getElementById('dataTable')
};

async function init() {
    await loadMetrics();
    setupEventListeners();
    initChart();
}

function setupEventListeners() {
    elements.metricSelect.addEventListener('change', loadData);
    elements.rollupSelect.addEventListener('change', loadData);
    elements.timeRangeSelect.addEventListener('change', loadData);
    elements.refreshBtn.addEventListener('click', loadData);
}

async function loadMetrics() {
    try {
        const url = `${API_URL}/metrics/names`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        elements.metricSelect.innerHTML = '';
        
        if (data.metrics && data.metrics.length > 0) {
            // Filter to only show cpu_usage
            const filteredMetrics = data.metrics.filter(metricName => metricName === 'cpu_usage');
            
            if (filteredMetrics.length > 0) {
                filteredMetrics.forEach(metricName => {
                    const option = document.createElement('option');
                    option.value = metricName;
                    option.textContent = metricName;
                    elements.metricSelect.appendChild(option);
                });
                
                showStatus(`Loaded ${filteredMetrics.length} metric (${data.total_records || 0} total records)`, 'success');
                await loadData();
            } else {
                elements.metricSelect.innerHTML = '<option value="">cpu_usage not found</option>';
                showStatus('cpu_usage metric not found in database', 'error');
            }
        } else {
            elements.metricSelect.innerHTML = '<option value="">No metrics available</option>';
            const msg = data.total_records === 0 
                ? 'Database is empty. Please ingest some metrics first.' 
                : 'No metrics found in database';
            showStatus(msg, 'error');
        }
    } 
    catch (error) {
        console.error('Error loading metrics:', error);
        elements.metricSelect.innerHTML = '<option value="">Error loading metrics</option>';
        showStatus(`Error loading metrics: ${error.message}`, 'error');
    }
}

async function loadData() {
    const metric = elements.metricSelect.value;
    const rollup = elements.rollupSelect.value;
    const timeRange = elements.timeRangeSelect.value;
    
    if (!metric) return;
    
    showStatus('Loading data...', 'loading');
    
    try {
        const { startTime, endTime } = getTimeRange(timeRange);
        let data;
        let response;
        let url;
        
        if (rollup === 'raw') {
            url = `${API_URL}/query/raw?metric_name=${metric}&start_time=${startTime}&end_time=${endTime}`;
        } else {
            url = `${API_URL}/query/rollup?metric_name=${metric}&start_time=${startTime}&end_time=${endTime}&window=${rollup}`;
        }
        
        response = await fetch(url);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
        }
        
        data = await response.json();
        
        updateChart(data, rollup);
        updateTable(data, rollup);
        
        const pointCount = data.points ? data.points.length : 0;
        if (pointCount === 0) {
            showStatus(`No data found for ${timeRange} (${startTime.split('T')[0]} to ${endTime.split('T')[0]})`, 'error');
        } else {
            showStatus(`Loaded ${pointCount} data points`, 'success');
        }
    }
    catch (error) {
        console.error('Error loading data:', error);
        showStatus(`Error: ${error.message}`, 'error');
        
        if (chart) {
            chart.data.labels = [];
            chart.data.datasets[0].data = [];
            chart.update();
        }
        elements.dataTable.innerHTML = '<tr><td colspan="2" style="text-align: center; color: #999;">Error loading data</td></tr>';
    }
}

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

function updateChart(data, rollup) {
    if (!chart) return;
    
    if (!data || !data.points || data.points.length === 0) {
        chart.data.labels = [];
        chart.data.datasets[0].data = [];
        chart.update();
        return;
    }
    
    const labels = data.points.map(p => formatTime(p.timestamp));
    const values = data.points.map(p => rollup === 'raw' ? p.value : p.avg);
    
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.data.datasets[0].label = `${data.metric_name} (${rollup})`;
    chart.data.datasets[0].borderColor = '#667eea';
    chart.data.datasets[0].backgroundColor = 'rgba(102, 126, 234, 0.1)';
    chart.update();
}

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

function getTimeRange(range) {
    let endTime = new Date();
    let startTime = new Date();
    
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
        case '30d':
            startTime.setDate(startTime.getDate() - 30);
            break;
        case 'all':
            startTime.setFullYear(2020);
            break;
        case 'manual_2026':
            startTime = new Date('2026-01-01T00:00:00Z');
            endTime = new Date('2026-12-31T23:59:59Z');
            break;
        case 'manual_2025':
            startTime = new Date('2025-01-01T00:00:00Z');
            endTime = new Date('2025-12-31T23:59:59Z');
            break;
    }
    
    return {
        startTime: startTime.toISOString(),
        endTime: endTime.toISOString()
    };
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

function formatFullTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

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

document.addEventListener('DOMContentLoaded', init);
