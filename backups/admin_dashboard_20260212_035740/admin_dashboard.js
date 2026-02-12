let users = [];
let currentFilter = 'all';
let currentStats = {
    totalUsers: 0,
    totalStartups: 0,
    totalCorporate: 0,
    totalConnectors: 0,
    totalPrograms: 0,
    totalAdmins: 0
};

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/admin/stats');
        if (!response.ok) throw new Error('Network response was not ok');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;

            // Update Overview Cards
            if (document.getElementById('totalUsers')) animateStatChange('totalUsers', currentStats.totalUsers, stats.total_users || 0);
            if (document.getElementById('totalStartups')) animateStatChange('totalStartups', currentStats.totalStartups, stats.total_startups || 0);
            if (document.getElementById('totalCorporate')) animateStatChange('totalCorporate', currentStats.totalCorporate, stats.total_corporate || 0);
            if (document.getElementById('totalConnectors')) animateStatChange('totalConnectors', currentStats.totalConnectors, stats.total_connectors || 0);
            if (document.getElementById('totalPrograms')) animateStatChange('totalPrograms', currentStats.totalPrograms, stats.total_programs || 0);

            // SYNC TABS (Below) - Ensuring match
            const updateEl = (id, val) => {
                const el = document.getElementById(id);
                if (el) el.textContent = val;
            };
            updateEl('allCount', stats.total_users || 0);
            updateEl('startupCount', stats.total_startups || 0);
            updateEl('corporateCount', stats.total_corporate || 0);
            updateEl('connectorCount', stats.total_connectors || 0);
            updateEl('adminCount', stats.total_admins || 0);

            currentStats = {
                totalUsers: stats.total_users || 0,
                totalStartups: stats.total_startups || 0,
                totalCorporate: stats.total_corporate || 0,
                totalConnectors: stats.total_connectors || 0,
                totalPrograms: stats.total_programs || 0,
                totalAdmins: stats.total_admins || 0
            };
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function loadRecentUsers() {
    const containers = ['recentUsers', 'allUsersList', 'startupUsersList', 'corporateUsersList', 'connectorsUsersList'];
    try {
        const response = await fetch('/api/admin/users');
        if (!response.ok) throw new Error('User fetch failed');
        const data = await response.json();

        if (Array.isArray(data)) {
            users = data;
        } else if (data.success && data.users) {
            users = data.users;
        } else {
            users = [];
        }

        updateUserCounts();
        renderRecentUsers();

        const sections = ['users', 'startups', 'corporate', 'connectors'];
        sections.forEach(s => {
            const el = document.getElementById(s + 'Section');
            if (el && el.style.display !== 'none') {
                if (s === 'users') renderFilteredUsers();
                if (s === 'startups') renderStartupUsers();
                if (s === 'corporate') renderCorporateUsers();
                if (s === 'connectors') renderConnectorUsers();
            }
        });
    } catch (error) {
        console.error('Error loading users:', error);
        containers.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = '<p style="text-align:center; color:#ef4444; padding:20px;">Failed to load users. Please refresh.</p>';
        });
    }
}

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

function getDisplayName(user) {
    if (user.name) return user.name;
    if (user.full_name) return user.full_name;
    if (user.corporate_name) return user.corporate_name;
    if (user.company) return user.company;

    if (user.first_name && user.last_name) {
        return `${user.first_name} ${user.last_name}`;
    }

    if (user.username && user.username.includes('_')) {
        const parts = user.username.split('_');
        return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
    }

    if (user.email) {
        const emailName = user.email.split('@')[0];
        if (emailName.includes('.')) {
            const parts = emailName.split('.');
            return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
        }
        return emailName.charAt(0).toUpperCase() + emailName.slice(1);
    }

    return user.username ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : 'Unknown User';
}

