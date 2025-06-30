/**
 * Admin Dashboard Performance Optimizations
 * Handles lazy loading, caching, and performance monitoring
 */

class AdminPerformance {
    constructor() {
        this.cache = new Map();
        this.loadingStates = new Set();
        this.activeFilters = new Set();
        this.currentView = 'grid'; // or 'table'
        this.init();
    }

    init() {
        this.setupLazyLoading();
        this.setupTableOptimizations();
        this.setupSearchOptimizations();
        this.setupNavigationOptimizations();
        this.setupFilters();
        this.setupViewToggle();
        this.setupSorting();
        this.setupQuickFilters();
        this.setupDeleteHandlers();
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
        const searchInput = document.getElementById('menuSearch');
        if (!searchInput) return;

        let searchTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            
            // Show loading state
            this.showSearchLoading(searchInput);
            
            searchTimeout = setTimeout(() => {
                this.applyFilters();
                this.hideSearchLoading(searchInput);
            }, 300); // Debounce search for better performance
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

    setupFilters() {
        // Category filter
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => this.applyFilters());
        }

        // Status filter
        const statusFilter = document.getElementById('statusFilter');
        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.applyFilters());
        }

        // Sort filter
        const sortBy = document.getElementById('sortBy');
        if (sortBy) {
            sortBy.addEventListener('change', () => this.applyFilters());
        }

        // Items per page
        const itemsPerPage = document.getElementById('itemsPerPage');
        if (itemsPerPage) {
            itemsPerPage.addEventListener('change', () => this.applyFilters());
        }

        // Clear all filters
        const clearAllBtn = document.getElementById('clearAllFilters');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', () => this.clearAllFilters());
        }
    }

    setupViewToggle() {
        const gridViewBtn = document.getElementById('gridViewBtn');
        const tableViewBtn = document.getElementById('tableViewBtn');
        const gridView = document.getElementById('gridView');
        const tableView = document.getElementById('tableView');

        if (gridViewBtn && tableViewBtn) {
            gridViewBtn.addEventListener('click', () => {
                this.currentView = 'grid';
                gridViewBtn.classList.add('active');
                tableViewBtn.classList.remove('active');
                gridView.style.display = 'block';
                tableView.style.display = 'none';
            });

            tableViewBtn.addEventListener('click', () => {
                this.currentView = 'table';
                tableViewBtn.classList.add('active');
                gridViewBtn.classList.remove('active');
                tableView.style.display = 'block';
                gridView.style.display = 'none';
            });
        }
    }

    setupSorting() {
        const headers = document.querySelectorAll('th[data-sort]');
        headers.forEach(header => {
            header.addEventListener('click', () => {
                const sortKey = header.dataset.sort;
                this.sortItems(sortKey);
            });
        });
    }

    setupQuickFilters() {
        const quickFilters = document.querySelectorAll('.quick-filter-pill');
        quickFilters.forEach(filter => {
            filter.addEventListener('click', () => {
                filter.classList.toggle('active');
                this.applyFilters();
            });
        });
    }

    setupDeleteHandlers() {
        const deleteButtons = document.querySelectorAll('.delete-item');
        const deleteModal = document.getElementById('deleteConfirmModal');
        const deleteForm = document.getElementById('deleteForm');

        deleteButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const itemId = e.currentTarget.dataset.itemId;
                deleteForm.action = `/admin/menu/items/${itemId}/delete`;
                new bootstrap.Modal(deleteModal).show();
            });
        });
    }

    applyFilters() {
        const searchQuery = document.getElementById('menuSearch')?.value.toLowerCase() || '';
        const categoryId = document.getElementById('categoryFilter')?.value || '';
        const status = document.getElementById('statusFilter')?.value || '';
        const sortValue = document.getElementById('sortBy')?.value || '';

        // Get active quick filters
        const activeQuickFilters = Array.from(document.querySelectorAll('.quick-filter-pill.active'))
            .map(filter => filter.dataset.filter);

        // Get all menu items based on current view
        const menuItems = this.currentView === 'grid' 
            ? document.querySelectorAll('.menu-item-card:not(.add-menu-item-card)')
            : document.querySelectorAll('.menu-item-row');

        let visibleCount = 0;
        menuItems.forEach(item => {
            const itemName = item.dataset.name?.toLowerCase() || '';
            const itemCategory = item.dataset.category || '';
            const itemStatus = item.dataset.status || '';
            const itemPrice = parseFloat(item.dataset.price || '0');
            const itemStock = parseInt(item.dataset.stock || '0');
            const itemPopularity = parseInt(item.dataset.popularity || '0');
            const isNew = item.dataset.isNew === 'true';

            // Apply search filter
            const matchesSearch = !searchQuery || 
                                itemName.includes(searchQuery);

            // Apply category filter
            const matchesCategory = !categoryId || itemCategory === categoryId;

            // Apply status filter
            const matchesStatus = !status || itemStatus === status;

            // Apply quick filters
            const matchesQuickFilters = activeQuickFilters.length === 0 || activeQuickFilters.every(filter => {
                switch (filter) {
                    case 'available':
                        return itemStatus === 'available';
                    case 'low_stock':
                        return itemStock <= 10 && itemStock > 0;
                    case 'high_price':
                        return itemPrice >= 100;
                    case 'new_items':
                        return isNew;
                    case 'popular':
                        return itemPopularity >= 8;
                    default:
                        return true;
                }
            });

            // Show/hide item based on all filters
            const shouldShow = matchesSearch && matchesCategory && matchesStatus && matchesQuickFilters;
            item.style.display = shouldShow ? '' : 'none';
            if (shouldShow) visibleCount++;
        });

        // Update filter count badge
        const filterCountBadge = document.getElementById('filterCountBadge');
        const filterCount = document.getElementById('filterCount');
        if (filterCountBadge && filterCount) {
            const activeFilterCount = (searchQuery ? 1 : 0) + 
                                   (categoryId ? 1 : 0) + 
                                   (status ? 1 : 0) + 
                                   activeQuickFilters.length;
            
            filterCountBadge.style.display = activeFilterCount > 0 ? '' : 'none';
            filterCount.textContent = activeFilterCount;
        }

        // Update search results text
        const searchResultsText = document.getElementById('searchResultsText');
        if (searchResultsText) {
            if (visibleCount === 0) {
                searchResultsText.textContent = 'No items found matching your criteria';
            } else {
                searchResultsText.textContent = `Showing ${visibleCount} items`;
            }
        }

        // Apply sorting if specified
        if (sortValue) {
            this.sortItems(sortValue);
        }
    }

    sortItems(sortKey) {
        const container = this.currentView === 'grid' 
            ? document.querySelector('.menu-items-grid')
            : document.querySelector('.menu-table tbody');

        if (!container) return;

        const items = Array.from(this.currentView === 'grid' 
            ? container.querySelectorAll('.menu-item-card:not(.add-menu-item-card)')
            : container.querySelectorAll('.menu-item-row'));

        items.sort((a, b) => {
            const aValue = this.getSortValue(a, sortKey);
            const bValue = this.getSortValue(b, sortKey);

            if (sortKey.endsWith('_desc')) {
                return bValue.localeCompare(aValue);
            }
            return aValue.localeCompare(bValue);
        });

        // Clear and re-append sorted items
        const addNewCard = container.querySelector('.add-menu-item-card');
        container.innerHTML = '';
        items.forEach(item => container.appendChild(item));
        if (addNewCard && this.currentView === 'grid') {
            container.appendChild(addNewCard);
        }
    }

    getSortValue(item, sortKey) {
        switch (sortKey) {
            case 'name_asc':
            case 'name_desc':
                return item.dataset.name || '';
            case 'price_asc':
            case 'price_desc':
                return (parseFloat(item.dataset.price || '0')).toString().padStart(10, '0');
            case 'created_asc':
            case 'created_desc':
                return item.dataset.created || '';
            default:
                return '';
        }
    }

    clearAllFilters() {
        // Reset search
        const searchInput = document.getElementById('menuSearch');
        if (searchInput) searchInput.value = '';

        // Reset select filters
        ['categoryFilter', 'statusFilter', 'sortBy', 'itemsPerPage'].forEach(id => {
            const select = document.getElementById(id);
            if (select) select.selectedIndex = 0;
        });

        // Reset quick filters
        document.querySelectorAll('.quick-filter-pill.active').forEach(filter => {
            filter.classList.remove('active');
        });

        // Apply cleared filters
        this.applyFilters();
    }
}

// Initialize performance optimizations when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AdminPerformance();
});

// Export for use in other modules
window.AdminPerformance = AdminPerformance;
