/**
 * Admin Bulk Operations
 * Provides bulk action capabilities for efficient management
 */

let selectedItems = new Set();
let currentEntityType = null;
let bulkActionMode = false;

// Initialize bulk operations
function initializeBulkOperations() {
    setupBulkActionBar();
    setupSelectAllCheckbox();
}

// Setup bulk action bar
function setupBulkActionBar() {
    const bulkBar = document.getElementById('bulkActionBar');
    if (!bulkBar) return;
    
    // Initially hidden
    bulkBar.style.display = 'none';
}

// Setup select all checkbox
function setupSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', (e) => {
            toggleSelectAll(e.target.checked);
        });
    }
}

// Toggle bulk action mode
function toggleBulkMode(entityType) {
    bulkActionMode = !bulkActionMode;
    currentEntityType = entityType;
    selectedItems.clear();
    
    const bulkBar = document.getElementById('bulkActionBar');
    const bulkModeBtn = document.getElementById('bulkModeBtn');
    const checkboxes = document.querySelectorAll('.item-checkbox');
    
    if (bulkActionMode) {
        bulkBar.style.display = 'flex';
        bulkModeBtn.textContent = 'Exit Bulk Mode';
        bulkModeBtn.classList.add('active');
        checkboxes.forEach(cb => cb.style.display = 'inline-block');
    } else {
        bulkBar.style.display = 'none';
        bulkModeBtn.textContent = 'Bulk Actions';
        bulkModeBtn.classList.remove('active');
        checkboxes.forEach(cb => {
            cb.style.display = 'none';
            cb.checked = false;
        });
    }
    
    updateBulkActionBar();
}

// Toggle select all
function toggleSelectAll(checked) {
    const checkboxes = document.querySelectorAll('.item-checkbox:not(#selectAllCheckbox)');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = checked;
        const itemId = parseInt(checkbox.dataset.itemId);
        
        if (checked) {
            selectedItems.add(itemId);
        } else {
            selectedItems.delete(itemId);
        }
    });
    
    updateBulkActionBar();
}

// Toggle individual item selection
function toggleItemSelection(itemId, checked) {
    if (checked) {
        selectedItems.add(itemId);
    } else {
        selectedItems.delete(itemId);
    }
    
    updateBulkActionBar();
    updateSelectAllCheckbox();
}

// Update select all checkbox state
function updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById('selectAllCheckbox');
    const checkboxes = document.querySelectorAll('.item-checkbox:not(#selectAllCheckbox)');
    const checkedCount = Array.from(checkboxes).filter(cb => cb.checked).length;
    
    if (selectAllCheckbox) {
        selectAllCheckbox.checked = checkedCount === checkboxes.length && checkboxes.length > 0;
        selectAllCheckbox.indeterminate = checkedCount > 0 && checkedCount < checkboxes.length;
    }
}

// Update bulk action bar
function updateBulkActionBar() {
    const selectedCount = document.getElementById('selectedCount');
    const bulkActions = document.getElementById('bulkActionsDropdown');
    
    if (selectedCount) {
        selectedCount.textContent = `${selectedItems.size} selected`;
    }
    
    if (bulkActions) {
        bulkActions.disabled = selectedItems.size === 0;
    }
}

