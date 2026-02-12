/**
 * Admin Advanced Search & Filtering
 * Provides comprehensive search capabilities across all admin sections
 */

let currentSearchEntity = 'users';
let currentSearchFilters = {};
let currentSearchPage = 0;
const RESULTS_PER_PAGE = 50;

// Initialize search functionality
function initializeSearch() {
    setupGlobalSearch();
    setupAdvancedSearch();
    loadFilterOptions();
}

// Global Search (search bar in header)
function setupGlobalSearch() {
    const searchInput = document.getElementById('globalSearchInput');
    const searchButton = document.getElementById('globalSearchButton');
    const searchResults = document.getElementById('globalSearchResults');
    
    if (!searchInput) return;
    
    // Debounced search
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            hideGlobalSearchResults();
            return;
        }
        
        searchTimeout = setTimeout(() => {
            performGlobalSearch(query);
        }, 300);
    });
    
    // Search button click
    if (searchButton) {
        searchButton.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query.length >= 2) {
                performGlobalSearch(query);
            }
        });
    }
    
    // Close results when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.global-search-container')) {
            hideGlobalSearchResults();
        }
    });
}

async function performGlobalSearch(query) {
    try {
        const response = await fetch(`/api/admin/search/global?q=${encodeURIComponent(query)}`);
        const result = await response.json();
        
        if (result.success) {
            displayGlobalSearchResults(result.data);
        }
    } catch (error) {
        console.error('Global search error:', error);
    }
}

