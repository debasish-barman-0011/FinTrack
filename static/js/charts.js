/**
 * FinTrack - Charts Module
 * Handles all chart visualizations including creation, updates, and exports
 */

// Chart.js global configuration
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.plugins.tooltip.backgroundColor = '#2c3e50';
Chart.defaults.plugins.tooltip.titleColor = '#ecf0f1';
Chart.defaults.plugins.tooltip.bodyColor = '#ecf0f1';
Chart.defaults.plugins.tooltip.padding = 10;
Chart.defaults.plugins.tooltip.cornerRadius = 8;

// Store chart instances for later updates/cleanup
const chartInstances = {};

/**
 * Create or update a pie chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data with labels and values
 * @param {Object} options - Additional chart options
 */
function createPieChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    
    // Destroy existing chart instance if it exists
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    const defaultColors = ['#27ae60', '#e74c3c', '#f39c12', '#3498db', '#9b59b6', 
                           '#1abc9c', '#e67e22', '#2c3e50', '#95a5a6', '#16a085'];
    
    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.colors || defaultColors.slice(0, data.labels.length),
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: options.legendPosition || 'bottom',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 10,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            ...options
        }
    });
    
    chartInstances[canvasId] = chart;
    return chart;
}

/**
 * Create or update a bar chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data with labels and datasets
 * @param {Object} options - Additional chart options
 */
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: options.legendPosition || 'top',
                    labels: {
                        usePointStyle: true,
                        boxWidth: 10
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            return `${label}: ₹${value.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    },
                    title: {
                        display: options.yAxisTitle ? true : false,
                        text: options.yAxisTitle || 'Amount (₹)'
                    }
                },
                x: {
                    title: {
                        display: options.xAxisTitle ? true : false,
                        text: options.xAxisTitle || ''
                    }
                }
            },
            ...options
        }
    });
    
    chartInstances[canvasId] = chart;
    return chart;
}

/**
 * Create or update a line chart (for trends)
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data with labels and datasets
 * @param {Object} options - Additional chart options
 */
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: data.datasets.map(dataset => ({
                ...dataset,
                tension: 0.4,
                fill: dataset.fill !== undefined ? dataset.fill : true,
                pointRadius: 4,
                pointHoverRadius: 6
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: options.legendPosition || 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.raw || 0;
                            return `${label}: ₹${value.toLocaleString()}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + value.toLocaleString();
                        }
                    }
                }
            },
            ...options
        }
    });
    
    chartInstances[canvasId] = chart;
    return chart;
}

/**
 * Create a donut chart (variation of pie chart)
 * @param {string} canvasId - Canvas element ID
 * @param {Object} data - Chart data
 * @param {Object} options - Additional options
 */
function createDonutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return null;
    
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    const defaultColors = ['#27ae60', '#e74c3c', '#f39c12', '#3498db', '#9b59b6'];
    
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.colors || defaultColors,
                borderWidth: 0,
                hoverOffset: 10,
                cutout: options.cutout || '60%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: options.legendPosition || 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ₹${value.toLocaleString()} (${percentage}%)`;
                        }
                    }
                }
            },
            ...options
        }
    });
    
    chartInstances[canvasId] = chart;
    return chart;
}

/**
 * Convert chart to base64 image (for PDF export)
 * @param {string} canvasId - Canvas element ID
 * @returns {string} Base64 image data
 */
function chartToBase64(canvasId) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    return canvas.toDataURL('image/png');
}

/**
 * Export all charts on page as images
 * @returns {Object} Object with chart IDs as keys and base64 images as values
 */
function exportAllCharts() {
    const charts = {};
    const canvases = document.querySelectorAll('canvas');
    
    canvases.forEach((canvas, index) => {
        const chartId = canvas.id || `chart_${index}`;
        charts[chartId] = canvas.toDataURL('image/png');
    });
    
    return charts;
}

/**
 * Update existing chart with new data
 * @param {string} canvasId - Canvas element ID
 * @param {Object} newData - New chart data
 */
function updateChart(canvasId, newData) {
    if (chartInstances[canvasId]) {
        const chart = chartInstances[canvasId];
        
        if (newData.labels) {
            chart.data.labels = newData.labels;
        }
        
        if (newData.datasets) {
            chart.data.datasets = newData.datasets;
        } else if (newData.values) {
            chart.data.datasets[0].data = newData.values;
        }
        
        chart.update();
    }
}

/**
 * Create monthly trend chart (income vs expenses)
 * @param {string} canvasId - Canvas element ID
 * @param {Array} data - Array of monthly data objects
 */
function createMonthlyTrendChart(canvasId, data) {
    const labels = data.map(item => item.month);
    const incomeData = data.map(item => item.income);
    const expenseData = data.map(item => item.expenses);
    
    return createLineChart(canvasId, {
        labels: labels,
        datasets: [
            {
                label: 'Income',
                data: incomeData,
                borderColor: '#27ae60',
                backgroundColor: 'rgba(39, 174, 96, 0.1)',
                borderWidth: 2
            },
            {
                label: 'Expenses',
                data: expenseData,
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: 2
            }
        ]
    }, {
        yAxisTitle: 'Amount (₹)',
        xAxisTitle: 'Month'
    });
}

/**
 * Create category distribution chart
 * @param {string} canvasId - Canvas element ID
 * @param {Object} categoryData - Object with category names as keys and amounts as values
 * @param {string} chartType - 'pie' or 'donut'
 */
function createCategoryChart(canvasId, categoryData, chartType = 'pie') {
    const labels = Object.keys(categoryData);
    const values = Object.values(categoryData);
    
    if (chartType === 'donut') {
        return createDonutChart(canvasId, { labels, values });
    }
    
    return createPieChart(canvasId, { labels, values });
}

/**
 * Destroy all charts and cleanup
 */
function destroyAllCharts() {
    Object.keys(chartInstances).forEach(key => {
        if (chartInstances[key]) {
            chartInstances[key].destroy();
            delete chartInstances[key];
        }
    });
}

/**
 * Resize all charts (useful for responsive layouts)
 */
function resizeAllCharts() {
    Object.values(chartInstances).forEach(chart => {
        if (chart && chart.resize) {
            chart.resize();
        }
    });
}

// Listen for window resize to adjust charts
window.addEventListener('resize', () => {
    resizeAllCharts();
});

// Export functions for global use
window.FinTrackCharts = {
    createPieChart,
    createBarChart,
    createLineChart,
    createDonutChart,
    createMonthlyTrendChart,
    createCategoryChart,
    chartToBase64,
    exportAllCharts,
    updateChart,
    destroyAllCharts,
    resizeAllCharts
};