// Show bulk action modal
async function showBulkActionModal(action) {
    if (selectedItems.size === 0) {
        showToast('No items selected', 'error');
        return;
    }
    
    // Get summary first
    const summary = await getBulkOperationSummary();
    
    const modal = document.createElement('div');
    modal.className = 'bulk-action-modal';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
    `;
    
    let modalContent = '';
    
    if (action === 'delete') {
        modalContent = `
            <div style="background: white; border-radius: 12px; padding: 24px; width: 500px; max-width: 90%;">
                <h3 style="margin: 0 0 16px 0; color: #ef4444;">
                    <i class="fas fa-exclamation-triangle"></i> Confirm Bulk Delete
                </h3>
                <div class="summary-box" style="background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 0 0 8px 0; font-weight: 600;">You are about to delete:</p>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>${selectedItems.size} ${currentEntityType}</li>
                        ${summary ? Object.entries(summary).map(([key, value]) => 
                            key !== 'total' ? `<li>${key}: ${value}</li>` : ''
                        ).join('') : ''}
                    </ul>
                </div>
                <p style="color: #991b1b; font-weight: 600;">This action cannot be undone!</p>
                <div style="display: flex; gap: 12px; justify-content: flex-end; margin-top: 20px;">
                    <button onclick="this.closest('.bulk-action-modal').remove()" class="btn-secondary">
                        Cancel
                    </button>
                    <button onclick="executeBulkDelete(); this.closest('.bulk-action-modal').remove();" class="btn-danger">
                        <i class="fas fa-trash"></i> Delete ${selectedItems.size} Items
                    </button>
                </div>
            </div>
        `;
    } else if (action === 'update_status') {
        const statuses = getStatusOptions(currentEntityType);
        modalContent = `
            <div style="background: white; border-radius: 12px; padding: 24px; width: 500px; max-width: 90%;">
                <h3 style="margin: 0 0 16px 0;">
                    <i class="fas fa-edit"></i> Bulk Update Status
                </h3>
                <div class="summary-box" style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 0; font-weight: 600;">Updating ${selectedItems.size} ${currentEntityType}</p>
                </div>
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">New Status</label>
                    <select id="bulkStatusSelect" class="form-select" style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;">
                        ${statuses.map(status => `<option value="${status}">${status}</option>`).join('')}
                    </select>
                </div>
                ${currentEntityType === 'applications' ? `
                    <div style="margin-bottom: 16px;">
                        <label style="display: block; margin-bottom: 8px; font-weight: 500;">Note (Optional)</label>
                        <textarea id="bulkStatusNote" rows="3" style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;" placeholder="Add a note about this status change..."></textarea>
                    </div>
                ` : ''}
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button onclick="this.closest('.bulk-action-modal').remove()" class="btn-secondary">
                        Cancel
                    </button>
                    <button onclick="executeBulkStatusUpdate(); this.closest('.bulk-action-modal').remove();" class="btn-primary">
                        <i class="fas fa-check"></i> Update Status
                    </button>
                </div>
            </div>
        `;
    } else if (action === 'update_fields') {
        const fields = getEditableFields(currentEntityType);
        modalContent = `
            <div style="background: white; border-radius: 12px; padding: 24px; width: 500px; max-width: 90%;">
                <h3 style="margin: 0 0 16px 0;">
                    <i class="fas fa-edit"></i> Bulk Update Fields
                </h3>
                <div class="summary-box" style="background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 0; font-weight: 600;">Updating ${selectedItems.size} ${currentEntityType}</p>
                </div>
                <div id="bulkUpdateFields">
                    ${fields.map(field => `
                        <div style="margin-bottom: 16px;">
                            <label style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                                <input type="checkbox" class="field-checkbox" data-field="${field.name}">
                                <span style="font-weight: 500;">${field.label}</span>
                            </label>
                            <${field.type === 'select' ? 'select' : 'input'} 
                                id="field_${field.name}" 
                                ${field.type !== 'select' ? `type="${field.type}"` : ''}
                                class="form-input" 
                                style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;"
                                disabled
                            >
                                ${field.type === 'select' ? field.options.map(opt => `<option value="${opt}">${opt}</option>`).join('') : ''}
                            </${field.type === 'select' ? 'select' : 'input'}>
                        </div>
                    `).join('')}
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button onclick="this.closest('.bulk-action-modal').remove()" class="btn-secondary">
                        Cancel
                    </button>
                    <button onclick="executeBulkFieldUpdate(); this.closest('.bulk-action-modal').remove();" class="btn-primary">
                        <i class="fas fa-check"></i> Update Fields
                    </button>
                </div>
            </div>
        `;
    } else if (action === 'export') {
        modalContent = `
            <div style="background: white; border-radius: 12px; padding: 24px; width: 500px; max-width: 90%;">
                <h3 style="margin: 0 0 16px 0;">
                    <i class="fas fa-download"></i> Export Selected Items
                </h3>
                <div class="summary-box" style="background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
                    <p style="margin: 0; font-weight: 600;">Exporting ${selectedItems.size} ${currentEntityType}</p>
                </div>
                <div style="margin-bottom: 16px;">
                    <label style="display: block; margin-bottom: 8px; font-weight: 500;">Export Format</label>
                    <select id="exportFormat" class="form-select" style="width: 100%; padding: 8px 12px; border: 1px solid #d1d5db; border-radius: 4px;">
                        <option value="csv">CSV (Excel Compatible)</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button onclick="this.closest('.bulk-action-modal').remove()" class="btn-secondary">
                        Cancel
                    </button>
                    <button onclick="executeBulkExport(); this.closest('.bulk-action-modal').remove();" class="btn-primary">
                        <i class="fas fa-download"></i> Export
                    </button>
                </div>
            </div>
        `;
    }
    
    modal.innerHTML = modalContent;
    document.body.appendChild(modal);
    
    // Setup field checkbox listeners
    document.querySelectorAll('.field-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            const fieldName = e.target.dataset.field;
            const input = document.getElementById(`field_${fieldName}`);
            input.disabled = !e.target.checked;
        });
    });
}

// Get status options for entity type
function getStatusOptions(entityType) {
    const options = {
        'users': ['active', 'inactive'],
        'programs': ['draft', 'published', 'closed'],
        'applications': ['submitted', 'under_review', 'shortlisted', 'accepted', 'rejected'],
        'meetings': ['scheduled', 'in_progress', 'completed', 'cancelled'],
        'referrals': ['pending', 'accepted', 'successful', 'rejected'],
        'leads': ['read', 'unread']
    };
    
    return options[entityType] || [];
}

// Get editable fields for entity type
function getEditableFields(entityType) {
    const fields = {
        'users': [
            { name: 'role', label: 'Role', type: 'select', options: ['startup', 'corporate', 'enabler', 'admin'] },
            { name: 'country', label: 'Country', type: 'text' },
            { name: 'company', label: 'Company', type: 'text' }
        ],
        'programs': [
            { name: 'type', label: 'Type', type: 'select', options: ['accelerator', 'grant', 'pilot', 'challenge', 'corporate_vc'] },
            { name: 'status', label: 'Status', type: 'select', options: ['draft', 'published', 'closed'] },
            { name: 'deadline', label: 'Deadline', type: 'datetime-local' }
        ]
    };
    
    return fields[entityType] || [];
}

// Get bulk operation summary
async function getBulkOperationSummary() {
    try {
        const response = await fetch('/api/admin/bulk/summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                entity_type: currentEntityType,
                entity_ids: Array.from(selectedItems)
            })
        });
        
        const result = await response.json();
        return result.success ? result.summary : null;
    } catch (error) {
        console.error('Error getting summary:', error);
        return null;
    }
}

// Execute bulk delete
async function executeBulkDelete() {
    const endpoint = `/api/admin/bulk/${currentEntityType}/delete`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                [`${currentEntityType.slice(0, -1)}_ids`]: Array.from(selectedItems),
                confirm: true
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            selectedItems.clear();
            reloadCurrentSection();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Bulk delete error:', error);
        showToast('Bulk delete failed', 'error');
    }
}

// Execute bulk status update
async function executeBulkStatusUpdate() {
    const status = document.getElementById('bulkStatusSelect')?.value;
    const note = document.getElementById('bulkStatusNote')?.value;
    
    if (!status) {
        showToast('Please select a status', 'error');
        return;
    }
    
    const endpoint = `/api/admin/bulk/${currentEntityType}/update-status`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                [`${currentEntityType.slice(0, -1)}_ids`]: Array.from(selectedItems),
                status: status,
                note: note
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            selectedItems.clear();
            reloadCurrentSection();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Bulk status update error:', error);
        showToast('Bulk status update failed', 'error');
    }
}

// Execute bulk field update
async function executeBulkFieldUpdate() {
    const updates = {};
    
    document.querySelectorAll('.field-checkbox:checked').forEach(checkbox => {
        const fieldName = checkbox.dataset.field;
        const input = document.getElementById(`field_${fieldName}`);
        if (input && !input.disabled) {
            updates[fieldName] = input.value;
        }
    });
    
    if (Object.keys(updates).length === 0) {
        showToast('No fields selected for update', 'error');
        return;
    }
    
    const endpoint = `/api/admin/bulk/${currentEntityType}/update`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                [`${currentEntityType.slice(0, -1)}_ids`]: Array.from(selectedItems),
                updates: updates
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast(result.message, 'success');
            selectedItems.clear();
            reloadCurrentSection();
        } else {
            showToast(result.error, 'error');
        }
    } catch (error) {
        console.error('Bulk field update error:', error);
        showToast('Bulk field update failed', 'error');
    }
}

// Execute bulk export
async function executeBulkExport() {
    const format = document.getElementById('exportFormat')?.value || 'csv';
    const endpoint = `/api/admin/bulk/${currentEntityType}/export`;
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                [`${currentEntityType.slice(0, -1)}_ids`]: Array.from(selectedItems),
                format: format
            })
        });
        
        if (format === 'csv') {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentEntityType}_export.csv`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            const result = await response.json();
            const blob = new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentEntityType}_export.json`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        }
        
        showToast('Export completed successfully', 'success');
    } catch (error) {
        console.error('Bulk export error:', error);
        showToast('Bulk export failed', 'error');
    }
}

// Reload current section
function reloadCurrentSection() {
    // Trigger reload based on current section
    if (currentEntityType === 'users') {
        renderFilteredUsers();
    } else if (currentEntityType === 'programs') {
        loadPrograms();
    } else if (currentEntityType === 'applications') {
        loadApplications();
    } else if (currentEntityType === 'meetings') {
        loadMeetings();
    } else if (currentEntityType === 'leads') {
        loadLeads();
    } else if (currentEntityType === 'referrals') {
        loadReferrals();
    }
    
    toggleBulkMode(currentEntityType);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeBulkOperations();
});
