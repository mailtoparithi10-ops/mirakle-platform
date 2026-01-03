/* startup.js — page-specific behavior for startup portal */

/* In-memory users & demo programs (as in your original) */
let currentUser = null;
const users = [];

const programs = [
    {
        id: 1,
        title: 'Global AI Innovation Challenge',
        company: 'AI Innovation Labs',
        description: 'Join the largest AI innovation challenge worldwide. Build next-generation AI solutions with cutting-edge technologies and compete for substantial rewards.',
        reward: '$100.00',
        stage: 'All stages',
        sector: 'AI/ML'
    },
    {
        id: 2,
        title: 'Web3 & Blockchain Startup Incubator',
        company: 'Blockchain Ventures',
        description: 'Transform your blockchain idea into a thriving business with mentorship and funding from industry leaders in decentralized technology.',
        reward: '$250.00',
        stage: 'Seed to Series A',
        sector: 'Blockchain'
    },
    {
        id: 3,
        title: 'Sustainable Innovation Accelerator',
        company: 'GreenTech Global',
        description: 'Drive the green revolution with cutting-edge sustainable technologies. Partner with leading environmental organizations for a cleaner future.',
        reward: '$150.00',
        stage: 'Seed to Series A',
        sector: 'CleanTech'
    },
    {
        id: 4,
        title: 'Next-Gen HealthTech Accelerator',
        company: 'MedTech Innovations',
        description: 'Revolutionize healthcare with innovative technology solutions. Partner with leading medical institutions and healthcare providers worldwide.',
        reward: '$75.00',
        stage: 'Seed to Series A',
        sector: 'HealthTech'
    },
    {
        id: 5,
        title: 'Revolutionary FinTech Program',
        company: 'FinTech Future Labs',
        description: 'Shape the future of finance with disruptive technologies. Gain access to top-tier VCs and financial institution partnerships.',
        reward: '$200.00',
        stage: 'Seed to Series A',
        sector: 'FinTech'
    },
    {
        id: 6,
        title: 'Space Technology Accelerator',
        company: 'Orbital Ventures',
        description: 'Launch your space technology startup with unprecedented access to space agencies and aerospace giants. Pioneer the next frontier of innovation.',
        reward: '$300.00',
        stage: 'Seed to Series A',
        sector: 'SpaceTech'
    }
];

/* --- Page show/hide helpers --- */
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
    renderPrograms();
}

/* --- Alerts --- */
function showAlert(elementId, message, type) {
    const alert = document.getElementById(elementId);
    if (!alert) return;
    alert.className = `alert alert-${type} show`;
    alert.textContent = message;
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

/* --- Registration / Login / Logout --- */
function handleRegister() {
    const firstName = document.getElementById('regFirstName').value.trim();
    const lastName = document.getElementById('regLastName').value.trim();
    const startupName = document.getElementById('regStartupName').value.trim();
    const email = document.getElementById('regEmail').value.trim();
    const password = document.getElementById('regPassword').value;

    if (!firstName || !lastName || !startupName || !email || !password) {
        showAlert('registerAlert', 'Please fill in all fields', 'error');
        return;
    }

    if (password.length < 6) {
        showAlert('registerAlert', 'Password must be at least 6 characters', 'error');
        return;
    }

    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
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

    users.push(newUser);
    showAlert('registerAlert', 'Registration successful! Redirecting to login...', 'success');

    setTimeout(() => {
        document.getElementById('registerForm').reset();
        showLogin();
    }, 2000);
}

function handleLogin() {
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('loginAlert', 'Please fill in all fields', 'error');
        return;
    }

    const user = users.find(u => u.email === email && u.password === password);

    if (user) {
        currentUser = user;
        const nameEl = document.getElementById('userName');
        if (nameEl) nameEl.textContent = user.startupName || `${user.firstName} ${user.lastName}`;
        showAlert('loginAlert', 'Login successful! Redirecting...', 'success');
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
        currentUser = null;
        showLanding();
    }
}

/* --- Programs render + apply --- */
function renderPrograms() {
    const grid = document.getElementById('programsGrid');
    if (!grid) return;
    grid.innerHTML = programs.map(program => `
        <div class="program-card">
            <div class="program-title">${program.title}</div>
            <div class="program-company"><i class="fas fa-building"></i> ${program.company}</div>
            <div class="program-description">${program.description}</div>
            <div class="program-meta">
                <span><i class="fas fa-chart-line"></i> ${program.stage}</span>
                <span class="program-reward"><i class="fas fa-gift"></i> ${program.reward}</span>
            </div>
            <button class="apply-btn" onclick="applyToProgram(${program.id})">
                <i class="fas fa-paper-plane"></i> APPLY NOW
            </button>
        </div>
    `).join('');
}

function applyToProgram(programId) {
    const program = programs.find(p => p.id === programId);
    if (program && currentUser) {
        alert(`Application Submitted Successfully!\n\nProgram: ${program.title}\nStartup: ${currentUser.startupName}\n\nYou will receive a confirmation email at ${currentUser.email} shortly.`);
    } else if (!currentUser) {
        alert('Please login to apply for programs.');
        showLogin();
    }
}

/* --- Initialize page --- */
document.addEventListener('DOMContentLoaded', function () {
    showLanding();
});
