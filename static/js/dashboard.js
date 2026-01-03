let userStats = { totalReferrals: 12, totalEarnings: 450.00, availableRewards: 350.00, pendingRewards: 100.00, flcPoints: 4500 };
function showSection(sectionName) {
    ['profileSection', 'referralsSection', 'rewardsSection', 'earningsSection', 'analyticsSection'].forEach(s => { const el = document.getElementById(s); if (el) el.style.display = 'none'; });
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));
    const sectionEl = document.getElementById(sectionName + 'Section');
    if (sectionEl) sectionEl.style.display = 'block';
    event.target.classList.add('active');
    const titles = { 'profile': 'Profile', 'referrals': 'My Referrals', 'rewards': 'My Rewards', 'earnings': 'Earnings', 'analytics': 'Analytics' };
    const subtitles = { 'profile': 'Manage your account settings and track your performance', 'referrals': 'Track your startup referrals and their progress', 'rewards': 'View your reward balance and earnings history', 'earnings': 'Monitor your earnings and commission payments', 'analytics': 'View detailed performance analytics and insights' };
    document.getElementById('sectionTitle').textContent = titles[sectionName];
    document.getElementById('sectionSubtitle').textContent = subtitles[sectionName];
}
function editProfile() { showAlert('Edit profile feature - Update your personal information here!', 'success'); }
function logout() { if (confirm('Are you sure you want to logout?')) { showAlert('Logging out...', 'success'); setTimeout(() => alert('Logout successful!'), 1000); } }
function cashOut() { if (userStats.availableRewards <= 0) { showAlert('No available balance to cash out', 'error'); return; } if (confirm(`Cash out $${userStats.availableRewards.toFixed(2)}?\n\nProcessing time: 3-5 business days`)) { showAlert(`Cash out request for $${userStats.availableRewards.toFixed(2)} submitted successfully!`, 'success'); } }
function showAlert(message, type = 'success') { const existingAlert = document.querySelector('.alert'); if (existingAlert) existingAlert.remove(); const alert = document.createElement('div'); alert.className = `alert alert-${type}`; alert.textContent = message; alert.style.position = 'fixed'; alert.style.top = '20px'; alert.style.right = '20px'; alert.style.zIndex = '10000'; alert.style.maxWidth = '400px'; alert.style.boxShadow = '0 4px 15px rgba(0,0,0,0.2)'; document.body.appendChild(alert); setTimeout(() => { if (alert && alert.parentNode) { alert.style.transition = 'opacity 0.3s'; alert.style.opacity = '0'; setTimeout(() => alert.remove(), 300); } }, 5000); }
function toggleMobileMenu() { document.getElementById('sidebar').classList.toggle('open'); }
document.addEventListener('click', function (event) { const sidebar = document.getElementById('sidebar'); const menuBtn = document.querySelector('.mobile-menu-btn'); if (window.innerWidth <= 768 && !sidebar.contains(event.target) && !menuBtn.contains(event.target) && sidebar.classList.contains('open')) { sidebar.classList.remove('open'); } });
console.log('Dashboard loaded - Yellow, Black, White theme ready!');
