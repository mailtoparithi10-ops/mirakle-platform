// Global state
let currentUser = null;
let isAuthenticated = false;

// Check authentication status on page load
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/user');
        const data = await response.json();

        if (data.authenticated) {
            isAuthenticated = true;
            currentUser = data.user;
            updateAuthUI(data.user);
            showProgramsView();
        } else {
            isAuthenticated = false;
            currentUser = null;
            updateAuthUI(null);
            showHeroView();
        }
    } catch (error) {
        console.error('Auth check failed:', error);
        isAuthenticated = false;
        currentUser = null;
        updateAuthUI(null);
        showHeroView();
    }
}

// Show hero section (when NOT authenticated)
function showHeroView() {
    document.getElementById('heroSection').classList.add('show');
    document.getElementById('programsSection').classList.remove('show');
}

// Show programs section (when authenticated)
function showProgramsView() {
    document.getElementById('heroSection').classList.remove('show');
    document.getElementById('programsSection').classList.add('show');
}

// Program navigation - works only when authenticated
function navigateToProgram(event, programId) {
    event.preventDefault();
    if (isAuthenticated) {
        window.location.href = `/program/${programId}`;
    } else {
        alert('Please log in to access programs');
        openModal('loginModal');
    }
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    document.body.style.overflow = 'auto';
    const form = document.querySelector(`#${modalId} form`);
    if (form) form.reset();
    clearAlerts();
}

function switchModal(from, to) {
    closeModal(from);
    openModal(to);
}

function showAlert(containerId, message, type = 'error') {
    const container = document.getElementById(containerId);
    const existingAlert = container.querySelector('.alert');
    if (existingAlert) existingAlert.remove();

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    container.appendChild(alert);
}

function clearAlerts() {
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
}

function setButtonLoading(buttonId, loading) {
    const button = document.getElementById(buttonId);
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
    } else {
        button.disabled = false;
        button.classList.remove('loading');
    }
}

// Authentication functions
function updateAuthUI(user) {
    const authButtons = document.getElementById('authButtons');
    const userInfo = document.getElementById('userInfo');
    const userName = document.getElementById('userName');
    const userAvatar = document.getElementById('userAvatar');
    const adminDashboardLink = document.getElementById('adminDashboardLink');

    if (user) {
        authButtons.style.display = 'none';
        userInfo.style.display = 'flex';
        userName.textContent = user.name;
        userAvatar.textContent = user.name.charAt(0).toUpperCase();

        // Show admin dashboard link for admin users
        if (user.role === 'admin') {
            adminDashboardLink.style.display = 'block';
        } else {
            adminDashboardLink.style.display = 'none';
        }

        currentUser = user;
        isAuthenticated = true;
    } else {
        authButtons.style.display = 'flex';
        userInfo.style.display = 'none';
        if (adminDashboardLink) adminDashboardLink.style.display = 'none';
        currentUser = null;
        isAuthenticated = false;
    }
}

// Dropdown functions
function toggleDropdown() {
    const dropdown = document.getElementById('userDropdown');
    const chevron = dropdown.querySelector('.fa-chevron-down');

    dropdown.classList.toggle('active');

    if (dropdown.classList.contains('active')) {
        chevron.style.transform = 'rotate(180deg)';
    } else {
        chevron.style.transform = 'rotate(0deg)';
    }
}

// Close dropdown when clicking outside
document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('userDropdown');
    if (dropdown && !dropdown.contains(event.target)) {
        dropdown.classList.remove('active');
        const chevron = dropdown.querySelector('.fa-chevron-down');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    }
});

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data && method !== 'GET') {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(endpoint, options);
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        return { success: false, message: 'Network error occurred' };
    }
}

// Authentication functions
async function signup(formData) {
    try {
        setButtonLoading('signupBtn', true);

        const response = await apiCall('/api/signup', 'POST', formData);

        if (response.success) {
            showAlert('signupAlert', response.message, 'success');
            updateAuthUI(response.user);
            isAuthenticated = true;
            currentUser = response.user;

            // Close modal and show programs
            setTimeout(() => {
                closeModal('signupModal');
                showProgramsView();
            }, 1500);
        } else {
            showAlert('signupAlert', response.message, 'error');
        }
    } catch (error) {
        showAlert('signupAlert', 'Network error. Please try again.', 'error');
    } finally {
        setButtonLoading('signupBtn', false);
    }
}

