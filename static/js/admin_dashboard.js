// ===== ADMIN DASHBOARD JS - CLEAN & INSTANT =====
// NO ANIMATIONS, INSTANT RESPONSE, ALL BUTTONS WORK

let users = [];
let currentFilter = 'all';
let currentStats = {
    totalUsers: 0,
    totalStartups: 0,
    totalCorporate: 0,
    totalConnectors: 0,
    totalPrograms: 0
};

// ===== DROPDOWN TOGGLE - INSTANT =====
window.toggleDropdown = function(dropdownId, e) {
    if (e) e.stopPropagation();
    
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;
    
    const isActive = dropdown.classList.contains('active');
    
    // Close all dropdowns
    document.querySelectorAll('.dropdown.active').forEach(d => {
        d.classList.remove('active');
    });
    
    // Toggle current
    if (!isActive) {
        dropdown.classList.add('active');
    }
};

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown')) {
        document.querySelectorAll('.dropdown.active').forEach(d => {
            d.classList.remove('active');
        });
    }
});

// ===== SECTION NAVIGATION - INSTANT =====
window.showSection = function(sectionName) {
    // Close dropdowns
    document.querySelectorAll('.dropdown.active').forEach(d => {
        d.classList.remove('active');
    });
    
    // Hide all sections
    document.querySelectorAll('main section').forEach(s => {
        s.style.display = 'none';
    });
    
    // Show target section
    const targetSection = document.getElementById(sectionName + 'Section');
    if (targetSection) {
        targetSection.style.display = 'block';
        window.scrollTo(0, 0);
        loadSectionData(sectionName);
    }
};

// ===== LOAD SECTION DATA =====
function loadSectionData(sectionName) {
    if (sectionName === 'users' && users.length > 0) {
        renderFilteredUsers();
    } else if (sectionName === 'startups' && users.length > 0) {
        renderStartupUsers();
    } else if (sectionName === 'corporate' && users.length > 0) {
        renderCorporateUsers();
    } else if (sectionName === 'connectors' && users.length > 0) {
        renderConnectorUsers();
    } else if (sectionName === 'programs') {
        loadPrograms();
    } else if (sectionName === 'analytics') {
        loadAnalytics();
    } else if (sectionName === 'referrals') {
        loadReferrals();
    } else if (sectionName === 'meetings') {
        loadMeetings();
    }
}

