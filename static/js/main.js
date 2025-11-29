// WorkX - Main JavaScript File

// Utility Functions
const showLoading = (element) => {
    if (element) {
        element.innerHTML = '<div class="loading">Loading...</div>';
    }
};

const showError = (message) => {
    alert(message);
};

const showSuccess = (message) => {
    alert(message);
};

// API Helper Functions
const api = {
    async get(url) {
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async post(url, body, isFormData = false) {
        try {
            const options = {
                method: 'POST',
                body: isFormData ? body : JSON.stringify(body)
            };

            if (!isFormData) {
                options.headers = {
                    'Content-Type': 'application/json'
                };
            }

            const response = await fetch(url, options);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
};

// Price Calculation
const calculatePrice = async (workType, pages) => {
    try {
        const data = await api.post('/api/calculate_price', {
            work_type: workType,
            pages: parseInt(pages)
        });
        
        return data;
    } catch (error) {
        showError('Failed to calculate price: ' + error.message);
        return null;
    }
};

// Format Currency
const formatCurrency = (amount) => {
    return `₹${amount}`;
};

// Format Date
const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-IN', options);
};

// Validate Form
const validateForm = (formId) => {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const inputs = form.querySelectorAll('[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'var(--danger-color)';
        } else {
            input.style.borderColor = 'var(--border-color)';
        }
    });
    
    return isValid;
};

// File Upload Handler
const handleFileUpload = (inputElement, maxSize = 16 * 1024 * 1024) => {
    const files = inputElement.files;
    const validFiles = [];
    
    for (let file of files) {
        if (file.size > maxSize) {
            showError(`File ${file.name} is too large. Maximum size is 16MB.`);
            continue;
        }
        validFiles.push(file);
    }
    
    return validFiles;
};

// Debounce Function
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Status Badge Generator
const getStatusBadge = (status) => {
    const statusClasses = {
        'Pending': 'status-pending',
        'Assigned': 'status-assigned',
        'In Progress': 'status-in-progress',
        'Completed': 'status-completed',
        'Delivered': 'status-completed'
    };
    
    const className = statusClasses[status] || 'status-pending';
    return `<span class="status-badge ${className}">${status}</span>`;
};

// Local Storage Helper
const storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Storage Error:', error);
            return false;
        }
    },

    get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Storage Error:', error);
            return null;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (error) {
            console.error('Storage Error:', error);
            return false;
        }
    }
};

// Save recent task IDs
const saveRecentTaskId = (taskId) => {
    let recentTasks = storage.get('recentTasks') || [];
    
    // Add to beginning of array
    recentTasks.unshift(taskId);
    
    // Keep only last 10
    recentTasks = recentTasks.slice(0, 10);
    
    // Remove duplicates
    recentTasks = [...new Set(recentTasks)];
    
    storage.set('recentTasks', recentTasks);
};

// Get recent task IDs
const getRecentTaskIds = () => {
    return storage.get('recentTasks') || [];
};

// Smooth Scroll
const smoothScroll = (target) => {
    const element = document.querySelector(target);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
};

// Copy to Clipboard
const copyToClipboard = (text) => {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess('Copied to clipboard!');
        }).catch(() => {
            showError('Failed to copy to clipboard');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showSuccess('Copied to clipboard!');
        } catch (err) {
            showError('Failed to copy to clipboard');
        }
        document.body.removeChild(textArea);
    }
};

// Initialize tooltips (if needed)
const initTooltips = () => {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = element.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = element.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
        });
        
        element.addEventListener('mouseleave', () => {
            const tooltips = document.querySelectorAll('.tooltip');
            tooltips.forEach(t => t.remove());
        });
    });
};

// Notification System
const notify = {
    show(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `;
        
        if (type === 'success') {
            notification.style.borderLeft = '4px solid var(--success-color)';
        } else if (type === 'error') {
            notification.style.borderLeft = '4px solid var(--danger-color)';
        } else {
            notification.style.borderLeft = '4px solid var(--primary-color)';
        }
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    },

    success(message) {
        this.show(message, 'success');
    },

    error(message) {
        this.show(message, 'error');
    },

    info(message) {
        this.show(message, 'info');
    }
};

// Loading Spinner
const spinner = {
    show(target = 'body') {
        const spinner = document.createElement('div');
        spinner.id = 'globalSpinner';
        spinner.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                        background: rgba(0, 0, 0, 0.5); display: flex; 
                        align-items: center; justify-content: center; z-index: 9999;">
                <div style="background: white; padding: 2rem; border-radius: 12px; 
                            text-align: center;">
                    <div style="width: 50px; height: 50px; border: 4px solid #f3f4f6; 
                                border-top: 4px solid var(--primary-color); 
                                border-radius: 50%; animation: spin 1s linear infinite; 
                                margin: 0 auto 1rem;"></div>
                    <p>Loading...</p>
                </div>
            </div>
        `;
        document.body.appendChild(spinner);
    },

    hide() {
        const spinner = document.getElementById('globalSpinner');
        if (spinner) {
            spinner.remove();
        }
    }
};

// Add animation keyframes to document
const addAnimations = () => {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
};

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    addAnimations();
    
    // Add mobile menu toggle if needed
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }
});

// Export functions for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        api,
        calculatePrice,
        formatCurrency,
        formatDate,
        validateForm,
        handleFileUpload,
        debounce,
        getStatusBadge,
        storage,
        saveRecentTaskId,
        getRecentTaskIds,
        smoothScroll,
        copyToClipboard,
        notify,
        spinner
    };
}