async function login(formData) {
    try {
        setButtonLoading('loginBtn', true);

        const response = await apiCall('/api/login', 'POST', formData);

        if (response.success) {
            showAlert('loginAlert', response.message, 'success');
            updateAuthUI(response.user);
            isAuthenticated = true;
            currentUser = response.user;

            // Close modal and show programs
            setTimeout(() => {
                closeModal('loginModal');
                showProgramsView();
            }, 1500);
        } else {
            showAlert('loginAlert', response.message, 'error');
        }
    } catch (error) {
        showAlert('loginAlert', 'Network error. Please try again.', 'error');
    } finally {
        setButtonLoading('loginBtn', false);
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/api/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        if (response.ok) {
            // Update UI immediately
            currentUser = null;
            isAuthenticated = false;
            updateAuthUI(null);
            showHeroView(); // Show hero section after logout

            // Close dropdown if open
            const dropdown = document.getElementById('userDropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
                const chevron = dropdown.querySelector('.fa-chevron-down');
                if (chevron) chevron.style.transform = 'rotate(0deg)';
            }

            // Show success message
            alert('You have been logged out successfully!');
        } else {
            alert('Error logging out. Please try again.');
        }
    } catch (error) {
        console.error('Logout error:', error);
        alert('Network error occurred during logout.');
    }
}

// Profile function
function goToProfile() {
    // Close dropdown
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.remove('active');
        const chevron = dropdown.querySelector('.fa-chevron-down');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    }

    if (currentUser && isAuthenticated) {
        window.location.href = '/dashboard';
    } else {
        alert('Please login first to access your dashboard.');
        openModal('loginModal');
    }
}

function goToAdminDashboard() {
    // Close dropdown
    const dropdown = document.getElementById('userDropdown');
    if (dropdown) {
        dropdown.classList.remove('active');
        const chevron = dropdown.querySelector('.fa-chevron-down');
        if (chevron) chevron.style.transform = 'rotate(0deg)';
    }

    if (currentUser && currentUser.role === 'admin') {
        window.location.href = '/admin/dashboard';
    } else {
        alert('Access denied. Admin privileges required.');
    }
}

// Form submission handlers
document.getElementById('signupForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const location = document.getElementById('location').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Basic validation
    if (!firstName || !lastName || !location || !email || !password || !confirmPassword) {
        showAlert('signupAlert', 'All fields are required', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showAlert('signupAlert', 'Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showAlert('signupAlert', 'Password must be at least 6 characters long', 'error');
        return;
    }

    const formData = {
        first_name: firstName,
        last_name: lastName,
        location: location,
        email: email,
        password: password
    };

    signup(formData);
});

document.getElementById('loginForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('loginAlert', 'Email and password are required', 'error');
        return;
    }

    const formData = { email, password };
    login(formData);
});

// Close modal when clicking outside
window.onclick = function (event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
}

// Timer countdown functionality
function updateTimers() {
    const timers = document.querySelectorAll('.timer');
    timers.forEach(timer => {
        const text = timer.textContent;
        if (text.includes('Time left:')) {
            // Extract time from timer text
            const timeMatch = text.match(/(\d{1,2}):(\d{2}):(\d{2})/);
            if (timeMatch) {
                let hours = parseInt(timeMatch[1]);
                let minutes = parseInt(timeMatch[2]);
                let seconds = parseInt(timeMatch[3]);

                // Countdown logic
                if (seconds > 0) {
                    seconds--;
                } else if (minutes > 0) {
                    minutes--;
                    seconds = 59;
                } else if (hours > 0) {
                    hours--;
                    minutes = 59;
                    seconds = 59;
                }

                // Update timer display
                timer.textContent = `Time left: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

                // Check if timer expired
                if (hours === 0 && minutes === 0 && seconds === 0) {
                    timer.textContent = 'Registration Closed';
                    timer.style.background = '#666666';
                }
            }
        }
    });
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function () {
    console.log('InnoBridge Platform Loaded Successfully!');

    // Check authentication status first
    checkAuthStatus();

    // Start timer countdown
    setInterval(updateTimers, 1000);

    // ESC key to close modals
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape') {
            // Close any open modals
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                if (modal.style.display === 'block') {
                    closeModal(modal.id);
                }
            });
        }
    });

    // Smooth scrolling for navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});