function displayGlobalSearchResults(data) {
    const resultsContainer = document.getElementById('globalSearchResults');
    if (!resultsContainer) return;
    
    if (data.total_results === 0) {
        resultsContainer.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-search"></i>
                <p>No results found for "${data.query}"</p>
            </div>
        `;
        resultsContainer.style.display = 'block';
        return;
    }
    
    let html = '<div class="global-search-results">';
    
    // Users
    if (data.users.length > 0) {
        html += '<div class="search-category">';
        html += '<h4><i class="fas fa-users"></i> Users</h4>';
        data.users.forEach(user => {
            html += `
                <div class="search-result-item" onclick="viewUser(${user.id})">
                    <div class="result-title">${user.name}</div>
                    <div class="result-meta">${user.email} • ${user.role}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Programs
    if (data.programs.length > 0) {
        html += '<div class="search-category">';
        html += '<h4><i class="fas fa-trophy"></i> Programs</h4>';
        data.programs.forEach(program => {
            html += `
                <div class="search-result-item" onclick="viewProgram(${program.id})">
                    <div class="result-title">${program.title}</div>
                    <div class="result-meta">${program.type} • ${program.status}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Meetings
    if (data.meetings.length > 0) {
        html += '<div class="search-category">';
        html += '<h4><i class="fas fa-video"></i> Meetings</h4>';
        data.meetings.forEach(meeting => {
            html += `
                <div class="search-result-item" onclick="viewMeeting(${meeting.id})">
                    <div class="result-title">${meeting.title}</div>
                    <div class="result-meta">${meeting.status} • ${new Date(meeting.scheduled_at).toLocaleDateString()}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Leads
    if (data.leads.length > 0) {
        html += '<div class="search-category">';
        html += '<h4><i class="fas fa-envelope"></i> Leads</h4>';
        data.leads.forEach(lead => {
            html += `
                <div class="search-result-item" onclick="viewLeadDetail(${lead.id})">
                    <div class="result-title">${lead.name}</div>
                    <div class="result-meta">${lead.email} • ${lead.type}</div>
                </div>
            `;
        });
        html += '</div>';
    }
    
    html += '</div>';
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
}

function hideGlobalSearchResults() {
    const resultsContainer = document.getElementById('globalSearchResults');
    if (resultsContainer) {
        resultsContainer.style.display = 'none';
    }
}

// Advanced Search (section-specific)
function setupAdvancedSearch() {
    const advancedSearchBtn = document.getElementById('advancedSearchBtn');
    const advancedSearchPanel = document.getElementById('advancedSearchPanel');
    const closeSearchPanel = document.getElementById('closeSearchPanel');
    const applyFiltersBtn = document.getElementById('applyFiltersBtn');
    const clearFiltersBtn = document.getElementById('clearFiltersBtn');
    
    if (advancedSearchBtn) {
        advancedSearchBtn.addEventListener('click', () => {
            advancedSearchPanel.style.display = 'block';
        });
    }
    
    if (closeSearchPanel) {
        closeSearchPanel.addEventListener('click', () => {
            advancedSearchPanel.style.display = 'none';
        });
    }
    
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', applyAdvancedFilters);
    }
    
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearAdvancedFilters);
    }
}

async function loadFilterOptions() {
    try {
        const response = await fetch('/api/admin/search/filter-options');
        const result = await response.json();
        
        if (result.success) {
            window.filterOptions = result.data;
        }
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

function showAdvancedSearch(entityType) {
    currentSearchEntity = entityType;
    const panel = document.getElementById('advancedSearchPanel');
    if (!panel) return;
    
    // Update panel title
    const title = document.getElementById('searchPanelTitle');
    if (title) {
        title.textContent = `Search ${entityType.charAt(0).toUpperCase() + entityType.slice(1)}`;
    }
    
    // Load appropriate filters
    loadFiltersForEntity(entityType);
    
    panel.style.display = 'block';
}

function loadFiltersForEntity(entityType) {
    const filtersContainer = document.getElementById('advancedFiltersContainer');
    if (!filtersContainer || !window.filterOptions) return;
    
    let html = '';
    
    // Text search
    html += `
        <div class="filter-group">
            <label>Search Term</label>
            <input type="text" id="filter_query" class="filter-input" placeholder="Search...">
        </div>
    `;
    
    // Entity-specific filters
    if (entityType === 'users') {
        html += `
            <div class="filter-group">
                <label>Role</label>
                <select id="filter_role" class="filter-select">
                    <option value="">All Roles</option>
                    ${window.filterOptions.users.roles.map(role => 
                        `<option value="${role}">${role}</option>`
                    ).join('')}
                </select>
            </div>
        `;
    } else if (entityType === 'programs') {
        html += `
            <div class="filter-group">
                <label>Type</label>
                <select id="filter_type" class="filter-select">
                    <option value="">All Types</option>
                    ${window.filterOptions.programs.types.map(type => 
                        `<option value="${type}">${type}</option>`
                    ).join('')}
                </select>
            </div>
            <div class="filter-group">
                <label>Status</label>
                <select id="filter_status" class="filter-select">
                    <option value="">All Statuses</option>
                    ${window.filterOptions.programs.statuses.map(status => 
                        `<option value="${status}">${status}</option>`
                    ).join('')}
                </select>
            </div>
        `;
    } else if (entityType === 'applications') {
        html += `
            <div class="filter-group">
                <label>Status</label>
                <select id="filter_status" class="filter-select">
                    <option value="">All Statuses</option>
                    ${window.filterOptions.applications.statuses.map(status => 
                        `<option value="${status}">${status}</option>`
                    ).join('')}
                </select>
            </div>
        `;
    } else if (entityType === 'meetings') {
        html += `
            <div class="filter-group">
                <label>Status</label>
                <select id="filter_status" class="filter-select">
                    <option value="">All Statuses</option>
                    ${window.filterOptions.meetings.statuses.map(status => 
                        `<option value="${status}">${status}</option>`
                    ).join('')}
                </select>
            </div>
            <div class="filter-group">
                <label>Access Type</label>
                <select id="filter_access_type" class="filter-select">
                    <option value="">All Types</option>
                    ${window.filterOptions.meetings.access_types.map(type => 
                        `<option value="${type}">${type.replace('_', ' ')}</option>`
                    ).join('')}
                </select>
            </div>
        `;
    } else if (entityType === 'leads') {
        html += `
            <div class="filter-group">
                <label>Type</label>
                <select id="filter_type" class="filter-select">
                    <option value="">All Types</option>
                    ${window.filterOptions.leads.types.map(type => 
                        `<option value="${type}">${type}</option>`
                    ).join('')}
                </select>
            </div>
            <div class="filter-group">
                <label>Read Status</label>
                <select id="filter_is_read" class="filter-select">
                    <option value="">All</option>
                    <option value="true">Read</option>
                    <option value="false">Unread</option>
                </select>
            </div>
        `;
    }
    
    // Date range filters
    html += `
        <div class="filter-group">
            <label>Date From</label>
            <input type="date" id="filter_date_from" class="filter-input">
        </div>
        <div class="filter-group">
            <label>Date To</label>
            <input type="date" id="filter_date_to" class="filter-input">
        </div>
    `;
    
    filtersContainer.innerHTML = html;
}

async function applyAdvancedFilters() {
    // Collect filter values
    const filters = {};
    
    const query = document.getElementById('filter_query')?.value;
    if (query) filters.q = query;
    
    const role = document.getElementById('filter_role')?.value;
    if (role) filters.role = role;
    
    const type = document.getElementById('filter_type')?.value;
    if (type) filters.type = type;
    
    const status = document.getElementById('filter_status')?.value;
    if (status) filters.status = status;
    
    const accessType = document.getElementById('filter_access_type')?.value;
    if (accessType) filters.access_type = accessType;
    
    const isRead = document.getElementById('filter_is_read')?.value;
    if (isRead) filters.is_read = isRead;
    
    const dateFrom = document.getElementById('filter_date_from')?.value;
    if (dateFrom) filters.date_from = dateFrom;
    
    const dateTo = document.getElementById('filter_date_to')?.value;
    if (dateTo) filters.date_to = dateTo;
    
    currentSearchFilters = filters;
    currentSearchPage = 0;
    
    // Perform search
    await performAdvancedSearch();
    
    // Close panel
    document.getElementById('advancedSearchPanel').style.display = 'none';
    
    showToast('Filters applied');
}

function clearAdvancedFilters() {
    currentSearchFilters = {};
    currentSearchPage = 0;
    
    // Clear all filter inputs
    document.querySelectorAll('.filter-input, .filter-select').forEach(input => {
        input.value = '';
    });
    
    // Reload data without filters
    performAdvancedSearch();
    
    showToast('Filters cleared');
}

async function performAdvancedSearch() {
    const endpoint = `/api/admin/search/${currentSearchEntity}`;
    const params = new URLSearchParams({
        ...currentSearchFilters,
        limit: RESULTS_PER_PAGE,
        offset: currentSearchPage * RESULTS_PER_PAGE
    });
    
    try {
        const response = await fetch(`${endpoint}?${params}`);
        const result = await response.json();
        
        if (result.success) {
            displayAdvancedSearchResults(result.data);
        }
    } catch (error) {
        console.error('Advanced search error:', error);
        showToast('Search failed', 'error');
    }
}

function displayAdvancedSearchResults(data) {
    const resultsContainer = document.getElementById('searchResultsContainer');
    if (!resultsContainer) return;
    
    if (data.results.length === 0) {
        resultsContainer.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <p>No results found</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="search-results-list">';
    
    data.results.forEach(item => {
        html += renderSearchResultItem(item, currentSearchEntity);
    });
    
    html += '</div>';
    
    // Pagination
    if (data.total > RESULTS_PER_PAGE) {
        html += renderPagination(data);
    }
    
    resultsContainer.innerHTML = html;
}

function renderSearchResultItem(item, entityType) {
    if (entityType === 'users') {
        return `
            <div class="search-result-card" onclick="viewUser(${item.id})">
                <div class="result-header">
                    <h4>${item.full_name}</h4>
                    <span class="badge badge-${item.role}">${item.role}</span>
                </div>
                <div class="result-body">
                    <p>${item.email}</p>
                    ${item.company ? `<p>${item.company}</p>` : ''}
                </div>
                <div class="result-footer">
                    <span><i class="fas fa-calendar"></i> ${new Date(item.created_at).toLocaleDateString()}</span>
                </div>
            </div>
        `;
    } else if (entityType === 'programs') {
        return `
            <div class="search-result-card" onclick="viewProgram(${item.id})">
                <div class="result-header">
                    <h4>${item.title}</h4>
                    <span class="badge badge-${item.status}">${item.status}</span>
                </div>
                <div class="result-body">
                    <p>${item.description}</p>
                    <span class="badge">${item.type}</span>
                </div>
            </div>
        `;
    }
    // Add more entity types as needed
    
    return '';
}

function renderPagination(data) {
    const totalPages = Math.ceil(data.total / RESULTS_PER_PAGE);
    const currentPage = currentSearchPage;
    
    let html = '<div class="pagination">';
    html += `<span class="pagination-info">Showing ${data.offset + 1}-${Math.min(data.offset + RESULTS_PER_PAGE, data.total)} of ${data.total}</span>`;
    html += '<div class="pagination-buttons">';
    
    if (currentPage > 0) {
        html += `<button onclick="goToPage(${currentPage - 1})" class="pagination-btn"><i class="fas fa-chevron-left"></i> Previous</button>`;
    }
    
    if (data.has_more) {
        html += `<button onclick="goToPage(${currentPage + 1})" class="pagination-btn">Next <i class="fas fa-chevron-right"></i></button>`;
    }
    
    html += '</div></div>';
    
    return html;
}

function goToPage(page) {
    currentSearchPage = page;
    performAdvancedSearch();
}

// Export search results
async function exportSearchResults() {
    const params = new URLSearchParams(currentSearchFilters);
    const url = `/api/admin/search/${currentSearchEntity}/export?${params}`;
    
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `${currentSearchEntity}_search_results.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        showToast('Results exported successfully');
    } catch (error) {
        console.error('Export error:', error);
        showToast('Export failed', 'error');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeSearch();
});
