/**
 * Admin Analytics Dashboard
 * Advanced analytics and reporting for admin panel
 */

let analyticsCharts = {};
let currentPeriod = 30; // days

// Initialize analytics when section is loaded
async function initializeAnalytics() {
    await loadAllAnalytics();
    setupPeriodSelector();
}

// Setup period selector
function setupPeriodSelector() {
    const selector = document.getElementById('analyticsPeriodSelector');
    if (selector) {
        selector.addEventListener('change', (e) => {
            currentPeriod = parseInt(e.target.value);
            loadAllAnalytics();
        });
    }
}

// Load all analytics data
async function loadAllAnalytics() {
    showAnalyticsLoading();
    
    try {
        await Promise.all([
            loadPlatformHealth(),
            loadUserGrowth(),
            loadApplicationFunnel(),
            loadProgramPerformance(),
            loadReferralAnalytics(),
            loadMeetingAnalytics(),
            loadLeadAnalytics(),
            loadRevenueAnalytics()
        ]);
        
        hideAnalyticsLoading();
    } catch (error) {
        console.error('Error loading analytics:', error);
        showToast('Failed to load analytics', 'error');
        hideAnalyticsLoading();
    }
}

// Platform Health
async function loadPlatformHealth() {
    try {
        const response = await fetch('/api/admin/analytics/platform-health');
        const result = await response.json();
        
        if (result.success) {
            displayPlatformHealth(result.data);
        }
    } catch (error) {
        console.error('Error loading platform health:', error);
    }
}

function displayPlatformHealth(data) {
    // Health score
    const healthScore = data.health_score;
    const healthEl = document.getElementById('healthScore');
    if (healthEl) {
        healthEl.textContent = healthScore;
        healthEl.className = 'health-score ' + getHealthClass(healthScore);
    }

    // Weekly activity
    document.getElementById('weeklyNewUsers').textContent = data.weekly_activity.new_users;
    document.getElementById('weeklyNewApplications').textContent = data.weekly_activity.new_applications;
    document.getElementById('weeklyNewMeetings').textContent = data.weekly_activity.new_meetings;
    document.getElementById('weeklyNewLeads').textContent = data.weekly_activity.new_leads;

    // Growth rate
    const growthRate = data.growth_rates.user_growth;
    const growthEl = document.getElementById('userGrowthRate');
    if (growthEl) {
        growthEl.textContent = `${growthRate > 0 ? '+' : ''}${growthRate}%`;
        growthEl.className = growthRate >= 0 ? 'positive' : 'negative';
    }
}

function getHealthClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'fair';
    return 'poor';
}

// User Growth Analytics
async function loadUserGrowth() {
    try {
        const response = await fetch(`/api/admin/analytics/user-growth?days=${currentPeriod}`);
        const result = await response.json();
        
        if (result.success) {
            displayUserGrowthChart(result.data);
            displayRoleDistribution(result.data);
        }
    } catch (error) {
        console.error('Error loading user growth:', error);
    }
}

