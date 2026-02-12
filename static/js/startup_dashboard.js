// Startup Dashboard JavaScript
// Handles analytics, connections, achievements, and real-time updates

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadAnalytics();
    loadConnections();
    loadAchievements();
    setupConnectionHandlers();
    
    // Refresh data periodically
    setInterval(loadAnalytics, 60000); // Every minute
    setInterval(loadConnections, 30000); // Every 30 seconds
});

// ==================== ANALYTICS ====================

async function loadAnalytics() {
    try {
        const response = await fetch('/api/startups/analytics');
        const data = await response.json();
        
        if (data.success) {
            updateAnalyticsCharts(data);
            updateAnalyticsSummary(data.summary);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function updateAnalyticsCharts(data) {
    // Update Funnel Chart
    if (window.funnelChart && data.funnel) {
        window.funnelChart.data.labels = data.funnel.labels;
        window.funnelChart.data.datasets[0].data = data.funnel.data;
        window.funnelChart.update();
    }
    
    // Update Growth Chart
    if (window.growthChart && data.growth) {
        window.growthChart.data.labels = data.growth.labels;
        window.growthChart.data.datasets[0].data = data.growth.data;
        window.growthChart.update();
    }
    
    // Update Radar Chart
    if (window.radarChart && data.radar) {
        window.radarChart.data.labels = data.radar.labels;
        window.radarChart.data.datasets[0].data = data.radar.values;
        window.radarChart.update();
    }
}

function updateAnalyticsSummary(summary) {
    if (!summary) return;
    
    // Update summary stats if elements exist
    const elements = {
        'profile-views': summary.profile_views,
        'referrals-received': summary.referrals_received,
        'applications-filed': summary.applications_filed,
        'applications-selected': summary.applications_selected,
        'conversion-rate': summary.conversion_rate + '%'
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    });
}

// ==================== CONNECTIONS ====================

async function loadConnections() {
    try {
        // Load suggestions
        const suggestionsResponse = await fetch('/api/connections/suggestions?limit=5');
        const suggestionsData = await suggestionsResponse.json();
        
        if (suggestionsData.success) {
            renderConnectionSuggestions(suggestionsData.suggestions);
        }
        
        // Load existing connections
        const connectionsResponse = await fetch('/api/connections/');
        const connectionsData = await connectionsResponse.json();
        
        if (connectionsData.success) {
            renderConnections(connectionsData.connections);
        }
        
        // Load connection stats
        const statsResponse = await fetch('/api/connections/stats');
        const statsData = await statsResponse.json();
        
        if (statsData.success) {
            updateConnectionStats(statsData.stats);
        }
    } catch (error) {
        console.error('Error loading connections:', error);
    }
}

function renderConnectionSuggestions(suggestions) {
    const container = document.getElementById('connectionSuggestions');
    if (!container) return;
    
    if (suggestions.length === 0) {
        container.innerHTML = `
            <p style="text-align: center; color: var(--text-dim); padding: 1rem;">
                No suggestions available right now.
            </p>
        `;
        return;
    }
    
    container.innerHTML = suggestions.map(user => {
        const avatarContent = user.profile_pic 
            ? `<img src="${user.profile_pic}" alt="${user.name}" style="width: 100%; height: 100%; object-fit: cover;">`
            : user.name.charAt(0).toUpperCase();
        
        return `
            <div style="display: flex; align-items: center; gap: 15px; padding: 12px; background: #f8fafc; border-radius: 12px; transition: var(--transition); border: 1px solid transparent;"
                onmouseover="this.style.borderColor='var(--primary)'"
                onmouseout="this.style.borderColor='transparent'">
                <div class="avatar" style="background: var(--primary); color: #000; font-weight: 800; font-size: 0.8rem; overflow: hidden;">
                    ${avatarContent}
                </div>
                <div style="flex: 1;">
                    <h4 style="font-size: 0.9rem; font-weight: 800; margin-bottom: 2px;">${user.name}</h4>
                    <p style="font-size: 0.75rem; color: var(--text-dim);">${user.company || user.role}</p>
                </div>
                <button class="btn btn-black connect-btn" style="padding: 6px 12px; font-size: 0.75rem;"
                    onclick="sendConnectionRequest(${user.id}, '${user.name}')">Connect</button>
            </div>
        `;
    }).join('');
}

function renderConnections(connections) {
    const container = document.getElementById('userConnections');
    if (!container) return;
    
    if (connections.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <i class="fas fa-link-slash" style="font-size: 2rem; color: var(--text-dim); margin-bottom: 1rem;"></i>
                <p style="font-size: 0.85rem; color: var(--text-dim);">
                    You haven't made any direct connections yet. Start connecting with suggested experts!
                </p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = connections.slice(0, 5).map(conn => {
        const user = conn.user;
        const avatarContent = user.profile_pic 
            ? `<img src="${user.profile_pic}" alt="${user.name}" style="width: 100%; height: 100%; object-fit: cover;">`
            : user.name.charAt(0).toUpperCase();
        
        return `
            <div style="display: flex; align-items: center; gap: 15px; padding: 12px; background: #f8fafc; border-radius: 12px;">
                <div class="avatar" style="background: #3b82f6; color: #fff; font-weight: 800; font-size: 0.8rem; overflow: hidden;">
                    ${avatarContent}
                </div>
                <div style="flex: 1;">
                    <h4 style="font-size: 0.9rem; font-weight: 800; margin-bottom: 2px;">${user.name}</h4>
                    <p style="font-size: 0.75rem; color: var(--text-dim);">${user.company || user.role}</p>
                </div>
                <button class="btn btn-outline" style="padding: 6px 12px; font-size: 0.75rem;"
                    onclick="window.location.href='/messages?user=${user.id}'">Message</button>
            </div>
        `;
    }).join('');
}

function updateConnectionStats(stats) {
    const totalEl = document.getElementById('totalConnections');
    if (totalEl) totalEl.textContent = stats.total_connections;
    
    const pendingEl = document.getElementById('pendingConnections');
    if (pendingEl) pendingEl.textContent = stats.pending_received;
}

async function sendConnectionRequest(userId, userName) {
    if (!confirm(`Send connection request to ${userName}?`)) return;
    
    try {
        const response = await fetch('/api/connections/request', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                recipient_id: userId,
                message: 'I would love to connect with you on Alchemy!'
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Connection request sent!', 'success');
            loadConnections(); // Refresh
        } else {
            showNotification(data.message || 'Failed to send request', 'error');
        }
    } catch (error) {
        console.error('Error sending connection request:', error);
        showNotification('Failed to send connection request', 'error');
    }
}

function setupConnectionHandlers() {
    // Handle connection request acceptance/rejection
    document.addEventListener('click', async (e) => {
        if (e.target.classList.contains('accept-connection')) {
            const connectionId = e.target.dataset.connectionId;
            await handleConnectionAction(connectionId, 'accept');
        } else if (e.target.classList.contains('reject-connection')) {
            const connectionId = e.target.dataset.connectionId;
            await handleConnectionAction(connectionId, 'reject');
        }
    });
}

async function handleConnectionAction(connectionId, action) {
    try {
        const response = await fetch(`/api/connections/${connectionId}/${action}`, {
            method: 'PUT'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Connection ${action}ed!`, 'success');
            loadConnections(); // Refresh
        } else {
            showNotification(data.message || `Failed to ${action} connection`, 'error');
        }
    } catch (error) {
        console.error(`Error ${action}ing connection:`, error);
        showNotification(`Failed to ${action} connection`, 'error');
    }
}

// ==================== ACHIEVEMENTS ====================

async function loadAchievements() {
    try {
        // Note: You'll need to create this endpoint
        const response = await fetch('/api/achievements/user');
        const data = await response.json();
        
        if (data.success || data.earned) {
            renderAchievements(data);
        }
    } catch (error) {
        console.error('Error loading achievements:', error);
        // Fallback to static achievements if API not ready
        renderStaticAchievements();
    }
}

function renderAchievements(data) {
    const container = document.querySelector('.badges-container');
    if (!container) return;
    
    const earned = data.earned || [];
    const locked = data.locked || [];
    
    // Render earned achievements
    const earnedHTML = earned.map(ach => `
        <div class="badge-card earned" title="${ach.description}">
            <i class="fas ${ach.icon}"></i>
            <h4>${ach.name}</h4>
            <p>${ach.description}</p>
            <small style="color: var(--primary); font-weight: 800;">+${ach.points} pts</small>
        </div>
    `).join('');
    
    // Render locked achievements with progress
    const lockedHTML = locked.slice(0, 5).map(ach => `
        <div class="badge-card" title="${ach.description}">
            <i class="fas ${ach.icon}"></i>
            <h4>${ach.name}</h4>
            <p>${ach.description}</p>
            <div style="margin-top: 8px;">
                <div style="background: #e5e7eb; height: 4px; border-radius: 2px; overflow: hidden;">
                    <div style="background: var(--primary); height: 100%; width: ${ach.progress}%;"></div>
                </div>
                <small style="color: var(--text-dim); font-size: 0.7rem;">${ach.progress}% complete</small>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = earnedHTML + lockedHTML;
    
    // Update total points
    const pointsEl = document.getElementById('totalPoints');
    if (pointsEl) pointsEl.textContent = data.total_points || 0;
}

function renderStaticAchievements() {
    // Fallback static rendering (current implementation)
    console.log('Using static achievements');
}

// ==================== UTILITIES ====================

function showNotification(message, type = 'info') {
    // Simple notification (you can enhance this with a toast library)
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Export functions for global use
window.DashboardApp = {
    loadAnalytics,
    loadConnections,
    loadAchievements,
    sendConnectionRequest,
    showNotification
};
