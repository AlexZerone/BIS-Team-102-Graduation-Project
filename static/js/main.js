
/**
 * Error Handler - Captures and displays JS errors
 */
class ErrorHandler {
    static init() {
        window.addEventListener('error', this.handleError.bind(this));
        window.addEventListener('unhandledrejection', this.handlePromiseError.bind(this));
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
        errorContainer.setAttribute('role', 'alert');
        errorContainer.innerHTML = `
            <strong>Oops!</strong> Something went wrong. Please try again later.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const alertArea = document.querySelector('.alert-container');
        if (alertArea) {
            alertArea.appendChild(errorContainer);
        } else {
            document.body.prepend(errorContainer);
        }

        // Auto-dismiss after 8 seconds
        setTimeout(() => {
            if (errorContainer.parentNode) {
                const bsAlert = new bootstrap.Alert(errorContainer);
                bsAlert.close();
            }
        }, 8000);
    }
}

/**
 * Performance Monitor - Tracks page and resource load times
 */
class PerformanceMonitor {
    static init() {
        this.measurePageLoad();
        this.measureNetworkRequests();
    }

    static measurePageLoad() {
        window.addEventListener('load', () => {
            if (window.performance) {
                if (performance.getEntriesByType) {
                    const nav = performance.getEntriesByType('navigation')[0];
                    if (nav) {
                        const loadTime = Math.round(nav.loadEventEnd - nav.startTime);
                        console.log(`📊 Page Load Time: ${loadTime}ms`);
                        return;
                    }
                }
                
                // Fallback for older browsers
                const timing = performance.timing;
                const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
                console.log(`📊 Page Load Time: ${pageLoadTime}ms`);
            }
        });
    }

    static measureNetworkRequests() {
        if (window.PerformanceObserver) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (entry.initiatorType !== 'xmlhttprequest' && entry.initiatorType !== 'fetch') return;
                    console.log(`📡 Resource: ${entry.name.split('/').pop()} - ${Math.round(entry.duration)}ms`);
                });
            });
            
            observer.observe({ entryTypes: ['resource'] });
        }
    }
}

/**
 * ThemeManager - Handles theme switching between light and dark modes
 */
class ThemeManager {
    static init() {
        this.themeSwitcher = document.getElementById('themeSwitcher');
        if (!this.themeSwitcher) return;
        
        this.icon = this.themeSwitcher.querySelector('i');
        this.htmlElement = document.documentElement;
        
        this.setInitialTheme();
        this.attachEventListeners();
    }
    
    static setInitialTheme() {
        // Check for saved theme preference or respect OS preference
        const savedTheme = localStorage.getItem('theme');
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Set initial theme
        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            this.htmlElement.setAttribute('data-bs-theme', 'dark');
            this.icon.classList.replace('fa-moon', 'fa-sun');
        }
    }
    
    static attachEventListeners() {
        // Toggle theme on click
        this.themeSwitcher.addEventListener('click', () => {
            const currentTheme = this.htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            
            this.htmlElement.setAttribute('data-bs-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Toggle icon
            if (newTheme === 'dark') {
                this.icon.classList.replace('fa-moon', 'fa-sun');
            } else {
                this.icon.classList.replace('fa-sun', 'fa-moon');
            }
        });
    }
}

/**
 * UX Utilities - Various UI enhancements
 */
class UXUtils {
    static init() {
        this.setupScrollToTop();
        this.setupLoadingSpinner();
        this.setupPasswordToggles();
        this.setupSmoothScrolling();
        this.setupFlashMessages();
        this.setupFormValidation();
    }
    
    static setupScrollToTop() {
        const scrollToTopBtn = document.getElementById('scrollToTop');
        if (!scrollToTopBtn) return;
        
        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollToTopBtn.classList.remove('d-none');
            } else {
                scrollToTopBtn.classList.add('d-none');
            }
        });
        
        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    static setupLoadingSpinner() {
        const spinner = document.getElementById('loading-spinner');
        if (!spinner) return;
        
        document.addEventListener('click', (e) => {
            const target = e.target.closest('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript"]):not([href^="mailto"]):not([href^="tel"])');
            if (target && target.getAttribute('href') && target.host === window.location.host) {
                spinner.classList.remove('d-none');
                
                // Safety timeout to hide spinner if page doesn't load
                setTimeout(() => {
                    if (!spinner.classList.contains('d-none')) {
                        spinner.classList.add('d-none');
                    }
                }, 10000);
            }
        });
    }
    
    static setupPasswordToggles() {
        document.addEventListener('click', (e) => {
            const toggleButton = e.target.closest('.toggle-password');
            if (!toggleButton) return;
            
            const input = toggleButton.closest('.input-group').querySelector('input');
            const icon = toggleButton.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.replace('fa-eye', 'fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.replace('fa-eye-slash', 'fa-eye');
            }
        });
    }
    
    static setupSmoothScrolling() {
        document.addEventListener('click', (e) => {
            const anchor = e.target.closest('a[href^="#"]:not([href="#"])');
            if (!anchor) return;
            
            const targetId = anchor.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    }
    
    static setupFlashMessages() {
        // Auto-hide flash messages after 5 seconds
        const flashMessages = document.querySelectorAll('.alert:not(.alert-important)');
        flashMessages.forEach(message => {
            setTimeout(() => {
                if (message.parentNode) {
                    const bsAlert = new bootstrap.Alert(message);
                    bsAlert.close();
                }
            }, 5000);
        });
    }
    
    static setupFormValidation() {
        // Apply Bootstrap's form validation
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
}
let mimetype = 'application/javascript'; // Define it properly

/**
 * Service Worker Registration - For offline capability & PWA support
 */
class ServiceWorkerManager {
    
    static init() {
        if ('serviceWorker' in navigator) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/js/sw.js', mimetype= 'application/javascript',{
                    type: 'module', // Valid options: 'classic' or 'module'
                    scope: '/register'
                } )
                    .then(registration => {
                        console.log('ServiceWorker registration successful with scope: ', registration.scope);
                    })
                    .catch(err => {
                        console.error('ServiceWorker registration failed: ', err);
                    });
            });
        }
    }
}

/**
 * Initialize all application features when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', () => {
    // Core functionality
    ErrorHandler.init();
    PerformanceMonitor.init();
    ThemeManager.init();
    UXUtils.init();
    ServiceWorkerManager.init();
    
    // Log application start
    console.log(`🚀 Sec Era application initialized - ${new Date().toLocaleString()}`);
});