function createParticles() {
    const container = document.getElementById('particles');
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        const size = 60 + Math.random() * 100;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        particle.style.left = Math.random() * 100 + '%';
        particle.style.bottom = '-200px';
        particle.style.animationDelay = Math.random() * 25 + 's';
        container.appendChild(particle);
    }
}
createParticles();

let currentUser = null;
let analytics = {
    users: [],
    programViews: {},
    applications: [],
    recentActivity: []
};

const programs = [
    {
        id: 1,
        title: 'Global AI Innovation Challenge',
        company: 'AI Innovation Labs',
        description: 'Join the largest AI innovation challenge worldwide.',
        reward: '$100.00',
        views: 0
    },
    {
        id: 2,
        title: 'Web3 & Blockchain Startup Incubator',
        company: 'Blockchain Ventures',
        description: 'Transform your blockchain idea into a thriving business.',
        reward: '$250.00',
        views: 0
    },
    {
        id: 3,
        title: 'Sustainable Innovation Accelerator',
        company: 'GreenTech Global',
        description: 'Drive the green revolution with cutting-edge technologies.',
        reward: '$150.00',
        views: 0
    },
    {
        id: 4,
        title: 'Next-Gen HealthTech Accelerator',
        company: 'MedTech Innovations',
        description: 'Revolutionize healthcare with innovative technology.',
        reward: '$75.00',
        views: 0
    },
    {
        id: 5,
        title: 'Revolutionary FinTech Program',
        company: 'FinTech Future Labs',
        description: 'Shape the future of finance with disruptive technologies.',
        reward: '$200.00',
        views: 0
    },
    {
        id: 6,
        title: 'Space Technology Accelerator',
        company: 'Orbital Ventures',
        description: 'Launch your space technology startup.',
        reward: '$300.00',
        views: 0
    }
];

function addActivity(message) {
    const activity = {
        message,
        timestamp: new Date().toLocaleString()
    };
    analytics.recentActivity.unshift(activity);
    if (analytics.recentActivity.length > 10) {
        analytics.recentActivity = analytics.recentActivity.slice(0, 10);
    }
}

function updateAnalytics() {
    document.getElementById('totalUsers').textContent = analytics.users.length;
    document.getElementById('totalPrograms').textContent = programs.length;

    const totalViews = programs.reduce((sum, p) => sum + p.views, 0);
    document.getElementById('totalViews').textContent = totalViews;
    document.getElementById('totalApplications').textContent = analytics.applications.length;

    const activityList = document.getElementById('activityList');
    if (analytics.recentActivity.length === 0) {
        activityList.innerHTML = '<div class="activity-item">No recent activity</div>';
    } else {
        activityList.innerHTML = analytics.recentActivity.map(activity => `
                    <div class="activity-item">
                        <div>${activity.message}</div>
                        <div class="activity-time">${activity.timestamp}</div>
                    </div>
                `).join('');
    }
}

function showLanding() {
    document.getElementById('landingPage').style.display = 'flex';
    document.getElementById('registerPage').style.display = 'none';
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'none';
}

function showRegister() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'flex';
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'none';
}

function showLogin() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'none';
    document.getElementById('loginPage').style.display = 'flex';
    document.getElementById('dashboardPage').style.display = 'none';
}

function showDashboard() {
    document.getElementById('landingPage').style.display = 'none';
    document.getElementById('registerPage').style.display = 'none';
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('dashboardPage').style.display = 'block';
    updateAnalytics();
    renderPrograms();
}

function showAlert(elementId, message, type) {
    const alert = document.getElementById(elementId);
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    setTimeout(() => alert.classList.remove('show'), 5000);
}

function handleRegister() {
    const firstName = document.getElementById('regFirstName').value.trim();
    const lastName = document.getElementById('regLastName').value.trim();
    const startupName = document.getElementById('regStartupName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;

    if (analytics.users.find(u => u.email === email)) {
        showAlert('registerAlert', 'Email already registered', 'error');
        return;
    }

    const newUser = {
        id: Date.now(),
        firstName,
        lastName,
        startupName,
        email,
        password,
        createdAt: new Date().toISOString()
    };

    analytics.users.push(newUser);
    addActivity(`New user registered: ${startupName}`);

    showAlert('registerAlert', 'Registration successful! Please login.', 'success');
    setTimeout(() => {
        document.getElementById('registerForm').reset();
        showLogin();
    }, 2000);
}

function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    const user = analytics.users.find(u => u.email === email && u.password === password);

    if (user) {
        currentUser = user;
        document.getElementById('userName').textContent = user.startupName;
        addActivity(`${user.startupName} logged in`);
        showAlert('loginAlert', 'Login successful!', 'success');
        setTimeout(() => {
            document.getElementById('loginForm').reset();
            showDashboard();
        }, 1000);
    } else {
        showAlert('loginAlert', 'Invalid email or password', 'error');
    }
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        addActivity(`${currentUser.startupName} logged out`);
        currentUser = null;
        showLanding();
    }
}

function renderPrograms() {
    const grid = document.getElementById('programsGrid');
    grid.innerHTML = programs.map(program => `
                <div class="program-card">
                    <div class="program-title">${program.title}</div>
                    <div class="program-company"><i class="fas fa-building"></i> ${program.company}</div>
                    <div class="program-description">${program.description}</div>
                    <div class="program-meta">
                        <span class="program-views"><i class="fas fa-eye"></i> ${program.views} views</span>
                        <span class="program-reward"><i class="fas fa-gift"></i> ${program.reward}</span>
                    </div>
                    <button class="apply-btn" onclick="viewProgram(${program.id})">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            `).join('');
}

function viewProgram(programId) {
    const program = programs.find(p => p.id === programId);
    if (program && currentUser) {
        program.views++;
        addActivity(`${currentUser.startupName} viewed ${program.title}`);

        const apply = confirm(`${program.title}\n\nCompany: ${program.company}\nReward: ${program.reward}\n\nWould you like to apply?`);

        if (apply) {
            analytics.applications.push({
                user: currentUser.startupName,
                program: program.title,
                timestamp: new Date().toISOString()
            });
            addActivity(`${currentUser.startupName} applied to ${program.title}`);
            alert('Application submitted successfully!');
        }

        updateAnalytics();
        renderPrograms();
    }
}

document.addEventListener('DOMContentLoaded', showLanding);
