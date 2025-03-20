
// Error Handler
class ErrorHandler {
    static init() {
        window.addEventListener('error', this.handleError);
        window.addEventListener('unhandledrejection', this.handlePromiseError);
    }

    static handleError(error) {
        console.error('Error:', error);
        this.showErrorMessage();
    }

    static handlePromiseError(event) {
        console.error('Promise Error:', event.reason);
        this.showErrorMessage();
    }

    static showErrorMessage() {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger alert-dismissible fade show';
        errorContainer.innerHTML = `
            <strong>Oops!</strong> Something went wrong. Please try again later.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.alert-container').appendChild(errorContainer);
    }
}

// Performance Monitor
const performanceMonitor = {
    init() {
        this.measurePageLoad();
        this.measureNetworkRequests();
    },

    measurePageLoad() {
        window.addEventListener('load', () => {
            const timing = performance.timing;
            const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Page Load Time: ${pageLoadTime}ms`);
        });
    },

    measureNetworkRequests() {
        const observer = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                console.log(`Resource Load Time: ${entry.name} - ${entry.duration}ms`);
            });
        });
        observer.observe({ entryTypes: ['resource'] });
    }
};

// Initialize
$(document).ready(function() {
    // Auto-hide flash messages
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Loading state handling
    $(document).on({
        ajaxStart: function() { $('#loading-spinner').show(); },
        ajaxStop: function() { $('#loading-spinner').hide(); }
    });

    // Theme switcher
    $('#themeSwitcher').click(function() {
        $('body').toggleClass('dark-theme');
        localStorage.setItem('theme', 
            $('body').hasClass('dark-theme') ? 'dark' : 'light'
        );
    });

    // Check saved theme
    if (localStorage.getItem('theme') === 'dark') {
        $('body').addClass('dark-theme');
    }

    // Initialize error handler and performance monitor
    ErrorHandler.init();
    performanceMonitor.init();
});

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('ServiceWorker registered'))
            .catch(err => console.log('ServiceWorker registration failed:', err));
    });
}
