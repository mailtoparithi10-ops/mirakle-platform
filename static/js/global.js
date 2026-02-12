/* ============================================================
   GLOBAL.JS  
   Shared scripts used across all pages
   ============================================================ */

/* -------------------------------
   SMOOTH SCROLL FOR INTERNAL LINKS
---------------------------------- */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (!target) return;

        e.preventDefault();
        target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});

/* -------------------------------
   HEADER SCROLL EFFECT
---------------------------------- */
const header = document.querySelector('.header');
let lastScrollY = window.scrollY;

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;

    if (currentScrollY > 100) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.1)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.boxShadow = 'none';
    }

    lastScrollY = currentScrollY;
});

/* -------------------------------
   BUTTON LOADING SPINNER
---------------------------------- */
document.querySelectorAll('.hero-btn, .nav-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        if (this.href && this.href.includes('#')) return;

        const originalText = this.textContent;
        this.innerHTML = '<span class="loading-spinner"></span>';

        setTimeout(() => {
            this.textContent = originalText;
        }, 2000);
    });
});

/* -------------------------------
   FLOATING SHAPES PARALLAX EFFECT
---------------------------------- */
let ticking = false;

function updateFloatingShapes() {
    const scrollPercent = window.scrollY /
        (document.documentElement.scrollHeight - window.innerHeight);

    document.querySelectorAll('.floating-shape').forEach((shape, index) => {
        const offset = scrollPercent * 50 * (index + 1);
        shape.style.transform = `translateY(${offset}px) rotate(${offset * 0.5}deg)`;
    });

    ticking = false;
}

window.addEventListener('scroll', () => {
    if (!ticking) {
        requestAnimationFrame(updateFloatingShapes);
        ticking = true;
    }
});

/* -------------------------------
   INTERSECTION OBSERVER ANIMATIONS
---------------------------------- */
const inViewOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const inViewObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, inViewOptions);

// Animate feature cards
document.querySelectorAll('.feature-card').forEach((card, index) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(30px)';
    card.style.transition = `all 0.6s ease-out ${index * 0.1}s`;

    inViewObserver.observe(card);
});

/* -------------------------------
   ESC KEY CLOSES MODALS (GLOBAL)
---------------------------------- */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal, .overlay')
            .forEach(el => el.style.display = 'none');
    }
});

/* -------------------------------
   GLOBAL ERROR LOGGER
---------------------------------- */
window.addEventListener('error', function (e) {
    console.error('🌐 Global Error:', e.error);
});

/* -------------------------------
   PREFETCH CRITICAL ROUTES
---------------------------------- */
['/alchemy', '/corporate'].forEach(url => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
});

/* -------------------------------
   GLOBAL REDIRECT HELPERS
---------------------------------- */
function redirectToCorporate() {
    window.location.href = '/corporate';
}

function navigateToApp() {
    window.location.href = '/alchemy';
}

// Export globally
window.redirectToCorporate = redirectToCorporate;
window.navigateToApp = navigateToApp;

console.log("🌐 global.js loaded successfully");
