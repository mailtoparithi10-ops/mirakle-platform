// Floating Elements JavaScript - Dynamic Animation System for Alchemy Platform
// Integrated with Startup Culture logic (Parallax, 3D Tilt, Reveal)

class FloatingElementsManager {
    constructor() {
        this.container = null;
        this.elements = [];
        this.isActive = true;
        this.ticking = false;

        this.elementTypes = {
            innovation: [
                { icon: 'fas fa-lightbulb' },
                { icon: 'fas fa-rocket' },
                { icon: 'fas fa-brain' },
                { icon: 'fas fa-seedling' }, // Startup growth
                { icon: 'fas fa-infinity' }  // Scalability
            ],
            business: [
                { icon: 'fas fa-chart-line' },
                { icon: 'fas fa-handshake' },
                { icon: 'fas fa-briefcase' },
                { icon: 'fas fa-user-friends' }, // Connection
                { icon: 'fas fa-globe' }
            ],
            tech: [
                { icon: 'fas fa-code' },
                { icon: 'fas fa-microchip' },
                { icon: 'fas fa-database' },
                { icon: 'fas fa-network-wired' },
                { icon: 'fas fa-cube' } // Blockchain/Structure
            ]
        };

        this.init();
    }

    init() {
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.isActive = false;
            return;
        }

        this.createContainer();
        this.generateInitialElements(15);
        this.setupRevealObserver();
        this.setupTiltEffect();
        this.setupParallax();

        // Spawn more periodically
        setInterval(() => {
            if (this.isActive && this.elements.length < 25) {
                this.addElement();
            }
        }, 3000);

        document.addEventListener('visibilitychange', () => {
            this.isActive = !document.hidden;
        });
    }

    createContainer() {
        this.container = document.querySelector('.floating-elements');
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.className = 'floating-elements';
            document.body.appendChild(this.container);
        }
    }

    generateInitialElements(count) {
        for (let i = 0; i < count; i++) {
            this.addElement(true); // Is initial (spread randomly across vertical)
        }
    }

    getRandomColorClass() {
        const colors = ['color-primary', 'color-secondary', 'color-success', 'color-danger', 'color-info', 'color-purple'];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    getRandomAutoMoveClass() {
        const moves = ['move-auto-1', 'move-auto-2', 'move-auto-3'];
        return moves[Math.floor(Math.random() * moves.length)];
    }

    addElement(isInitial = false) {
        if (!this.container) return;

        const allTypes = [...this.elementTypes.innovation, ...this.elementTypes.business, ...this.elementTypes.tech];
        const type = allTypes[Math.floor(Math.random() * allTypes.length)];

        // Create wrapper for multi-layer animation
        const wrapper = document.createElement('div');
        wrapper.className = 'floating-shape';

        // inner for the autonomous movement
        const inner = document.createElement('div');
        inner.className = `float-icon ${this.getRandomColorClass()} ${this.getRandomAutoMoveClass()}`;

        // Randomly make it a bubble
        if (Math.random() > 0.5) {
            inner.classList.add('float-bubble');
        }

        inner.innerHTML = `<i class="${type.icon}"></i>`;
        wrapper.appendChild(inner);

        // Random Positioning
        const startX = Math.random() * 100;
        const startY = isInitial ? (Math.random() * 100) : 110; // Initial ones spread, new ones from bottom

        wrapper.style.left = `${startX}vw`;
        wrapper.style.top = `${startY}vh`;

        const scale = 0.5 + Math.random() * 0.8;
        wrapper.style.transform = `scale(${scale})`;

        this.container.appendChild(wrapper);
        this.elements.push({ wrapper, speed: 0.1 + Math.random() * 0.4 });

        // Cleanup if not initial (initial ones stay, or use a long timeout)
        if (!isInitial) {
            setTimeout(() => {
                this.removeElement(wrapper);
            }, 60000);
        }
    }

    removeElement(el) {
        if (el && el.parentNode) el.parentNode.removeChild(el);
        this.elements = this.elements.filter(item => item.wrapper !== el);
    }

    // Parallax on Scroll (Subtle)
    setupParallax() {
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            this.elements.forEach(item => {
                const offset = scrollY * item.speed;
                item.wrapper.style.marginTop = `-${offset}px`;
            });
        });
    }

    setupRevealObserver() {
        const fadeObserver = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        fadeObserver.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1, rootMargin: "0px 0px -50px 0px" }
        );

        const selectors = '.feature-card, .product-section, .value-card, .team-card, .hero-content, .hero-visual';
        document.querySelectorAll(selectors).forEach((el, index) => {
            el.classList.add('fade-in-section');
            el.style.transitionDelay = `${(index % 4) * 0.1}s`;
            fadeObserver.observe(el);
        });
    }

    setupTiltEffect() {
        const tiltElements = document.querySelectorAll('.feature-card, .value-card, .team-card, .device-mockup');
        tiltElements.forEach(el => {
            el.classList.add('tilt-element');
            el.addEventListener('mousemove', (e) => {
                const rect = el.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width - 0.5) * 20;
                const y = ((e.clientY - rect.top) / rect.height - 0.5) * -20;
                el.style.transform = `perspective(1000px) rotateX(${y}deg) rotateY(${x}deg) scale3d(1.05, 1.05, 1.05)`;
            });
            el.addEventListener('mouseleave', () => {
                el.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
            });
        });
    }

    destroy() {
        if (this.container) this.container.remove();
        this.isActive = false;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const skipPages = ['dashboard', 'admin', 'meeting'];
    const path = window.location.pathname;
    if (!skipPages.some(p => path.includes(p))) {
        window.floatingElements = new FloatingElementsManager();
    }
});