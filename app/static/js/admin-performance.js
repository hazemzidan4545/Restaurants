/**
 * Admin Dashboard Performance Optimizations
 * Handles lazy loading, caching, and performance monitoring
 */

class AdminPerformance {
    constructor() {
        this.cache = new Map();
        this.loadingStates = new Set();
        this.init();
    }

    init() {
        this.setupLazyLoading();
        this.setupTableOptimizations();
        this.setupSearchOptimizations();
        this.setupNavigationOptimizations();
        this.monitorPerformance();
    }

    /**
     * Setup lazy loading for images and content
     */
    setupLazyLoading() {
        // Intersection Observer for lazy loading
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('loading-skeleton');
                        img.classList.add('loaded');
                        imageObserver.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px 0px',
            threshold: 0.1
        });

        // Observe all lazy images
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });

        // Lazy load table rows for large datasets
        const tableObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const row = entry.target;
                    if (row.dataset.lazy) {
                        this.loadTableRowData(row);
                        tableObserver.unobserve(row);
                    }
                }
            });
        });

        document.querySelectorAll('tr[data-lazy]').forEach(row => {
            tableObserver.observe(row);
        });
    }

    /**
     * Optimize table performance for large datasets
     */
    setupTableOptimizations() {
        const tables = document.querySelectorAll('.admin-table');
        
        tables.forEach(table => {
            // Virtual scrolling for large tables
            if (table.rows.length > 100) {
                this.enableVirtualScrolling(table);
            }

            // Optimize table sorting
            const headers = table.querySelectorAll('th[data-sortable]');
            headers.forEach(header => {
                header.addEventListener('click', (e) => {
                    this.debounce(() => this.sortTable(table, header), 100)();
                });
            });
        });
    }

    /**
     * Setup optimized search functionality
     */
    setupSearchOptimizations() {
        const searchInputs = document.querySelectorAll('.search-input');
        
        searchInputs.forEach(input => {
            let searchTimeout;
            
            input.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                
                // Show loading state
                this.showSearchLoading(input);
                
                searchTimeout = setTimeout(() => {
                    this.performSearch(e.target.value, input);
                }, 300); // Debounce search
            });

            // Cache search results
            input.addEventListener('focus', () => {
                if (!this.cache.has('search-suggestions')) {
                    this.preloadSearchSuggestions();
                }
            });
        });
    }

    /**
     * Optimize navigation and page transitions
     */
    setupNavigationOptimizations() {
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            // Preload on hover
            link.addEventListener('mouseenter', () => {
                if (link.href && !this.cache.has(link.href)) {
                    this.preloadPage(link.href);
                }
            });

            // Add loading states
            link.addEventListener('click', (e) => {
                if (!link.classList.contains('active')) {
                    this.showNavigationLoading(link);
                }
            });
        });

        // Prefetch critical resources
        this.prefetchCriticalResources();
    }

    /**
     * Monitor and report performance metrics
     */
    monitorPerformance() {
        // Monitor page load performance
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = performance.getEntriesByType('navigation')[0];
                const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                
                if (loadTime > 3000) { // If load time > 3s
                    console.warn('Slow page load detected:', loadTime + 'ms');
                    this.optimizeForSlowConnection();
                }
            }, 0);
        });

        // Monitor memory usage
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                if (memory.usedJSHeapSize > 50 * 1024 * 1024) { // 50MB
                    console.warn('High memory usage detected');
                    this.cleanupMemory();
                }
            }, 30000); // Check every 30 seconds
        }
    }

    /**
     * Utility functions
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    showSearchLoading(input) {
        const container = input.closest('.search-box');
        if (container) {
            container.classList.add('loading');
        }
    }

    hideSearchLoading(input) {
        const container = input.closest('.search-box');
        if (container) {
            container.classList.remove('loading');
        }
    }

    showNavigationLoading(link) {
        link.classList.add('loading');
        
        // Remove loading state after navigation
        setTimeout(() => {
            link.classList.remove('loading');
        }, 2000);
    }

    async performSearch(query, input) {
        try {
            // Check cache first
            const cacheKey = `search-${query}`;
            if (this.cache.has(cacheKey)) {
                this.displaySearchResults(this.cache.get(cacheKey), input);
                return;
            }

            // Perform search
            const response = await fetch(`/admin/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            
            // Cache results
            this.cache.set(cacheKey, results);
            
            this.displaySearchResults(results, input);
        } catch (error) {
            console.error('Search error:', error);
        } finally {
            this.hideSearchLoading(input);
        }
    }

    displaySearchResults(results, input) {
        // Implementation for displaying search results
        console.log('Search results:', results);
    }

    async preloadPage(url) {
        if (this.loadingStates.has(url)) return;
        
        this.loadingStates.add(url);
        
        try {
            const response = await fetch(url, { method: 'HEAD' });
            if (response.ok) {
                this.cache.set(url, true);
            }
        } catch (error) {
            console.error('Preload error:', error);
        } finally {
            this.loadingStates.delete(url);
        }
    }

    prefetchCriticalResources() {
        const criticalUrls = [
            '/admin/dashboard',
            '/admin/orders',
            '/admin/meals',
            '/admin/services'
        ];

        criticalUrls.forEach(url => {
            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            document.head.appendChild(link);
        });
    }

    optimizeForSlowConnection() {
        // Reduce image quality
        document.querySelectorAll('img').forEach(img => {
            if (img.src && img.src.includes('unsplash')) {
                img.src = img.src.replace(/w=\d+/, 'w=300').replace(/h=\d+/, 'h=200');
            }
        });

        // Disable animations
        document.body.classList.add('reduced-motion');
    }

    cleanupMemory() {
        // Clear old cache entries
        if (this.cache.size > 50) {
            const entries = Array.from(this.cache.entries());
            entries.slice(0, 25).forEach(([key]) => {
                this.cache.delete(key);
            });
        }

        // Force garbage collection if available
        if (window.gc) {
            window.gc();
        }
    }

    loadTableRowData(row) {
        // Implementation for loading table row data
        row.classList.remove('loading-skeleton');
        row.removeAttribute('data-lazy');
    }

    enableVirtualScrolling(table) {
        // Implementation for virtual scrolling
        console.log('Virtual scrolling enabled for table:', table);
    }

    sortTable(table, header) {
        // Implementation for optimized table sorting
        console.log('Sorting table by:', header.textContent);
    }

    preloadSearchSuggestions() {
        // Implementation for preloading search suggestions
        console.log('Preloading search suggestions');
    }
}

// Initialize performance optimizations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AdminPerformance();
});

// Export for use in other modules
window.AdminPerformance = AdminPerformance;
