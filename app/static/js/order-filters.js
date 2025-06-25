/**
 * Orders page filter functionality
 * Handles filtering orders by type and status
 */

// Create a global namespace for the filters
window.OrderFilters = {
    activeFilters: {
        type: '',
        status: ''
    },
    
    // Apply filters function that can be called from other scripts
    applyFilters: function() {
        console.log('Applying filters:', this.activeFilters);
        
        const orderRows = document.querySelectorAll('.order-row');
        orderRows.forEach(row => {
            let showRow = true;
            
            // Check type filter
            if (this.activeFilters.type && row.dataset.type !== this.activeFilters.type) {
                showRow = false;
            }
            
            // Check status filter
            if (this.activeFilters.status && row.dataset.status !== this.activeFilters.status) {
                showRow = false;
            }
            
            // Show/hide row
            row.style.display = showRow ? '' : 'none';
        });
        
        // Count visible rows
        const visibleCount = [...orderRows].filter(row => row.style.display !== 'none').length;
        console.log(`Filter applied: ${visibleCount} orders shown`);
    }
};

document.addEventListener('DOMContentLoaded', function() {
    console.log('Order filters script loaded');
    
    // Filter buttons (All Orders)
    const filterButtons = document.querySelectorAll('.filter-btn');
    // Filter dropdowns (Type, Status)
    const filterSelects = document.querySelectorAll('.filter-select');
    // Reset filter button
    const resetFilterBtn = document.querySelector('.reset-filter-btn');
    
    // Active filters
    const activeFilters = {
        type: '',
        status: ''
    };
      // Handle filter button clicks (All Orders)
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            
            // Reset all filters
            window.OrderFilters.activeFilters.type = '';
            window.OrderFilters.activeFilters.status = '';
            
            // Reset select dropdowns
            filterSelects.forEach(select => {
                select.selectedIndex = 0;
            });
            
            // Show all orders
            const orderRows = document.querySelectorAll('.order-row');
            orderRows.forEach(row => {
                row.style.display = '';
            });
            
            console.log('Filters reset, showing all orders');
        });
    });
      // Handle filter select changes
    filterSelects.forEach(select => {
        select.addEventListener('change', function() {
            const filterType = this.dataset.filter;
            const filterValue = this.value;
            
            // Update active filters
            window.OrderFilters.activeFilters[filterType] = filterValue;
            
            // Remove active class from All Orders button
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Apply filters
            window.OrderFilters.applyFilters();
        });
    });
      // Handle reset filters button
    if (resetFilterBtn) {
        resetFilterBtn.addEventListener('click', function() {
            // Reset all filters
            window.OrderFilters.activeFilters.type = '';
            window.OrderFilters.activeFilters.status = '';
            
            // Reset select dropdowns
            filterSelects.forEach(select => {
                select.selectedIndex = 0;
            });
            
            // Add active class to All Orders button
            filterButtons.forEach(btn => {
                if (btn.dataset.filter === 'all') {
                    btn.classList.add('active');
                }
            });
            
            // Show all orders
            const orderRows = document.querySelectorAll('.order-row');
            orderRows.forEach(row => {
                row.style.display = '';
            });
            
            console.log('Filters reset, showing all orders');
        });
    }
  });
