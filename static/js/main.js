// ===============================
// MAIN UI JS FILE
// ===============================

console.log("🚀 main.js loaded");


// Smooth scroll fallback (if browser doesn't support CSS scroll-behavior)
function smoothScrollTo(targetId) {
    const element = document.querySelector(targetId);
    if (element) {
        window.scrollTo({
            top: element.offsetTop - 80,
            behavior: "smooth"
        });
    }
}

// Navbar scroll shrink effect
window.addEventListener("scroll", () => {
    const header = document.querySelector(".header");
    
    // Only apply if header exists (not on admin dashboard)
    if (header) {
        if (window.scrollY > 120) {
            header.classList.add("header-small");
        } else {
            header.classList.remove("header-small");
        }
    }
});


// Button loading animation globally
document.addEventListener("DOMContentLoaded", () => {
    // 1. Loading States
    document.querySelectorAll("a, button").forEach(btn => {
        btn.addEventListener("click", function () {
            if (this.classList.contains("no-load")) return;

            this.classList.add("loading");
            setTimeout(() => {
                this.classList.remove("loading");
            }, 1800);
        });
    });

    // 2. Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector(".mobile-menu-btn");
    const navMenu = document.querySelector(".nav-menu");

    if (mobileMenuBtn && navMenu) {
        mobileMenuBtn.addEventListener("click", () => {
            navMenu.classList.toggle("active");
            // Toggle icon if FontAwesome is present
            const icon = mobileMenuBtn.querySelector("i");
            if (icon) {
                icon.classList.toggle("fa-bars");
                icon.classList.toggle("fa-times");
            }
        });

        // Close menu when clicking a link
        navMenu.querySelectorAll(".nav-link").forEach(link => {
            link.addEventListener("click", () => {
                navMenu.classList.remove("active");
                const icon = mobileMenuBtn.querySelector("i");
                if (icon) {
                    icon.classList.add("fa-bars");
                    icon.classList.remove("fa-times");
                }
            });
        });
    }

    // 3. User Profile Dropdown Toggle
    const userMenuBtn = document.getElementById("userMenuBtn");
    const userMenuContent = document.getElementById("userMenuContent");

    if (userMenuBtn && userMenuContent) {
        userMenuBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            userMenuContent.classList.toggle("active");
        });

        // Close dropdown when clicking outside
        document.addEventListener("click", (e) => {
            if (!userMenuBtn.contains(e.target) && !userMenuContent.contains(e.target)) {
                userMenuContent.classList.remove("active");
            }
        });

        // Close on scroll
        window.addEventListener("scroll", () => {
            userMenuContent.classList.remove("active");
        });
    }
});


// Floating shapes movement based on mouse - Disabled to keep autonomous float consistent
/*
document.addEventListener("mousemove", (e) => {
    document.querySelectorAll(".floating-shape").forEach((shape, i) => {
        const speed = (i + 1) * 0.02;
        const x = e.clientX * speed;
        const y = e.clientY * speed;
        shape.style.transform = `translate(${x}px, ${y}px)`;
    });
});
*/

// ==========================================
// PLATFORM SECURITY & ANTI-SCREENSHOT DETERRENTS
// ==========================================

// 1. Disable Right Click (Context Menu)
document.addEventListener('contextmenu', (e) => {
    e.preventDefault();
}, false);

// 2. Blur Content when focus is lost (Deterrent for Mobile Screen Recording)
const toggleSecurityBlur = (shouldBlur) => {
    const main = document.querySelector('main') || document.body;
    if (shouldBlur) {
        main.classList.add('security-blur');
    } else {
        main.classList.remove('security-blur');
    }
};

window.addEventListener('blur', () => toggleSecurityBlur(true));
window.addEventListener('focus', () => toggleSecurityBlur(false));
document.addEventListener('visibilitychange', () => {
    toggleSecurityBlur(document.hidden);
});

// 3. Disable specific Keyboard Shortcuts (Cmd+S, PrintScreen, etc.)
document.addEventListener('keydown', (e) => {
    // Prevent Save (Ctrl+S / Cmd+S)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
    }

    // Alert on PrintScreen
    if (e.key === 'PrintScreen') {
        navigator.clipboard.writeText(""); // Clear clipboard
        alert('Screenshots are discouraged on Alchemy for data protection.');
    }
});
