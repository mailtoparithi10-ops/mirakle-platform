let users = [];
let currentFilter = 'all';
let currentStats = {
    totalUsers: 0,
    totalStartups: 0,
    totalCorporate: 0,
    totalPrograms: 0
};

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/admin/stats');
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;

            animateStatChange('totalUsers', currentStats.totalUsers, stats.total_users);
            animateStatChange('totalStartups', currentStats.totalStartups, stats.total_startups);
            animateStatChange('totalCorporate', currentStats.totalCorporate, stats.total_corporate);
            animateStatChange('totalPrograms', currentStats.totalPrograms, stats.total_programs);

            currentStats = {
                totalUsers: stats.total_users,
                totalStartups: stats.total_startups,
                totalCorporate: stats.total_corporate,
                totalPrograms: stats.total_programs
            };
        }
    } catch (error) {
        console.error('Error loading stats:', error);
        showToast('Error loading dashboard stats', 'error');
    }
}

async function loadRecentUsers() {
    try {
        const response = await fetch('/api/admin/users');
        const data = await response.json();

        if (data.success) {
            users = data.users || [];
            updateUserCounts();
            renderRecentUsers();

            if (document.getElementById('usersSection').style.display !== 'none') {
                renderFilteredUsers();
            }
            if (document.getElementById('startupsSection').style.display !== 'none') {
                renderStartupUsers();
            }
            if (document.getElementById('corporateSection').style.display !== 'none') {
                renderCorporateUsers();
            }
        }
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function updateUserCounts() {
    const counts = {
        all: users.length,
        startup: users.filter(u => u.role === 'startup').length,
        corporate: users.filter(u => u.role === 'corporate').length,
        enabler: users.filter(u => u.role === 'enabler').length
    };

    document.getElementById('allCount').textContent = counts.all;
    document.getElementById('startupCount').textContent = counts.startup;
    document.getElementById('corporateCount').textContent = counts.corporate;
    document.getElementById('enablerCount').textContent = counts.enabler;
}

function getDisplayName(user) {
    if (user.role === 'corporate' && user.corporate_name) {
        return user.corporate_name;
    }

    if (user.first_name && user.last_name) {
        return `${user.first_name} ${user.last_name}`;
    }

    if (user.full_name) {
        return user.full_name;
    }

    if (user.username && user.username.includes('_')) {
        const parts = user.username.split('_');
        return parts.map(part => part.charAt(0).toUpperCase() + part.slice(1)).join(' ');
    }

    if (user.email && user.email.includes('@')) {
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
    if (user.first_name && user.last_name) {
        return (user.first_name[0] + user.last_name[0]).toUpperCase();
    }

    if (user.full_name) {
        const parts = user.full_name.split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return user.full_name.substring(0, 2).toUpperCase();
    }

    if (user.corporate_name) {
        const parts = user.corporate_name.split(' ');
        if (parts.length >= 2) {
            return (parts[0][0] + parts[1][0]).toUpperCase();
        }
        return user.corporate_name.substring(0, 2).toUpperCase();
    }

    if (!user.username) return '??';

    if (user.username.includes('@')) {
        const emailPart = user.username.split('@')[0];
        return emailPart.substring(0, 2).toUpperCase();
    }

    const parts = user.username.split('_');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }

    return user.username.substring(0, 2).toUpperCase();
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
        filteredUsers = users.filter(u => u.role === currentFilter);
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

    container.innerHTML = sortedUsers.map(user => {
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
                            <div class="user-role">${user.role.toUpperCase()} • Joined ${timeAgo}</div>
                            <div class="user-details">
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Email</div>
                                    <div class="user-detail-value">${user.email}</div>
                                </div>
                                ${user.phone_number ? `
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Phone</div>
                                    <div class="user-detail-value">${user.phone_number}</div>
                                </div>
                                ` : ''}
                                ${user.corporate_name ? `
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Company</div>
                                    <div class="user-detail-value">${user.corporate_name}</div>
                                </div>
                                ` : ''}
                                <div class="user-detail-item">
                                    <div class="user-detail-label">User ID</div>
                                    <div class="user-detail-value">#${user.id}</div>
                                </div>
                            </div>
                            <div class="user-actions" style="margin-top: 10px; display: flex; gap: 10px;">
                                <button onclick="editUser(${user.id})" style="padding: 5px 10px; background: #fcb82e; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Edit</button>
                                <button onclick="deleteUser(${user.id})" style="padding: 5px 10px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Delete</button>
                            </div>
                        </div>
                        <div class="user-status status-offline">
                            <span class="status-dot"></span>
                            Offline
                        </div>
                    </div>
                `;
    }).join('');
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

    container.innerHTML = sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
                    <div class="user-item">
                        <div class="user-avatar startup">
                            ${initials}
                        </div>
                        <div class="user-info">
                            <div class="user-name">${displayName}</div>
                            <div class="user-role">STARTUP • Joined ${timeAgo}</div>
                            <div class="user-details">
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Email</div>
                                    <div class="user-detail-value">${user.email}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Username</div>
                                    <div class="user-detail-value">${user.username}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">User ID</div>
                                    <div class="user-detail-value">#${user.id}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Registration Date</div>
                                    <div class="user-detail-value">${new Date(user.created_at).toLocaleDateString()}</div>
                                </div>
                            </div>
                            <div class="user-actions" style="margin-top: 10px; display: flex; gap: 10px;">
                                <button onclick="editUser(${user.id})" style="padding: 5px 10px; background: #fcb82e; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Edit</button>
                                <button onclick="deleteUser(${user.id})" style="padding: 5px 10px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Delete</button>
                            </div>
                        </div>
                        <div class="user-status status-offline">
                            <span class="status-dot"></span>
                            Offline
                        </div>
                    </div>
                `;
    }).join('');
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

    container.innerHTML = sortedUsers.map(user => {
        const initials = getUserInitials(user);
        const timeAgo = formatTimeAgo(user.created_at);
        const displayName = getDisplayName(user);

        return `
                    <div class="user-item">
                        <div class="user-avatar corporate">
                            ${initials}
                        </div>
                        <div class="user-info">
                            <div class="user-name">${displayName}</div>
                            <div class="user-role">CORPORATE • Joined ${timeAgo}</div>
                            <div class="user-details">
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Contact Person</div>
                                    <div class="user-detail-value">${user.full_name || 'N/A'}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Company Name</div>
                                    <div class="user-detail-value">${user.corporate_name || 'N/A'}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Email</div>
                                    <div class="user-detail-value">${user.email}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Phone</div>
                                    <div class="user-detail-value">${user.phone_number || 'N/A'}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">User ID</div>
                                    <div class="user-detail-value">#${user.id}</div>
                                </div>
                                <div class="user-detail-item">
                                    <div class="user-detail-label">Registration Date</div>
                                    <div class="user-detail-value">${new Date(user.created_at).toLocaleDateString()}</div>
                                </div>
                            </div>
                            <div class="user-actions" style="margin-top: 10px; display: flex; gap: 10px;">
                                <button onclick="editUser(${user.id})" style="padding: 5px 10px; background: #fcb82e; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Edit</button>
                                <button onclick="deleteUser(${user.id})" style="padding: 5px 10px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600;">Delete</button>
                            </div>
                        </div>
                        <div class="user-status status-offline">
                            <span class="status-dot"></span>
                            Offline
                        </div>
                    </div>
                `;
    }).join('');
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
        }
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
    window.location.href = 'index.html';
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        fetch('/logout', { method: 'GET' })
            .then(() => {
                window.location.href = '/';
            })
            .catch(() => {
                window.location.href = '/';
            });
    }
}

function updateLastUpdateTime() {
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString();
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('Admin Dashboard loaded successfully!');

    loadDashboardStats();
    loadRecentUsers();

    setInterval(() => {
        loadDashboardStats();
        updateLastUpdateTime();
    }, 30000);

    setInterval(loadRecentUsers, 60000);

    showToast('Admin Dashboard loaded successfully!', 'success');
});

async function deleteUser(id) {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) return;

    try {
        const response = await fetch(`/api/admin/users/${id}`, { method: 'DELETE' });
        const data = await response.json();

        if (response.ok) {
            showToast('User deleted successfully', 'success');
            loadRecentUsers(); // Reload list
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

    const newName = prompt('Enter new name:', user.full_name || user.corporate_name || user.first_name || user.username);
    if (newName === null) return; // Cancelled

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
            loadRecentUsers(); // Reload list
        } else {
            showToast(data.error || 'Failed to update user', 'error');
        }
    } catch (error) {
        console.error('Error updating user:', error);
        showToast('Error updating user', 'error');
    }
}
