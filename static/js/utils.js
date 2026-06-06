/**
 * FinTrack - Utility Functions
 * Helper functions for common operations
 */

// Format currency in Indian Rupees
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(amount);
}

// Format date to local string
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'loadingSpinner';
        loadingDiv.innerHTML = '<div class="loading-spinner"></div>';
        element.style.position = 'relative';
        element.appendChild(loadingDiv);
    }
}

// Hide loading spinner
function hideLoading() {
    const spinner = document.getElementById('loadingSpinner');
    if (spinner) {
        spinner.remove();
    }
}

// Show notification toast
function showNotification(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `flash flash-${type}`;
    toast.textContent = message;
    
    const container = document.querySelector('.flash-messages');
    if (container) {
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 5000);
    }
}

// Validate form inputs
function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return true;
    
    let isValid = true;
    const inputs = form.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        const rule = rules[input.name];
        if (rule) {
            if (rule.required && !input.value) {
                showFieldError(input, rule.message || 'This field is required');
                isValid = false;
            } else if (rule.min && parseFloat(input.value) < rule.min) {
                showFieldError(input, `Value must be at least ${rule.min}`);
                isValid = false;
            } else if (rule.max && parseFloat(input.value) > rule.max) {
                showFieldError(input, `Value must not exceed ${rule.max}`);
                isValid = false;
            } else if (rule.pattern && !rule.pattern.test(input.value)) {
                showFieldError(input, rule.message || 'Invalid format');
                isValid = false;
            } else {
                clearFieldError(input);
            }
        }
    });
    
    return isValid;
}

// Show field error
function showFieldError(input, message) {
    input.classList.add('error');
    const errorDiv = input.parentElement.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.textContent = message;
    } else {
        const error = document.createElement('div');
        error.className = 'form-error';
        error.textContent = message;
        input.parentElement.appendChild(error);
    }
}

// Clear field error
function clearFieldError(input) {
    input.classList.remove('error');
    const errorDiv = input.parentElement.querySelector('.form-error');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Debounce function for search inputs
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// Export to CSV
function exportToCSV(data, filename = 'export.csv') {
    const headers = Object.keys(data[0]);
    const csvRows = [];
    
    csvRows.push(headers.join(','));
    
    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            return `"${String(value).replace(/"/g, '""')}"`;
        });
        csvRows.push(values.join(','));
    }
    
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Copy to clipboard
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
    } catch (err) {
        console.error('Failed to copy:', err);
        showNotification('Failed to copy', 'danger');
    }
}

// Get query parameters from URL
function getQueryParams() {
    const params = {};
    const queryString = window.location.search;
    const urlParams = new URLSearchParams(queryString);
    
    for (const [key, value] of urlParams) {
        params[key] = value;
    }
    
    return params;
}

// Set query parameters in URL without reload
function setQueryParams(params) {
    const url = new URL(window.location.href);
    Object.keys(params).forEach(key => {
        if (params[key]) {
            url.searchParams.set(key, params[key]);
        } else {
            url.searchParams.delete(key);
        }
    });
    window.history.pushState({}, '', url);
}

// Make API request with error handling
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'danger');
        throw error;
    }
}

// Export utility functions
window.FinTrackUtils = {
    formatCurrency,
    formatDate,
    showLoading,
    hideLoading,
    showNotification,
    validateForm,
    debounce,
    exportToCSV,
    copyToClipboard,
    getQueryParams,
    setQueryParams,
    apiRequest
};