function getUserInitials(user) {
    // Priority 1: Use full name or name
    const nameToUse = user.name || user.full_name || user.corporate_name;
    if (nameToUse) {
        const parts = nameToUse.split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return nameToUse.substring(0, 2).toUpperCase();
    }

    // Priority 2: Use email
    if (user.email) {
        const parts = user.email.split('@')[0].split('.');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return user.email.substring(0, 2).toUpperCase();
    }

    // Priority 3: Use username
    if (user.username) {
        if (user.username.includes('_')) {
            const parts = user.username.split('_');
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return user.username.substring(0, 2).toUpperCase();
    }

    // Final Fallback: Icon instead of '??'
    return '<i class="fas fa-user" style="font-size: 0.8em;"></i>';
}

function renderRecentUsers() {
    const container = document.getElementById('recentUsers');

    if (!users || users.length === 0) {
        container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-users"></i>
                        <p>No users registered yet</p>
                    </div>
                `;
        return;
    }

    const recentUsers = [...users]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 10);

    container.innerHTML = recentUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
                    <div class="user-item">
                        <div class="user-avatar ${user.role}">
                            ${initials}
                        </div>
                        <div class="user-info">
                            <div class="user-name">${displayName}</div>
                            <div class="user-role">${user.role.toUpperCase()} • ${timeAgo}</div>
                        </div>
                        <div class="user-status status-offline">
                            <span class="status-dot"></span>
                            Offline
                        </div>
                    </div>
                `;
    }).join('');
}

