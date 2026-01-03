// Show alert function
function showAlert(message, type = 'error') {
    const alert = document.getElementById('loginAlert');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.display = 'block';
}

// Hide alert function
function hideAlert() {
    const alert = document.getElementById('loginAlert');
    alert.style.display = 'none';
}

// Set loading state
function setLoading(loading) {
    const btn = document.getElementById('loginBtn');
    const inputs = document.querySelectorAll('input');

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

// Form submission
document.getElementById('loginForm').addEventListener('submit', async function (e) {
    e.preventDefault();
    hideAlert();

    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    if (!email || !password) {
        showAlert('Please fill in all fields');
        return;
    }

    setLoading(true);

    try {
        const response = await fetch('/api/corporate/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.success) {
            showAlert('Login successful! Redirecting to dashboard...', 'success');
            setTimeout(() => {
                window.location.href = '/corporate/dashboard';
            }, 1500);
        } else {
            showAlert(data.message || 'Login failed');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('Network error. Please try again.');
    } finally {
        setLoading(false);
    }
});

// Clear form validation on input
document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', function () {
        this.classList.remove('error');
        if (document.getElementById('loginAlert').style.display === 'block') {
            hideAlert();
        }
    });
});

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    console.log('Corporate Login Page Loaded');

    // Focus on email field
    const emailInput = document.getElementById('loginEmail');
    if (emailInput) {
        emailInput.focus();
    }
});
