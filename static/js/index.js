/**
 * INDEX.JS
 * Clean, optimized, modular script for the Alchemy landing page.
 * ZERO UI/UX changes — only improved internal structure & performance.
 *
 * Sections:
 * 1. Navigation + Redirect Handlers
 * 2. Smooth Scrolling
 * 3. Header Scroll Effects
 * 4. Scroll-Based Floating Animations
 * 5. Feature Card Reveal (IntersectionObserver)
 * 6. Button Loading State Animation
 * 7. Keyboard Navigation
 * 8. Prefetch Optimization
 * 9. Error Logging
 */

// ---------------------------
// 1. NAVIGATION & REDIRECTS
// ---------------------------

function redirectToCorporate() {
    window.location.href = "/corporate";
}

function navigateToApp() {
    window.location.href = "/alchemy";
}

// Attach events safely (avoid inline JS)
document.addEventListener("DOMContentLoaded", () => {
    const corpBtn = document.querySelector(".nav-btn.secondary[onclick]");

    if (corpBtn) {
        corpBtn.addEventListener("click", redirectToCorporate);
        corpBtn.removeAttribute("onclick");
    }

    // Feature cards now use their href attributes directly - no override needed
});


// ---------------------------
// 2. SMOOTH SCROLLING
// ---------------------------

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute("href"));
        if (!target) return;

        target.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    });
});


// ---------------------------
// 3. HEADER SCROLL EFFECT
// ---------------------------

const header = document.querySelector(".header");

function handleHeaderScroll() {
    if (!header) return;

    if (window.scrollY > 100) {
        header.style.background = "rgba(255, 255, 255, 0.98)";
        header.style.boxShadow = "0 4px 30px rgba(0, 0, 0, 0.1)";
    } else {
        header.style.background = "rgba(255, 255, 255, 0.95)";
        header.style.boxShadow = "none";
    }
}

window.addEventListener("scroll", handleHeaderScroll);


// ---------------------------
// 4. FLOATING SHAPES — SCROLL SYNC
// ---------------------------

let ticking = false;

function updateFloatingAnimations() {
    const maxScroll =
        document.documentElement.scrollHeight - window.innerHeight;
    const scrollPercent = maxScroll > 0 ? window.scrollY / maxScroll : 0;

    document.querySelectorAll(".floating-shape").forEach((shape, index) => {
        const offset = scrollPercent * 50 * (index + 1);
        shape.style.transform = `translateY(${offset}px) rotate(${offset * 0.5}deg)`;
    });

    ticking = false;
}

window.addEventListener("scroll", () => {
    if (!ticking) {
        requestAnimationFrame(updateFloatingAnimations);
        ticking = true;
    }
});
// ------------------------------------------------
// 5. FEATURE CARD REVEAL ANIMATION (ON SCROLL)
// ------------------------------------------------

// Reusable fade-in observer
const fadeObserver = new IntersectionObserver(
    entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = "1";
                entry.target.style.transform = "translateY(0)";
            }
        });
    },
    {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    }
);

// Initialize card animations on load
document.addEventListener("DOMContentLoaded", () => {
    const cards = document.querySelectorAll(".feature-card");

    cards.forEach((card, index) => {
        card.style.opacity = "0";
        card.style.transform = "translateY(30px)";
        card.style.transition = `all 0.6s ease-out ${index * 0.1}s`;

        fadeObserver.observe(card);
    });
});

// ------------------------------------------------
// 6. BUTTON LOADING SPINNER (ON CLICK)
// ------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".hero-btn, .nav-btn");

    buttons.forEach(btn => {
        btn.addEventListener("click", function (e) {
            // ignore anchor links with # hash navigation
            if (this.href && this.href.includes("#")) return;

            const originalText = this.textContent;
            this.innerHTML = '<span class="loading-spinner"></span>';

            // Restore text after 2 seconds (UX-friendly)
            setTimeout(() => {
                this.textContent = originalText;
            }, 2000);
        });
    });
});

// ------------------------------------------------
// 7. KEYBOARD SHORTCUT SUPPORT
// ------------------------------------------------

document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
        document.querySelectorAll(".modal, .overlay").forEach(el => {
            el.style.display = "none";
        });
    }
});

// ------------------------------------------------
// 8. RESOURCE PREFETCHING
// ------------------------------------------------

(function prefetchResources() {
    const links = ["/alchemy", "/corporate"];

    links.forEach(href => {
        const linkEl = document.createElement("link");
        linkEl.rel = "prefetch";
        linkEl.href = href;
        document.head.appendChild(linkEl);
    });
})();

// ------------------------------------------------
// 9. GLOBAL ERROR HANDLER
// ------------------------------------------------

window.addEventListener("error", e => {
    console.error("🔥 Alchemy Error:", e.error || e.message);
});
// ------------------------------------------------------------
// 10. PERFORMANCE ENHANCEMENTS & SAFETY CHECKS
// ------------------------------------------------------------

// Prevent layout thrashing by batching DOM reads/writes
let animationFrameRequested = false;

function safeUpdateFloatingShapes() {
    if (animationFrameRequested) return;

    animationFrameRequested = true;
    requestAnimationFrame(() => {
        updateFloatingAnimations();
        animationFrameRequested = false;
    });
}

window.addEventListener("scroll", safeUpdateFloatingShapes);

// -------------------------------------------------------------------
// 11. DOM READY FINALIZATION
// -------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Alchemy Landing Page JS Loaded Successfully!");
});

// -------------------------------------------------------------------
// 12. FALLBACK HANDLING FOR OLDER BROWSERS OR JS ERRORS
// -------------------------------------------------------------------

(function fallbackInit() {
    try {
        // Test basic features
        const test = document.querySelector(".hero-title");
        if (!test) throw new Error("Critical element missing");
    } catch (err) {
        console.warn("⚠ Fallback Mode Activated:", err.message);

        // Minimal fallback UI if animations fail
        document.querySelectorAll(".feature-card").forEach(card => {
            card.style.opacity = "1";
            card.style.transform = "none";
        });
    }
})();

// -------------------------------------------------------------------
// 13. CLEAN EXIT
// -------------------------------------------------------------------

console.log("%c✔ index.js fully initialized", "color: #fcb82e; font-weight: bold;");
