// Error Handler
class ErrorHandler {
    static init() {
        window.addEventListener('error', this.handleError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseError.bind(this));
    }

    static handleError(error) {
        console.error('Error:', error);
        ErrorHandler.showErrorMessage();
    }

    static handlePromiseError(event) {
        console.error('Promise Error:', event.reason);
        ErrorHandler.showErrorMessage();
    }

    static showErrorMessage() {
        const errorContainer = document.createElement('div');
        errorContainer.className = 'alert alert-danger alert-dismissible fade show';
        errorContainer.innerHTML = `
            <strong>Oops!</strong> Something went wrong. Please try again later.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        const alertArea = document.querySelector('.alert-container');
        if (alertArea) {
            alertArea.appendChild(errorContainer);
        } else {
            document.body.prepend(errorContainer);
        }
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
            if (performance.getEntriesByType) {
                const nav = performance.getEntriesByType('navigation')[0];
                if (nav) {
                    console.log(`Page Load Time: ${Math.round(nav.loadEventEnd - nav.startTime)}ms`);
                    return;
                }
            }
            // fallback
            const timing = performance.timing;
            const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`Page Load Time: ${pageLoadTime}ms`);
        });
    },

    measureNetworkRequests() {
        if (window.PerformanceObserver) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.initiatorType !== 'xmlhttprequest' && entry.initiatorType !== 'fetch') return;
                    console.log(`Resource Load Time: ${entry.name} - ${Math.round(entry.duration)}ms`);
                });
            });
            observer.observe({ entryTypes: ['resource'] });
        }
    }
};

// Utility: Smooth scroll to anchor links
function enableSmoothScroll() {
    $(document).on('click', 'a[href^="#"]', function(e) {
        const target = $(this.getAttribute('href'));
        if (target.length) {
            e.preventDefault();
            $('html, body').animate({ scrollTop: target.offset().top - 80 }, 600);
        }
    });
}

// Utility: Show/hide password toggle
function enablePasswordToggle() {
    $(document).on('click', '.toggle-password', function() {
        const input = $(this).closest('.input-group').find('input');
        if (input.attr('type') === 'password') {
            input.attr('type', 'text');
            $(this).find('i').removeClass('fa-eye').addClass('fa-eye-slash');
        } else {
            input.attr('type', 'password');
            $(this).find('i').removeClass('fa-eye-slash').addClass('fa-eye');
        }
    });
}

// Initialize
$(document).ready(function() {
    // Auto-hide flash messages
    setTimeout(function() {
        $('.alert').not('.alert-important').fadeOut('slow');
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
        $(this).find('i').toggleClass('fa-moon fa-sun');
    });

    // Set correct icon on load
    if (localStorage.getItem('theme') === 'dark') {
        $('body').addClass('dark-theme');
        $('#themeSwitcher i').removeClass('fa-moon').addClass('fa-sun');
    } else {
        $('#themeSwitcher i').removeClass('fa-sun').addClass('fa-moon');
    }

    // Initialize error handler and performance monitor
    ErrorHandler.init();
    performanceMonitor.init();
    enableSmoothScroll();
    enablePasswordToggle();
});

// Service Worker Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('ServiceWorker registered'))
            .catch(err => console.log('ServiceWorker registration failed:', err));
    });
}

    // Theme Switcher
    document.addEventListener('DOMContentLoaded', function() {
        // Theme Switcher
        const themeSwitcher = document.getElementById('themeSwitcher');
        const icon = themeSwitcher.querySelector('i');
        const htmlElement = document.documentElement;
        
        // Check for saved theme preference or respect OS preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            htmlElement.setAttribute('data-bs-theme', 'dark');
            icon.classList.replace('fa-moon', 'fa-sun');
        }
        
        // Toggle theme on click
        themeSwitcher.addEventListener('click', function() {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Toggle icon
            if (newTheme === 'dark') {
                icon.classList.replace('fa-moon', 'fa-sun');
            } else {
                icon.classList.replace('fa-sun', 'fa-moon');
            }
        });
        
        // Scroll to Top Button
        const scrollToTopBtn = document.getElementById('scrollToTop');
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollToTopBtn.classList.remove('d-none');
            } else {
                scrollToTopBtn.classList.add('d-none');
            }
        });
        
        scrollToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Show loading spinner when navigating between pages
        document.addEventListener('click', function(e) {
            const target = e.target.closest('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript"]):not([href^="mailto"]):not([href^="tel"])');
            if (target && target.getAttribute('href') && target.host === window.location.host) {
                const spinner = document.getElementById('loading-spinner');
                spinner.classList.remove('d-none');
                setTimeout(() => {
                    if (spinner.classList.contains('d-none') === false) {
                        spinner.classList.add('d-none');
                    }
                }, 10000); // Safety timeout
            }
        });
    });