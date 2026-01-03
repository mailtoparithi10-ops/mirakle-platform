// Modal functions
function openLoginModal() {
    document.getElementById('loginModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    document.getElementById('loginEmail').focus();
}

function closeLoginModal() {
    document.getElementById('loginModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    hideAlert('login');
    document.getElementById('loginForm').reset();
    setLoading(false, 'login');
}

function openSignupModal() {
    document.getElementById('signupModal').style.display = 'block';
    document.body.style.overflow = 'hidden';
    document.getElementById('fullName').focus();
}

function closeSignupModal() {
    document.getElementById('signupModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    hideAlert('signup');
    document.getElementById('signupForm').reset();
    setLoading(false, 'signup');
}

function switchToSignup() {
    closeLoginModal();
    setTimeout(() => openSignupModal(), 100);
}

function switchToLogin() {
    closeSignupModal();
    setTimeout(() => openLoginModal(), 100);
}

// Show alert function
function showAlert(message, type = 'error', modalType = 'login') {
    const alert = document.getElementById(modalType + 'Alert');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.display = 'block';
}

// Hide alert function
function hideAlert(modalType = 'login') {
    const alert = document.getElementById(modalType + 'Alert');
    alert.style.display = 'none';
}

// Set loading state
function setLoading(loading, modalType = 'login') {
    const btn = document.getElementById(modalType + 'Btn');
    const modal = document.getElementById(modalType + 'Modal');
    const inputs = modal.querySelectorAll('input');

    if (loading) {
        btn.disabled = true;
        btn.classList.add('loading');
        inputs.forEach(input => input.disabled = true);
    } else {
        btn.disabled = false;
        btn.classList.remove('loading');
        inputs.forEach(input => input.disabled = false);
    }
}

// Validation functions
function validatePassword(password) {
    if (password.length < 8) {
        return 'Password must be at least 8 characters long';
    }
    if (!/(?=.*[a-z])/.test(password)) {
        return 'Password must contain at least one lowercase letter';
    }
    if (!/(?=.*[A-Z])/.test(password)) {
        return 'Password must contain at least one uppercase letter';
    }
    if (!/(?=.*\d)/.test(password)) {
        return 'Password must contain at least one number';
    }
    return null;
}

function validateEmail(email) {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailPattern.test(email);
}

function validatePhone(phone) {
    const phonePattern = /^[\+]?[1-9][\d]{0,15}$/;
    return phonePattern.test(phone.replace(/[\s\-\(\)]/g, ''));
}

// Login form submission
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    hideAlert('login');

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('Please fill in all required fields', 'error', 'login');
        return;
    }

    if (!validateEmail(email)) {
        showAlert('Please enter a valid corporate email address', 'error', 'login');
        return;
    }

    setLoading(true, 'login');

    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Mock successful login
        showAlert('Authentication successful! Redirecting to dashboard...', 'success', 'login');
        setTimeout(() => {
            window.location.href = '/corporate/dashboard';
        }, 1500);
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Connection error. Please check your network and try again.', 'error', 'login');
    } finally {
        setLoading(false, 'login');
    }
});

// Signup form submission
document.getElementById('signupForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    hideAlert('signup');

    const fullName = document.getElementById('fullName').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const corporateName = document.getElementById('corporateName').value.trim();
    const phoneNumber = document.getElementById('phoneNumber').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validation
    if (!fullName || !email || !corporateName || !phoneNumber || !password || !confirmPassword) {
        showAlert('Please fill in all required fields', 'error', 'signup');
        return;
    }

    if (!validateEmail(email)) {
        showAlert('Please enter a valid corporate email address', 'error', 'signup');
        return;
    }

    if (!validatePhone(phoneNumber)) {
        showAlert('Please enter a valid phone number', 'error', 'signup');
        return;
    }

    const passwordError = validatePassword(password);
    if (passwordError) {
        showAlert(passwordError, 'error', 'signup');
        return;
    }

    if (password !== confirmPassword) {
        showAlert('Passwords do not match', 'error', 'signup');
        return;
    }

    setLoading(true, 'signup');

    try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));

        showAlert('Corporate account created successfully! Welcome to InnoBridge Enterprise!', 'success', 'signup');
        setTimeout(() => {
            window.location.href = '/corporate/dashboard';
        }, 2000);
    } catch (error) {
        console.error('Signup error:', error);
        showAlert('Connection error. Please try again later.', 'error', 'signup');
    } finally {
        setLoading(false, 'signup');
    }
});

// Clear form validation on input
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', function () {
        this.classList.remove('error');
        const modalType = this.closest('#loginModal') ? 'login' : 'signup';
        if (document.getElementById(modalType + 'Alert').style.display === 'block') {
            hideAlert(modalType);
        }
    });
});

// Close modal when clicking outside
window.onclick = function (event) {
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');

    if (event.target === loginModal) {
        closeLoginModal();
    } else if (event.target === signupModal) {
        closeSignupModal();
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
        closeLoginModal();
        closeSignupModal();
    }
});

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

console.log('🏢 InnoBridge Corporate Hub Loaded Successfully!');