function renderFilteredUsers() {
    const container = document.getElementById('allUsersList');

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
        container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-users"></i>
                        <p>No ${currentFilter === 'all' ? '' : currentFilter} users found</p>
                    </div>
                `;
        return;
    }

    const sortedUsers = [...filteredUsers].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        // Determine Theme Colors based on Role
        let headerGradient = 'linear-gradient(90deg, #64748b, #94a3b8)'; // Default Gray
        let badgeBg = '#f1f5f9';
        let badgeColor = '#475569';
        let badgeBorder = '#e2e8f0';

        if (user.role === 'startup' || user.role === 'founder') {
            headerGradient = 'linear-gradient(90deg, #fcb82e, #f59e0b)';
            badgeBg = '#fff7ed';
            badgeColor = '#c2410c';
            badgeBorder = '#ffedd5';
        } else if (user.role === 'connector' || user.role === 'enabler') {
            headerGradient = 'linear-gradient(90deg, #2563eb, #3b82f6)';
            badgeBg = '#eff6ff';
            badgeColor = '#1e40af';
            badgeBorder = '#dbeafe';
        } else if (user.role === 'corporate') {
            headerGradient = 'linear-gradient(90deg, #0f172a, #334155)';
            badgeBg = '#f8fafc';
            badgeColor = '#0f172a';
            badgeBorder = '#e2e8f0';
        } else if (user.role === 'admin') {
            headerGradient = 'linear-gradient(90deg, #7e22ce, #a855f7)';
            badgeBg = '#faf5ff';
            badgeColor = '#6b21a8';
            badgeBorder = '#f3e8ff';
        }

        return `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: ${headerGradient};"></div>
                
                <div style="display: flex; align-items: flex-start; margin-bottom: 1.25rem;">
                    <div class="user-avatar ${user.role}" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        ${initials}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${displayName}</div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: ${badgeBg}; color: ${badgeColor}; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; border: 1px solid ${badgeBorder}; text-transform: uppercase;">${user.role}</span>
                            <span style="font-size: 0.8rem; color: #94a3b8;">• Joined ${timeAgo}</span>
                        </div>
                    </div>
                </div>

                <div class="user-details-grid" style="background: #f8fafc; padding: 1rem; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; font-size: 0.85rem;">
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Email</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.email}</div>
                    </div>
                    
                    ${user.corporate_name ? `
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Company</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.corporate_name}</div>
                    </div>` : ''}

                    ${user.country ? `
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Country</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.country}</div>
                    </div>` : ''}

                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">User ID</div>
                        <div style="color: #334155; font-weight: 600;">#${user.id}</div>
                    </div>
                </div>

                <div class="user-actions" style="display: flex; gap: 10px; border-top: 1px solid #f1f5f9; padding-top: 1.25rem;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600; color: #475569; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('')}
    </div>`;
}

function renderStartupUsers() {
    const container = document.getElementById('startupUsersList');
    const startupUsers = users.filter(u => u.role === 'startup');

    if (startupUsers.length === 0) {
        container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-rocket"></i>
                        <p>No startup users registered yet</p>
                    </div>
                `;
        return;
    }

    const sortedUsers = [...startupUsers].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: linear-gradient(90deg, #fcb82e, #f59e0b);"></div>
                
                <div style="display: flex; align-items: flex-start; margin-bottom: 1.25rem;">
                    <div class="user-avatar startup" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        ${initials}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${displayName}</div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: #fff7ed; color: #c2410c; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; border: 1px solid #ffedd5;">STARTUP</span>
                            <span style="font-size: 0.8rem; color: #94a3b8;">• Joined ${timeAgo}</span>
                        </div>
                    </div>
                </div>

                <div class="user-details-grid" style="background: #f8fafc; padding: 1rem; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; font-size: 0.85rem;">
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Email</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.email}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">User ID</div>
                        <div style="color: #334155; font-weight: 600;">#${user.id}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Username</div>
                        <div style="color: #334155; font-weight: 600;">${user.username || 'N/A'}</div>
                    </div>
                    <div>
                         <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Registered</div>
                        <div style="color: #334155; font-weight: 600;">${new Date(user.created_at).toLocaleDateString()}</div>
                    </div>
                </div>

                <div class="user-actions" style="display: flex; gap: 10px; border-top: 1px solid #f1f5f9; padding-top: 1.25rem;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600; color: #475569; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('')}
    </div>`;
}

function renderCorporateUsers() {
    const container = document.getElementById('corporateUsersList');
    const corporateUsers = users.filter(u => u.role === 'corporate');

    if (corporateUsers.length === 0) {
        container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-building"></i>
                        <p>No corporate users registered yet</p>
                    </div>
                `;
        return;
    }

    const sortedUsers = [...corporateUsers].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: linear-gradient(90deg, #0f172a, #334155);"></div>
                
                <div style="display: flex; align-items: flex-start; margin-bottom: 1.25rem;">
                    <div class="user-avatar corporate" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05); background: #f1f5f9; color: #0f172a; border: 1px solid #e2e8f0;">
                        ${initials}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${displayName}</div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: #f1f5f9; color: #334155; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; border: 1px solid #e2e8f0;">CORPORATE</span>
                            <span style="font-size: 0.8rem; color: #94a3b8;">• Joined ${timeAgo}</span>
                        </div>
                    </div>
                </div>

                <div class="user-details-grid" style="background: #f8fafc; padding: 1rem; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; font-size: 0.85rem;">
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Company</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.corporate_name || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Contact</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.full_name || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Email</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.email}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Phone</div>
                        <div style="color: #334155; font-weight: 600;">${user.phone_number || 'N/A'}</div>
                    </div>
                </div>

                <div class="user-actions" style="display: flex; gap: 10px; border-top: 1px solid #f1f5f9; padding-top: 1.25rem;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600; color: #475569; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('')}
    </div>`;
}

function renderConnectorUsers() {
    const container = document.getElementById('connectorsUsersList');
    const connectorUsers = users.filter(u => u.role === 'connector' || u.role === 'enabler');

    if (connectorUsers.length === 0) {
        container.innerHTML = `
                    <div class="empty-state">
                        <i class="fas fa-handshake"></i>
                        <p>No connector users registered yet</p>
                    </div>
                `;
        return;
    }

    const sortedUsers = [...connectorUsers].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    container.innerHTML = `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 1.5rem;">
        ${sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
            <div class="user-card" style="background: white; border: 1px solid #e2e8f0; border-radius: 16px; padding: 1.5rem; transition: transform 0.2s, box-shadow 0.2s; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 6px; background: linear-gradient(90deg, #2563eb, #3b82f6);"></div>
                
                <div style="display: flex; align-items: flex-start; margin-bottom: 1.25rem;">
                    <div class="user-avatar connector" style="width: 56px; height: 56px; font-size: 1.25rem; margin-right: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05); background: #eff6ff; color: #1d4ed8; border: 1px solid #dbeafe;">
                        ${initials}
                    </div>
                    <div>
                        <div class="user-name" style="font-size: 1.1rem; margin-bottom: 0.25rem;">${displayName}</div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="background: #eff6ff; color: #1e40af; padding: 2px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 700; border: 1px solid #dbeafe;">CONNECTOR</span>
                            <span style="font-size: 0.8rem; color: #94a3b8;">• Joined ${timeAgo}</span>
                        </div>
                    </div>
                </div>

                <div class="user-details-grid" style="background: #f8fafc; padding: 1rem; border-radius: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; font-size: 0.85rem;">
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Email</div>
                        <div style="color: #334155; font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${user.email}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Country</div>
                        <div style="color: #334155; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${user.country || 'N/A'}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">User ID</div>
                        <div style="color: #334155; font-weight: 600;">#${user.id}</div>
                    </div>
                    <div>
                        <div style="color: #64748b; font-weight: 500; margin-bottom: 2px;">Registered</div>
                        <div style="color: #334155; font-weight: 600;">${new Date(user.created_at).toLocaleDateString()}</div>
                    </div>
                </div>

                <div class="user-actions" style="display: flex; gap: 10px; border-top: 1px solid #f1f5f9; padding-top: 1.25rem;">
                    <button onclick="editUser(${user.id})" style="flex: 1; padding: 8px; background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; cursor: pointer; font-weight: 600; color: #475569; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-pen"></i> Edit
                    </button>
                    <button onclick="deleteUser(${user.id})" style="flex: 1; padding: 8px; background: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; cursor: pointer; font-weight: 600; color: #e11d48; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s;">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('')}
    </div>`;
}

function filterUsers(filter) {
    currentFilter = filter;

    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    renderFilteredUsers();
}

function animateStatChange(elementId, fromValue, toValue) {
    const element = document.getElementById(elementId);
    const duration = 1000;
    const start = Date.now();

    function update() {
        const elapsed = Date.now() - start;
        const progress = Math.min(elapsed / duration, 1);

        const currentValue = Math.round(fromValue + (toValue - fromValue) * progress);
        element.textContent = currentValue;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    update();
}

function showSection(sectionName) {
    document.querySelectorAll('.admin-nav-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');

    document.querySelectorAll('main section').forEach(section => {
        section.style.display = 'none';
    });

    const sectionId = sectionName + 'Section';
    const section = document.getElementById(sectionId);
    if (section) {
        section.style.display = 'block';

        if (sectionName === 'users') {
            renderFilteredUsers();
        } else if (sectionName === 'startups') {
            renderStartupUsers();
        } else if (sectionName === 'corporate') {
            renderCorporateUsers();
        } else if (sectionName === 'connectors') {
            renderConnectorUsers();
        } else if (sectionName === 'programs') {
            loadPrograms();
        }
    }
}

async function loadPrograms() {
    const container = document.getElementById('programsList');
    container.innerHTML = '<div class="loading" style="margin: 20px auto;"></div><p style="text-align: center;">Loading programs...</p>';

    try {
        const response = await fetch('/api/admin/opportunities');
        const data = await response.json();

        if (data.success && data.opportunities) {
            renderPrograms(data.opportunities);
        }
    } catch (error) {
        console.error('Error loading programs:', error);
        container.innerHTML = '<p style="text-align: center; color: #ef4444;">Failed to load programs.</p>';
    }
}

function renderPrograms(programs) {
    const container = document.getElementById('programsList');

    if (!programs || programs.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px;">
                <i class="fas fa-rocket" style="font-size: 48px; color: #a0aec0; margin-bottom: 15px;"></i>
                <p style="color: #a0aec0; margin-bottom: 20px;">No programs created yet</p>
                <button onclick="seedAllDemoData()" style="padding: 10px 20px; background: #4f46e5; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                    <i class="fas fa-magic"></i> Seed All Demo Data
                </button>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <div style="display: flex; justify-content: flex-end; margin-bottom: 1.5rem;">
            <button onclick="seedAllDemoData()" style="font-size: 0.8rem; padding: 5px 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer;">
                <i class="fas fa-plus"></i> Add More Demos
            </button>
        </div>
        <div class="programs-grid" style="display: grid; gap: 1.5rem;">
            ${programs.map(p => `
                <div class="program-card" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem; display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem;">
                            <span style="background: ${p.status === 'published' ? '#f0fdf4' : '#fef2f2'}; color: ${p.status === 'published' ? '#166534' : '#991b1b'}; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase;">
                                ${p.status}
                            </span>
                            <span style="font-size: 0.8rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">
                                ${p.type}
                            </span>
                        </div>
                        <h4 style="font-size: 1.1rem; font-weight: 700; color: #0f172a; margin-bottom: 0.5rem;">${p.title}</h4>
                        <p style="color: #475569; font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.5;">${p.description}</p>
                        <div style="display: flex; gap: 1.5rem; font-size: 0.85rem; color: #64748b;">
                            <span><i class="fas fa-gift" style="margin-right: 5px;"></i> ${p.benefits}</span>
                            <span><i class="fas fa-calendar" style="margin-right: 5px;"></i> Deadline: ${new Date(p.deadline).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

async function seedAllDemoData() {
    try {
        const response = await fetch('/api/admin/seed-all-data', { method: 'POST' });
        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            loadDashboardStats(); // Refresh stats
            loadRecentUsers(); // Refresh user list
            loadPrograms(); // Refresh programs list
        } else {
            showToast(data.message || 'Failed to seed data', 'error');
        }
    } catch (error) {
        console.error('Error seeding data:', error);
        showToast('Error seeding demo data', 'error');
    }
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);

    if (diffInSeconds < 60) return 'Just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
    return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