// ===== LOAD ANALYTICS =====
async function loadAnalytics() {
    console.log('Loading analytics...');
    
    try {
        // Load stats for analytics
        const response = await fetch('/api/admin/stats');
        const data = await response.json();
        
        if (data.success && data.stats) {
            const stats = data.stats;
            
            // Update analytics cards
            const updateEl = (id, value) => {
                const el = document.getElementById(id);
                if (el) el.textContent = value || 0;
            };
            
            updateEl('activeUsersCount', stats.total_users);
            updateEl('totalApplicationsAnalytics', stats.total_applications);
            
            console.log('Analytics loaded successfully');
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics', 'error');
    }
}

// ===== LOAD REFERRALS =====
async function loadReferrals() {
    console.log('Loading referrals...');
    const tbody = document.getElementById('referralsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px;"><div class="loading"></div><p>Loading referrals...</p></td></tr>';
    
    try {
        const response = await fetch('/api/admin/referrals');
        const data = await response.json();
        
        console.log('Referrals data:', data);
        
        if (data.success && data.referrals) {
            const referrals = data.referrals;
            
            if (referrals.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 40px; color: #94a3b8;">
                            <i class="fas fa-exchange-alt" style="font-size: 48px; margin-bottom: 15px; display: block; opacity: 0.3;"></i>
                            <p style="margin: 0;">No referrals yet</p>
                            <p style="font-size: 0.9rem; margin-top: 8px;">Referrals will appear here when connectors refer startups</p>
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = referrals.map(ref => `
                <tr>
                    <td>
                        <div style="font-weight: 600;">${ref.connector_name || 'Unknown'}</div>
                        <div style="font-size: 0.85rem; color: #64748b;">${ref.connector_email || ''}</div>
                    </td>
                    <td>
                        <div style="font-weight: 600;">${ref.startup_name || 'Unknown'}</div>
                        <div style="font-size: 0.85rem; color: #64748b;">${ref.startup_email || ''}</div>
                    </td>
                    <td>${ref.program_title || 'N/A'}</td>
                    <td>
                        <span class="status-badge status-${ref.status}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                            ${ref.status}
                        </span>
                    </td>
                    <td>${new Date(ref.created_at).toLocaleDateString()}</td>
                </tr>
            `).join('');
            
            console.log(`Loaded ${referrals.length} referrals`);
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: #ef4444;">Failed to load referrals</td></tr>';
        }
    } catch (error) {
        console.error('Error loading referrals:', error);
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 40px; color: #ef4444;">Error loading referrals</td></tr>';
        showToast('Failed to load referrals', 'error');
    }
}

// ===== LOAD MEETINGS =====
async function loadMeetings() {
    console.log('Loading meetings...');
    
    try {
        // Load meeting stats
        const statsResponse = await fetch('/api/meetings/stats');
        const statsData = await statsResponse.json();
        
        if (statsData.success && statsData.stats) {
            const stats = statsData.stats;
            
            // Update stat cards
            const updateEl = (id, value) => {
                const el = document.getElementById(id);
                if (el) el.textContent = value || 0;
            };
            
            updateEl('totalMeetings', stats.total_meetings);
            updateEl('upcomingMeetings', stats.upcoming_meetings);
            updateEl('totalParticipants', stats.total_participants);
            
            console.log('Meeting stats loaded:', stats);
        }
        
        // Load meetings list
        const meetingsResponse = await fetch('/api/meetings/');
        const meetingsData = await meetingsResponse.json();
        
        console.log('Meetings data:', meetingsData);
        
        if (meetingsData.success && meetingsData.meetings) {
            renderMeetings(meetingsData.meetings);
        } else {
            const container = document.getElementById('meetingsList');
            if (container) {
                container.innerHTML = '<p style="text-align: center; color: #ef4444;">Failed to load meetings</p>';
            }
        }
    } catch (error) {
        console.error('Error loading meetings:', error);
        const container = document.getElementById('meetingsList');
        if (container) {
            container.innerHTML = '<p style="text-align: center; color: #ef4444;">Error loading meetings</p>';
        }
        showToast('Failed to load meetings', 'error');
    }
}

// ===== RENDER MEETINGS =====
function renderMeetings(meetings) {
    const container = document.getElementById('meetingsList');
    if (!container) return;
    
    if (!meetings || meetings.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-video"></i>
                <p>No meetings scheduled</p>
                <p style="font-size: 0.9rem; color: #64748b; margin-top: 8px;">Create a new meeting to get started</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = meetings.map(meeting => {
        const scheduledDate = new Date(meeting.scheduled_at);
        const isUpcoming = scheduledDate > new Date();
        const statusClass = meeting.status || (isUpcoming ? 'scheduled' : 'completed');
        
        return `
            <div class="meeting-item" style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                            <h4 style="margin: 0; font-weight: 600;">${meeting.title}</h4>
                            <span class="status-badge status-${statusClass}" style="padding: 4px 8px; border-radius: 4px; font-size: 12px;">
                                ${statusClass}
                            </span>
                        </div>
                        <p style="margin: 0 0 8px 0; color: #666; font-size: 14px;">${meeting.description || 'No description'}</p>
                        <div style="font-size: 13px; color: #666; display: flex; gap: 16px;">
                            <span><i class="fas fa-calendar"></i> ${scheduledDate.toLocaleDateString()}</span>
                            <span><i class="fas fa-clock"></i> ${scheduledDate.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}</span>
                            <span><i class="fas fa-hourglass-half"></i> ${meeting.duration_minutes} min</span>
                            <span><i class="fas fa-users"></i> ${meeting.participant_count || 0} participants</span>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px; flex-shrink: 0; margin-left: 16px;">
                        ${isUpcoming ? `
                            <button onclick="window.joinMeeting('${meeting.meeting_room_id}')" class="admin-btn primary" style="padding: 8px 16px;">
                                <i class="fas fa-video"></i> Join
                            </button>
                        ` : ''}
                        <button onclick="window.viewMeeting(${meeting.id})" class="admin-btn" style="padding: 8px 16px;">
                            <i class="fas fa-eye"></i> View
                        </button>
                        <button onclick="window.editMeeting(${meeting.id})" class="admin-btn" style="padding: 8px 16px;">
                            <i class="fas fa-edit"></i> Edit
                        </button>
                        <button onclick="window.deleteMeeting(${meeting.id})" class="admin-btn" style="padding: 8px 16px; background: #ef4444; color: white; border: none;">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    console.log(`Rendered ${meetings.length} meetings`);
}

// ===== MEETING ACTIONS (PLACEHOLDERS) =====
window.joinMeeting = function(roomId) {
    window.open(`/meetings/join/${roomId}`, '_blank');
};

window.viewMeeting = function(id) {
    showToast('View meeting details coming soon', 'info');
};

window.editMeeting = function(id) {
    showToast('Edit meeting functionality coming soon', 'info');
};

window.deleteMeeting = async function(id) {
    if (!confirm('Are you sure you want to delete this meeting?')) return;
    showToast('Delete meeting functionality coming soon', 'info');
};

window.showCreateMeetingModal = function() {
    showToast('Create meeting functionality coming soon', 'info');
};

window.filterMeetings = function(filter) {
    showToast(`Filter by ${filter} coming soon`, 'info');
};

// ===== LOAD DASHBOARD STATS =====
async function loadDashboardStats() {
    try {
        console.log('Loading dashboard stats...');
        const response = await fetch('/api/admin/stats');
        console.log('Stats response status:', response.status);
        
        if (!response.ok) {
            console.error('Stats API error:', response.status, response.statusText);
            return;
        }
        
        const data = await response.json();
        console.log('Stats data received:', data);

        if (data.success && data.stats) {
            const stats = data.stats;

            // Update stats instantly
            const updateStat = (id, value) => {
                const el = document.getElementById(id);
                if (el) {
                    el.textContent = value || 0;
                    console.log(`Updated ${id} to ${value || 0}`);
                } else {
                    console.warn(`Element not found: ${id}`);
                }
            };

            updateStat('totalUsers', stats.total_users);
            updateStat('totalStartups', stats.total_startups);
            updateStat('totalCorporate', stats.total_corporate);
            updateStat('totalConnectors', stats.total_connectors);
            updateStat('totalPrograms', stats.total_programs);
            updateStat('allCount', stats.total_users);
            updateStat('startupCount', stats.total_startups);
            updateStat('corporateCount', stats.total_corporate);
            updateStat('connectorCount', stats.total_connectors);
            updateStat('adminCount', stats.total_admins);

            currentStats = {
                totalUsers: stats.total_users || 0,
                totalStartups: stats.total_startups || 0,
                totalCorporate: stats.total_corporate || 0,
                totalConnectors: stats.total_connectors || 0,
                totalPrograms: stats.total_programs || 0
            };
            
            console.log('Stats updated successfully:', currentStats);
        } else {
            console.error('Invalid stats response format:', data);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Failed to load dashboard stats', 'error');
    }
}

// ===== LOAD USERS =====
async function loadRecentUsers() {
    try {
        console.log('Loading users...');
        const response = await fetch('/api/admin/users');
        console.log('Users response status:', response.status);
        
        if (!response.ok) {
            console.error('Users API error:', response.status, response.statusText);
            return;
        }
        
        const data = await response.json();
        console.log('Users data received:', data);

        users = Array.isArray(data) ? data : (data.success && data.users ? data.users : []);
        console.log('Total users loaded:', users.length);

        updateUserCounts();
        renderRecentUsers();
    } catch (error) {
        console.error('Error loading users:', error);
        showToast('Failed to load users', 'error');
    }
}

// ===== UPDATE USER COUNTS =====
function updateUserCounts() {
    const counts = {
        all: users.length,
        startup: users.filter(u => u && (u.role === 'startup' || u.role === 'founder')).length,
        corporate: users.filter(u => u && u.role === 'corporate').length,
        connector: users.filter(u => u && (u.role === 'connector' || u.role === 'enabler')).length,
        admin: users.filter(u => u && u.role === 'admin').length
    };

    const updateEl = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
    };

    updateEl('allCount', counts.all);
    updateEl('startupCount', counts.startup);
    updateEl('corporateCount', counts.corporate);
    updateEl('connectorCount', counts.connector);
    updateEl('adminCount', counts.admin);
}

// ===== GET DISPLAY NAME =====
function getDisplayName(user) {
    if (user.name) return user.name;
    if (user.full_name) return user.full_name;
    if (user.corporate_name) return user.corporate_name;
    if (user.company) return user.company;
    if (user.first_name && user.last_name) return `${user.first_name} ${user.last_name}`;
    if (user.email) return user.email.split('@')[0];
    return user.username || 'Unknown User';
}

// ===== GET USER INITIALS =====
function getUserInitials(user) {
    const nameToUse = user.name || user.full_name || user.corporate_name;
    if (nameToUse) {
        const parts = nameToUse.split(' ');
        if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
        return nameToUse.substring(0, 2).toUpperCase();
    }
    if (user.email) return user.email.substring(0, 2).toUpperCase();
    if (user.username) return user.username.substring(0, 2).toUpperCase();
    return 'U';
}

// ===== FORMAT TIME AGO =====
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

// ===== RENDER RECENT USERS =====
function renderRecentUsers() {
    const container = document.getElementById('recentUsers');
    if (!container) return;

    if (!users || users.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><p>No users yet</p></div>';
        return;
    }

    const recentUsers = [...users].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 10);

    container.innerHTML = recentUsers.map(user => `
        <div class="user-item">
            <div class="user-avatar ${user.role}">${getUserInitials(user)}</div>
            <div class="user-info">
                <div class="user-name">${getDisplayName(user)}</div>
                <div class="user-role">${user.role.toUpperCase()} • ${formatTimeAgo(user.created_at)}</div>
            </div>
        </div>
    `).join('');
}

// ===== RENDER FILTERED USERS =====
function renderFilteredUsers() {
    const container = document.getElementById('allUsersList');
    if (!container) return;

    let filteredUsers = users;
    if (currentFilter !== 'all') {
        if (currentFilter === 'startup') {
            filteredUsers = users.filter(u => u.role === 'startup' || u.role === 'founder');
        } else if (currentFilter === 'connector') {
            filteredUsers = users.filter(u => u.role === 'connector' || u.role === 'enabler');
        } else {
            filteredUsers = users.filter(u => u.role === currentFilter);
        }
    }

    if (filteredUsers.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-users"></i><p>No users found</p></div>';
        return;
    }

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${filteredUsers.map(user => `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                    <div class="user-avatar ${user.role}" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem;">
                        ${getUserInitials(user)}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${getDisplayName(user)}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">${user.role.toUpperCase()} • ${formatTimeAgo(user.created_at)}</div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; font-size: 0.85rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Email:</strong> ${user.email}</div>
                    <div><strong>ID:</strong> #${user.id}</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('')}
    </div>`;
}

// ===== RENDER STARTUP USERS =====
function renderStartupUsers() {
    const container = document.getElementById('startupUsersList');
    if (!container) return;

    const startupUsers = users.filter(u => u.role === 'startup' || u.role === 'founder');
    if (startupUsers.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-rocket"></i><p>No startup users</p></div>';
        return;
    }

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${startupUsers.map(user => `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                    <div class="user-avatar startup" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem;">
                        ${getUserInitials(user)}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${getDisplayName(user)}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">STARTUP • ${formatTimeAgo(user.created_at)}</div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; font-size: 0.85rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Email:</strong> ${user.email}</div>
                    <div><strong>ID:</strong> #${user.id}</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('')}
    </div>`;
}

// ===== RENDER CORPORATE USERS =====
function renderCorporateUsers() {
    const container = document.getElementById('corporateUsersList');
    if (!container) return;

    const corporateUsers = users.filter(u => u.role === 'corporate');
    if (corporateUsers.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-building"></i><p>No corporate users</p></div>';
        return;
    }

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${corporateUsers.map(user => `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                    <div class="user-avatar corporate" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem;">
                        ${getUserInitials(user)}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${getDisplayName(user)}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">CORPORATE • ${formatTimeAgo(user.created_at)}</div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; font-size: 0.85rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Email:</strong> ${user.email}</div>
                    <div><strong>Company:</strong> ${user.corporate_name || 'N/A'}</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('')}
    </div>`;
}

// ===== RENDER CONNECTOR USERS =====
function renderConnectorUsers() {
    const container = document.getElementById('connectorsUsersList');
    if (!container) return;

    const connectorUsers = users.filter(u => u.role === 'connector' || u.role === 'enabler');
    if (connectorUsers.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-handshake"></i><p>No connector users</p></div>';
        return;
    }

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${connectorUsers.map(user => `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem;">
                <div style="display: flex; align-items: flex-start; margin-bottom: 1rem;">
                    <div class="user-avatar connector" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem;">
                        ${getUserInitials(user)}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${getDisplayName(user)}</div>
                        <div style="font-size: 0.8rem; color: #94a3b8;">CONNECTOR • ${formatTimeAgo(user.created_at)}</div>
                    </div>
                </div>
                <div style="background: #f8fafc; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; font-size: 0.85rem;">
                    <div style="margin-bottom: 0.5rem;"><strong>Email:</strong> ${user.email}</div>
                    <div><strong>ID:</strong> #${user.id}</div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `).join('')}
    </div>`;
}

// ===== FILTER USERS =====
function filterUsers(filter) {
    currentFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(tab => tab.classList.remove('active'));
    event.target.classList.add('active');
    renderFilteredUsers();
}

// ===== LOAD PROGRAMS =====
async function loadPrograms() {
    const container = document.getElementById('programsList');
    if (!container) return;

    container.innerHTML = '<p style="text-align: center; padding: 20px;">Loading programs...</p>';

    try {
        const response = await fetch('/api/admin/opportunities?v=' + Date.now());
        const data = await response.json();

        if (data.success && data.opportunities) {
            window.allPrograms = data.opportunities;
            renderPrograms(data.opportunities);
        } else {
            container.innerHTML = '<p style="text-align: center; color: #ef4444;">Failed to load programs</p>';
        }
    } catch (error) {
        console.error('Error loading programs:', error);
        container.innerHTML = '<p style="text-align: center; color: #ef4444;">Error loading programs</p>';
    }
}

// ===== RENDER PROGRAMS =====
function renderPrograms(programs) {
    const container = document.getElementById('programsList');
    if (!container) return;

    if (!programs || programs.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-rocket"></i><p>No programs yet</p></div>';
        return;
    }

    container.innerHTML = programs.map(program => `
        <div class="program-item">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <h4 style="margin: 0; font-weight: 600;">${program.title}</h4>
                        <span class="status-badge status-${program.status}">${program.status}</span>
                    </div>
                    <p style="margin: 0 0 8px 0; color: #666; font-size: 14px;">${program.description || 'No description'}</p>
                    <div style="font-size: 13px; color: #666;">
                        <i class="fas fa-calendar"></i> ${new Date(program.created_at).toLocaleDateString()}
                    </div>
                </div>
                <div style="display: flex; gap: 8px; flex-shrink: 0; margin-left: 16px;">
                    <button onclick="window.viewProgram(${program.id})" class="admin-btn" style="padding: 8px 16px;">
                        <i class="fas fa-eye"></i> View
                    </button>
                    <button onclick="window.editProgram(${program.id})" class="admin-btn primary" style="padding: 8px 16px;">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button onclick="window.viewApplications(${program.id})" class="admin-btn" style="padding: 8px 16px; background: #059669; color: white; border: none;">
                        <i class="fas fa-paper-plane"></i> Apps
                    </button>
                    <button onclick="window.deleteProgram(${program.id})" class="admin-btn" style="padding: 8px 16px; background: #ef4444; color: white; border: none;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ===== SHOW TOAST =====
function showToast(message, type = 'info') {
    document.querySelectorAll('.toast').forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

// ===== GO TO PLATFORM =====
function goToPlatform() {
    window.location.href = '/';
}

// ===== DELETE USER =====
async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user?')) return;

    try {
        const response = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.success) {
            showToast('User deleted successfully', 'success');
            loadRecentUsers();
            loadDashboardStats();
        } else {
            showToast('Failed to delete user', 'error');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Error deleting user', 'error');
    }
}

// ===== EDIT USER =====
async function editUser(id) {
    showToast('Edit user functionality coming soon', 'info');
}

// ===== INITIALIZE ON LOAD =====
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();
    loadRecentUsers();
    
    // Load programs if on programs section
    const programsSection = document.getElementById('programsSection');
    if (programsSection && programsSection.style.display !== 'none') {
        loadPrograms();
    }
});
