// Floating Elements JavaScript - Dynamic Animation System for InnoBridge Platform

class FloatingElementsManager {
    constructor() {
        this.container = null;
        this.elements = [];
        this.isActive = true;
        this.elementTypes = {
            innovation: [
                { icon: 'fas fa-lightbulb', class: 'float-lightbulb' },
                { icon: 'fas fa-rocket', class: 'float-rocket' },
                { icon: 'fas fa-cog', class: 'float-gear' },
                { icon: 'fas fa-atom', class: 'float-network' }
            ],
            business: [
                { icon: 'fas fa-chart-line', class: 'float-chart' },
                { icon: 'fas fa-coins', class: 'float-coin' },
                { icon: 'fas fa-handshake', class: 'float-network' },
                { icon: 'fas fa-trophy', class: 'float-bounce' }
            ],
            tech: [
                { icon: 'fas fa-code', class: 'float-code' },
                { icon: 'fas fa-microchip', class: 'float-gear' },
                { icon: 'fas fa-wifi', class: 'float-network' },
                { icon: 'fas fa-database', class: 'float-up' }
            ],
            shapes: [
                { type: 'circle', class: 'float-circle' },
                { type: 'triangle', class: 'float-triangle' },
                { type: 'square', class: 'float-square' },
                { type: 'line', class: 'float-connection' }
            ]
        };
        
        this.init();
    }

    init() {
        // Check if user prefers reduced motion
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.isActive = false;
            return;
        }

        this.createContainer();
        this.startAnimation();
        
        // Pause animations when page is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAnimations();
            } else {
                this.resumeAnimations();
            }
        });
    }

    createContainer() {
        this.container = document.createElement('div');
        this.container.className = 'floating-elements';
        document.body.appendChild(this.container);
    }

    getPageTheme() {
        const path = window.location.pathname;
        
        // Determine theme based on page
        if (path.includes('startup') || path.includes('rocket') || path === '/') {
            return 'innovation';
        } else if (path.includes('corporate') || path.includes('investor')) {
            return 'business';
        } else if (path.includes('product') || path.includes('about')) {
            return 'tech';
        } else {
            return 'mixed'; // Use all types
        }
    }

    getElementsForTheme(theme) {
        if (theme === 'mixed') {
            return [
                ...this.elementTypes.innovation,
                ...this.elementTypes.business,
                ...this.elementTypes.tech,
                ...this.elementTypes.shapes
            ];
        }
        
        return [
            ...this.elementTypes[theme],
            ...this.elementTypes.shapes
        ];
    }

    createElement(type) {
        const element = document.createElement('div');
        element.className = `floating-element ${type.class}`;
        
        if (type.icon) {
            element.innerHTML = `<i class="${type.icon}"></i>`;
        } else if (type.type === 'line') {
            element.className += ' float-connection';
        }
        
        // Random starting position
        const startX = Math.random() * window.innerWidth;
        const delay = Math.random() * 10; // Random delay up to 10 seconds
        
        element.style.left = startX + 'px';
        element.style.animationDelay = delay + 's';
        
        return element;
    }

    addElement() {
        if (!this.isActive || !this.container) return;
        
        const theme = this.getPageTheme();
        const availableTypes = this.getElementsForTheme(theme);
        const randomType = availableTypes[Math.floor(Math.random() * availableTypes.length)];
        
        const element = this.createElement(randomType);
        this.container.appendChild(element);
        this.elements.push(element);
        
        // Remove element after animation completes
        const animationDuration = this.getAnimationDuration(randomType.class);
        setTimeout(() => {
            this.removeElement(element);
        }, animationDuration * 1000);
    }

    removeElement(element) {
        if (element && element.parentNode) {
            element.parentNode.removeChild(element);
            this.elements = this.elements.filter(el => el !== element);
        }
    }

    getAnimationDuration(className) {
        // Return animation duration in seconds based on class
        const durations = {
            'float-up': 12,
            'float-diagonal': 15,
            'float-wave': 18,
            'float-circle': 25,
            'float-zigzag': 14,
            'float-bounce': 16,
            'rotate-float': 20,
            'float-line': 22
        };
        
        for (const [key, duration] of Object.entries(durations)) {
            if (className.includes(key)) {
                return duration;
            }
        }
        
        return 15; // Default duration
    }

    startAnimation() {
        if (!this.isActive) return;
        
        // Add initial elements
        for (let i = 0; i < 3; i++) {
            setTimeout(() => this.addElement(), i * 2000);
        }
        
        // Continue adding elements periodically
        this.intervalId = setInterval(() => {
            if (this.elements.length < 8) { // Limit max elements
                this.addElement();
            }
        }, 3000 + Math.random() * 4000); // Random interval 3-7 seconds
    }

    pauseAnimations() {
        this.elements.forEach(element => {
            element.style.animationPlayState = 'paused';
        });
    }

    resumeAnimations() {
        this.elements.forEach(element => {
            element.style.animationPlayState = 'running';
        });
    }

    destroy() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
        }
        
        if (this.container) {
            this.container.remove();
        }
        
        this.elements = [];
        this.isActive = false;
    }
}

// Initialize floating elements when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on non-dashboard pages
    const isDashboard = window.location.pathname.includes('dashboard') || 
                       window.location.pathname.includes('admin') ||
                       window.location.pathname.includes('meeting');
    
    if (!isDashboard) {
        window.floatingElements = new FloatingElementsManager();
    }
});

// Clean up when page unloads
window.addEventListener('beforeunload', function() {
    if (window.floatingElements) {
        window.floatingElements.destroy();
    }
});