function showToast(message, type = 'info') {
    document.querySelectorAll('.toast').forEach(toast => toast.remove());

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 100);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function goToPlatform() {
    window.location.href = '/';
}

function updateLastUpdateTime() {
    const el = document.getElementById('lastUpdate');
    if (el) el.textContent = new Date().toLocaleTimeString();
}

function updateLiveInsights() {
    // Simulate concurrent users
    const liveUsers = Math.floor(Math.random() * (45 - 12 + 1)) + 12;
    const liveUsersEl = document.getElementById('liveUsers');
    if (liveUsersEl) liveUsersEl.textContent = liveUsers;

    // Simulate market trend
    const marketTrendEl = document.getElementById('marketTrend');
    if (marketTrendEl) {
        const trends = ['Bullish (+2.4%)', 'Steady (+0.8%)', 'Very Bullish (+4.1%)', 'Growing (+1.2%)'];
        marketTrendEl.textContent = trends[Math.floor(Math.random() * trends.length)];
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('Admin Dashboard restored successfully!');

    loadDashboardStats();
    loadRecentUsers();
    updateLiveInsights();

    setInterval(() => {
        loadDashboardStats();
        updateLastUpdateTime();
        updateLiveInsights();
    }, 30000);

    // Random pings on the live map every few seconds
    setInterval(updateLiveInsights, 8000);

    setInterval(loadRecentUsers, 60000);
});

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;

    try {
        const response = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (response.ok) {
            showToast('User deleted successfully', 'success');
            loadRecentUsers();
            loadDashboardStats();
        } else {
            showToast(data.error || 'Failed to delete user', 'error');
        }
    } catch (error) {
        console.error('Error deleting user:', error);
        showToast('Error deleting user', 'error');
    }
}

async function editUser(id) {
    const user = users.find(u => u.id === id);
    if (!user) return;

    const newName = prompt('Enter new name:', user.full_name || user.name || user.username);
    if (newName === null) return;

    const newRole = prompt('Enter new role (startup/corporate/connector/admin):', user.role);
    if (newRole === null) return;

    try {
        const response = await fetch(`/api/admin/users/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: newName, role: newRole })
        });
        const data = await response.json();

        if (response.ok) {
            showToast('User updated successfully', 'success');
            loadRecentUsers();
            loadDashboardStats();
        } else {
            showToast(data.error || 'Failed to update user', 'error');
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showToast('Error updating user', 'error');
    }
}