function displayUserGrowthChart(data) {
    const ctx = document.getElementById('userGrowthChart');
    if (!ctx) return;

    // Destroy existing chart
    if (analyticsCharts.userGrowth) {
        analyticsCharts.userGrowth.destroy();
    }

    const labels = data.daily_registrations.map(d => d.date);
    const values = data.daily_registrations.map(d => d.count);

    analyticsCharts.userGrowth = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'New Users',
                data: values,
                borderColor: '#4f46e5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

function displayRoleDistribution(data) {
    const ctx = document.getElementById('roleDistributionChart');
    if (!ctx) return;

    if (analyticsCharts.roleDistribution) {
        analyticsCharts.roleDistribution.destroy();
    }

    const labels = data.total_by_role.map(r => r.role);
    const values = data.total_by_role.map(r => r.count);
    const colors = ['#4f46e5', '#fcb82e', '#10b981', '#ef4444', '#8b5cf6'];

    analyticsCharts.roleDistribution = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: colors.slice(0, labels.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Application Funnel
async function loadApplicationFunnel() {
    try {
        const response = await fetch('/api/admin/analytics/application-funnel');
        const result = await response.json();
        
        if (result.success) {
            displayApplicationFunnel(result.data);
        }
    } catch (error) {
        console.error('Error loading application funnel:', error);
    }
}

function displayApplicationFunnel(data) {
    // Update metrics
    document.getElementById('totalStartups').textContent = data.total_startups;
    document.getElementById('startupsWithApps').textContent = data.startups_with_applications;
    document.getElementById('conversionRate').textContent = data.conversion_rate + '%';
    document.getElementById('acceptanceRate').textContent = data.acceptance_rate + '%';

    // Funnel chart
    const ctx = document.getElementById('applicationFunnelChart');
    if (!ctx) return;

    if (analyticsCharts.applicationFunnel) {
        analyticsCharts.applicationFunnel.destroy();
    }

    const labels = data.status_breakdown.map(s => s.status);
    const values = data.status_breakdown.map(s => s.count);

    analyticsCharts.applicationFunnel = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Applications',
                data: values,
                backgroundColor: '#fcb82e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Program Performance
async function loadProgramPerformance() {
    try {
        const response = await fetch('/api/admin/analytics/program-performance');
        const result = await response.json();
        
        if (result.success) {
            displayProgramPerformance(result.data);
        }
    } catch (error) {
        console.error('Error loading program performance:', error);
    }
}

function displayProgramPerformance(data) {
    const tbody = document.getElementById('programPerformanceTable');
    if (!tbody) return;

    if (data.program_stats.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; padding:20px;">No programs found</td></tr>';
        return;
    }

    tbody.innerHTML = data.program_stats.map(program => `
        <tr>
            <td>
                <div style="font-weight: 600;">${program.title}</div>
                <div style="font-size: 12px; color: #666;">${program.type}</div>
            </td>
            <td><span class="status-badge status-${program.status}">${program.status}</span></td>
            <td style="text-align: center;">${program.applications}</td>
            <td style="text-align: center;">${program.accepted}</td>
            <td style="text-align: center;">
                <span style="color: ${program.acceptance_rate >= 50 ? '#10b981' : '#ef4444'}; font-weight: 600;">
                    ${program.acceptance_rate}%
                </span>
            </td>
        </tr>
    `).join('');

    // Program type distribution chart
    displayProgramTypeChart(data.type_distribution);
}

function displayProgramTypeChart(typeData) {
    const ctx = document.getElementById('programTypeChart');
    if (!ctx) return;

    if (analyticsCharts.programType) {
        analyticsCharts.programType.destroy();
    }

    const labels = typeData.map(t => t.type);
    const values = typeData.map(t => t.count);

    analyticsCharts.programType = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: ['#4f46e5', '#fcb82e', '#10b981', '#ef4444', '#8b5cf6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

// Referral Analytics
async function loadReferralAnalytics() {
    try {
        const response = await fetch('/api/admin/analytics/referrals');
        const result = await response.json();
        
        if (result.success) {
            displayReferralAnalytics(result.data);
        }
    } catch (error) {
        console.error('Error loading referral analytics:', error);
    }
}

function displayReferralAnalytics(data) {
    document.getElementById('totalReferrals').textContent = data.total_referrals;
    document.getElementById('successfulReferrals').textContent = data.successful_referrals;
    document.getElementById('referralConversionRate').textContent = data.conversion_rate + '%';
    document.getElementById('totalCommissions').textContent = '$' + data.total_commissions.toFixed(2);

    // Top enablers table
    const tbody = document.getElementById('topEnablersTable');
    if (tbody && data.top_enablers.length > 0) {
        tbody.innerHTML = data.top_enablers.map((enabler, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${enabler.name}</td>
                <td style="text-align: center;">${enabler.referrals}</td>
                <td style="text-align: right; color: #10b981; font-weight: 600;">$${enabler.commission.toFixed(2)}</td>
            </tr>
        `).join('');
    }
}

// Meeting Analytics
async function loadMeetingAnalytics() {
    try {
        const response = await fetch(`/api/admin/analytics/meetings?days=${currentPeriod}`);
        const result = await response.json();
        
        if (result.success) {
            displayMeetingAnalytics(result.data);
        }
    } catch (error) {
        console.error('Error loading meeting analytics:', error);
    }
}

function displayMeetingAnalytics(data) {
    document.getElementById('totalMeetingsAnalytics').textContent = data.total_meetings;
    document.getElementById('avgMeetingDuration').textContent = data.average_duration + ' min';
    document.getElementById('totalMeetingParticipants').textContent = data.total_participants;

    // Daily meetings chart
    const ctx = document.getElementById('meetingTrendChart');
    if (!ctx) return;

    if (analyticsCharts.meetingTrend) {
        analyticsCharts.meetingTrend.destroy();
    }

    const labels = data.daily_meetings.map(m => m.date);
    const values = data.daily_meetings.map(m => m.count);

    analyticsCharts.meetingTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Meetings Created',
                data: values,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Lead Analytics
async function loadLeadAnalytics() {
    try {
        const response = await fetch(`/api/admin/analytics/leads?days=${currentPeriod}`);
        const result = await response.json();
        
        if (result.success) {
            displayLeadAnalytics(result.data);
        }
    } catch (error) {
        console.error('Error loading lead analytics:', error);
    }
}

function displayLeadAnalytics(data) {
    document.getElementById('totalLeadsAnalytics').textContent = data.total_leads;
    document.getElementById('unreadLeads').textContent = data.unread_leads;
    document.getElementById('leadResponseRate').textContent = data.response_rate + '%';

    // Lead type breakdown chart
    const ctx = document.getElementById('leadTypeChart');
    if (!ctx) return;

    if (analyticsCharts.leadType) {
        analyticsCharts.leadType.destroy();
    }

    const labels = data.type_breakdown.map(t => t.type);
    const values = data.type_breakdown.map(t => t.count);

    analyticsCharts.leadType = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Leads',
                data: values,
                backgroundColor: ['#4f46e5', '#10b981', '#fcb82e']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
}

// Revenue Analytics
async function loadRevenueAnalytics() {
    try {
        const response = await fetch(`/api/admin/analytics/revenue?days=${currentPeriod}`);
        const result = await response.json();
        
        if (result.success) {
            displayRevenueAnalytics(result.data);
        }
    } catch (error) {
        console.error('Error loading revenue analytics:', error);
    }
}

function displayRevenueAnalytics(data) {
    document.getElementById('totalRevenueAnalytics').textContent = '$' + data.total_commissions.toFixed(2);

    // Daily revenue chart
    const ctx = document.getElementById('revenueChart');
    if (!ctx) return;

    if (analyticsCharts.revenue) {
        analyticsCharts.revenue.destroy();
    }

    const labels = data.daily_commissions.map(c => c.date);
    const values = data.daily_commissions.map(c => c.amount);

    analyticsCharts.revenue = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Revenue',
                data: values,
                backgroundColor: '#10b981'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toFixed(2);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            }
        }
    });
}

// Export analytics
async function exportAnalytics(type) {
    try {
        const response = await fetch(`/api/admin/analytics/export/${type}?days=${currentPeriod}`);
        const blob = await response.blob();
        
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${type}_analytics_${currentPeriod}days.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('Analytics exported successfully!');
    } catch (error) {
        console.error('Error exporting analytics:', error);
        showToast('Failed to export analytics', 'error');
    }
}

// Loading states
function showAnalyticsLoading() {
    const container = document.getElementById('analyticsContent');
    if (container) {
        container.style.opacity = '0.5';
        container.style.pointerEvents = 'none';
    }
}

function hideAnalyticsLoading() {
    const container = document.getElementById('analyticsContent');
    if (container) {
        container.style.opacity = '1';
        container.style.pointerEvents = 'auto';
    }
}

// Refresh analytics
function refreshAnalytics() {
    loadAllAnalytics();
    showToast('Analytics refreshed');
}
