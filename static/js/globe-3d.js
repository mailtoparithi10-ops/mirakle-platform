/**
 * 3D Globe with World Map and Connection Dots
 * Uses Three.js for 3D rendering
 */

class Globe3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.globe = null;
        this.connections = [];
        this.dots = [];
        this.particles = null;
        this.connectionParticles = [];
        
        // Globe settings
        this.globeRadius = 200;
        this.rotationSpeed = 0.005;
        
        // Generate evenly distributed connection points around the entire globe
        this.connectionPoints = this.generateEvenlyDistributedPoints(80); // 80 dots for good coverage
        
        this.init();
    }
    
    // Generate evenly distributed points around the globe using Fibonacci sphere algorithm
    generateEvenlyDistributedPoints(numPoints) {
        const points = [];
        const goldenRatio = (1 + Math.sqrt(5)) / 2; // Golden ratio for optimal distribution
        
        for (let i = 0; i < numPoints; i++) {
            // Use Fibonacci spiral for even distribution
            const y = 1 - (i / (numPoints - 1)) * 2; // y goes from 1 to -1
            const radius = Math.sqrt(1 - y * y);
            
            const theta = 2 * Math.PI * i / goldenRatio;
            
            const x = Math.cos(theta) * radius;
            const z = Math.sin(theta) * radius;
            
            // Convert to lat/lng
            const lat = Math.asin(y) * (180 / Math.PI);
            const lng = Math.atan2(z, x) * (180 / Math.PI);
            
            points.push({
                name: `Point ${i + 1}`,
                lat: lat,
                lng: lng,
                color: '#fcb82e'
            });
        }
        
        return points;
    }
    
    init() {
        if (!window.THREE) {
            console.warn('Three.js not loaded, falling back to CSS globe');
            this.createCSSGlobe();
            return;
        }
        
        this.createScene();
        this.createGlobe();
        this.createConnectionDots();
        this.createConnectionLines();
        this.createParticles();
        this.createFloatingCards();
        this.animate();
        this.handleResize();
    }
    
    createScene() {
        // Scene
        this.scene = new THREE.Scene();
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            75,
            this.container.clientWidth / this.container.clientHeight,
            0.1,
            1000
        );
        this.camera.position.z = 400;
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ 
            alpha: true, 
            antialias: true 
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setClearColor(0x000000, 0);
        this.container.appendChild(this.renderer.domElement);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(1, 1, 1);
        this.scene.add(directionalLight);
    }
    
    createGlobe() {
        // Globe geometry
        const geometry = new THREE.SphereGeometry(this.globeRadius, 64, 64);
        
        // Load world map texture
        const textureLoader = new THREE.TextureLoader();
        
        // Create a golden gradient material to match startup images
        const material = new THREE.MeshPhongMaterial({
            color: 0x1a4d72, // Deep blue base
            transparent: true,
            opacity: 0.9,
            shininess: 100,
            emissive: 0x0a1a2e, // Dark blue emissive
            emissiveIntensity: 0.2
        });
        
        // Try to load world map texture with golden overlay
        textureLoader.load(
            'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/land_ocean_ice_cloud_2048.jpg',
            (texture) => {
                material.map = texture;
                // Add golden tint to the texture
                material.color.setHex(0x2d5aa0); // Blue-golden mix
                material.needsUpdate = true;
            },
            undefined,
            (error) => {
                console.log('World map texture failed to load, using golden gradient');
                // Fallback to golden gradient
                material.color.setHex(0xfcb82e);
                material.emissive.setHex(0x8b5a00);
            }
        );
        
        this.globe = new THREE.Mesh(geometry, material);
        this.scene.add(this.globe);
        
        // Add golden wireframe overlay to match startup theme
        const wireframeGeometry = new THREE.SphereGeometry(this.globeRadius + 2, 32, 32);
        const wireframeMaterial = new THREE.MeshBasicMaterial({
            color: 0xfcb82e, // Golden color
            wireframe: true,
            transparent: true,
            opacity: 0.15
        });
        const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial);
        this.scene.add(wireframe);
        
        // Add inner glow effect
        const glowGeometry = new THREE.SphereGeometry(this.globeRadius + 5, 32, 32);
        const glowMaterial = new THREE.MeshBasicMaterial({
            color: 0xfcb82e,
            transparent: true,
            opacity: 0.1,
            side: THREE.BackSide
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        this.scene.add(glow);
    }
    
    createConnectionDots() {
        this.connectionPoints.forEach(point => {
            // Main dot with golden color
            const dotGeometry = new THREE.SphereGeometry(4, 16, 16);
            const dotMaterial = new THREE.MeshBasicMaterial({
                color: 0xfcb82e, // Golden color
                transparent: true,
                opacity: 1
            });
            
            const dot = new THREE.Mesh(dotGeometry, dotMaterial);
            
            // Convert lat/lng to 3D coordinates
            const phi = (90 - point.lat) * (Math.PI / 180);
            const theta = (point.lng + 180) * (Math.PI / 180);
            
            dot.position.x = -(this.globeRadius + 8) * Math.sin(phi) * Math.cos(theta);
            dot.position.y = (this.globeRadius + 8) * Math.cos(phi);
            dot.position.z = (this.globeRadius + 8) * Math.sin(phi) * Math.sin(theta);
            
            dot.userData = point;
            this.dots.push(dot);
            this.scene.add(dot);
            
            // Add pulsing glow effect with golden color
            const glowGeometry = new THREE.SphereGeometry(8, 16, 16);
            const glowMaterial = new THREE.MeshBasicMaterial({
                color: 0xfcb82e,
                transparent: true,
                opacity: 0.4
            });
            const glow = new THREE.Mesh(glowGeometry, glowMaterial);
            glow.position.copy(dot.position);
            this.scene.add(glow);
            
            // Add outer ring effect
            const ringGeometry = new THREE.RingGeometry(10, 12, 16);
            const ringMaterial = new THREE.MeshBasicMaterial({
                color: 0xfcb82e,
                transparent: true,
                opacity: 0.3,
                side: THREE.DoubleSide
            });
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            ring.position.copy(dot.position);
            ring.lookAt(0, 0, 0); // Face the center of the globe
            this.scene.add(ring);
        });
    }
    
    createConnectionLines() {
        // Create connections between nearby points for a network effect
        const connections = [];
        
        // Connect each point to its nearest neighbors
        this.connectionPoints.forEach((point, index) => {
            const distances = [];
            
            // Calculate distances to all other points
            this.connectionPoints.forEach((otherPoint, otherIndex) => {
                if (index !== otherIndex) {
                    const distance = this.calculateSphericalDistance(
                        point.lat, point.lng, 
                        otherPoint.lat, otherPoint.lng
                    );
                    distances.push({ index: otherIndex, distance });
                }
            });
            
            // Sort by distance and connect to 3-5 nearest neighbors
            distances.sort((a, b) => a.distance - b.distance);
            const numConnections = Math.min(4, distances.length);
            
            for (let i = 0; i < numConnections; i++) {
                const targetIndex = distances[i].index;
                // Avoid duplicate connections
                if (index < targetIndex) {
                    connections.push([index, targetIndex]);
                }
            }
        });
        
        // Create the connection lines
        connections.forEach(([startIdx, endIdx], connectionIndex) => {
            const start = this.connectionPoints[startIdx];
            const end = this.connectionPoints[endIdx];
            
            const startVec = this.latLngToVector3(start.lat, start.lng, this.globeRadius + 15);
            const endVec = this.latLngToVector3(end.lat, end.lng, this.globeRadius + 15);
            
            // Create curved line for better visibility
            const midPoint = startVec.clone().add(endVec).multiplyScalar(0.5);
            midPoint.normalize().multiplyScalar(this.globeRadius + 40); // Moderate arc height
            
            const curve = new THREE.QuadraticBezierCurve3(startVec, midPoint, endVec);
            const points = curve.getPoints(50);
            
            const lineGeometry = new THREE.BufferGeometry().setFromPoints(points);
            
            // Golden line material
            const lineMaterial = new THREE.LineBasicMaterial({
                color: 0xfcb82e,
                transparent: true,
                opacity: 0.6,
                linewidth: 2
            });
            
            const line = new THREE.Line(lineGeometry, lineMaterial);
            line.userData = { connectionIndex, startPoint: start, endPoint: end };
            this.connections.push(line);
            this.scene.add(line);
            
            // Add animated particles along some connection lines (every 3rd line to avoid clutter)
            if (connectionIndex % 3 === 0) {
                this.createConnectionParticles(curve, connectionIndex);
            }
        });
    }
    
    // Calculate spherical distance between two lat/lng points
    calculateSphericalDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Earth's radius in km
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLng = (lng2 - lng1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                Math.sin(dLng/2) * Math.sin(dLng/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }
    
    createConnectionParticles(curve, connectionIndex) {
        const particleCount = 8;
        const particles = [];
        
        for (let i = 0; i < particleCount; i++) {
            const particleGeometry = new THREE.SphereGeometry(1.5, 8, 8);
            const particleMaterial = new THREE.MeshBasicMaterial({
                color: 0xfcb82e,
                transparent: true,
                opacity: 0.7
            });
            
            const particle = new THREE.Mesh(particleGeometry, particleMaterial);
            particle.userData = {
                curve: curve,
                progress: i / particleCount,
                speed: 0.01 + Math.random() * 0.01,
                connectionIndex: connectionIndex
            };
            
            particles.push(particle);
            this.scene.add(particle);
        }
        
        this.connectionParticles = this.connectionParticles || [];
        this.connectionParticles.push(...particles);
    }
    
    createParticles() {
        if (window.GlobeParticles) {
            this.particles = new GlobeParticles(this.scene, this.globeRadius);
        }
    }
    
    createFloatingCards() {
        // Create HTML floating cards
        const cards = [
            { icon: '🚀', title: '12K+', subtitle: 'Startups', position: { top: '20%', right: '10%' } },
            { icon: '🌍', title: '50+', subtitle: 'Countries', position: { top: '60%', left: '5%' } },
            { icon: '🤝', title: '300+', subtitle: 'Corporates', position: { bottom: '25%', right: '15%' } },
            { icon: '💰', title: '$2.4M', subtitle: 'Funding', position: { top: '40%', left: '15%' } }
        ];
        
        cards.forEach((card, index) => {
            const cardElement = document.createElement('div');
            cardElement.className = 'globe-floating-card';
            cardElement.style.animationDelay = `${index * 0.5}s`;
            
            Object.keys(card.position).forEach(key => {
                cardElement.style[key] = card.position[key];
            });
            
            cardElement.innerHTML = `
                <div class="card-icon">${card.icon}</div>
                <div class="card-title">${card.title}</div>
                <div class="card-subtitle">${card.subtitle}</div>
            `;
            
            this.container.appendChild(cardElement);
        });
    }
    
    createCSSGlobe() {
        // Fallback CSS-only globe with evenly distributed dots
        let dotsHTML = '';
        
        // Generate evenly distributed dots for CSS fallback
        const numDots = 60; // Fewer dots for CSS version to avoid clutter
        const goldenRatio = (1 + Math.sqrt(5)) / 2;
        
        for (let i = 0; i < numDots; i++) {
            const y = 1 - (i / (numDots - 1)) * 2;
            const radius = Math.sqrt(1 - y * y);
            const theta = 2 * Math.PI * i / goldenRatio;
            
            // Convert to screen coordinates (approximate projection)
            const x = Math.cos(theta) * radius;
            const z = Math.sin(theta) * radius;
            
            // Project to 2D screen coordinates
            const screenX = (x * 0.4 + 0.5) * 100; // Convert to percentage
            const screenY = (-y * 0.4 + 0.5) * 100; // Convert to percentage, flip Y
            
            // Only show dots that would be visible on the front hemisphere
            if (z >= -0.3) { // Show dots slightly around the edges
                const opacity = Math.max(0.3, (z + 0.3) / 1.3); // Fade dots at edges
                dotsHTML += `<div class="globe-connection-dot" style="top: ${screenY}%; left: ${screenX}%; opacity: ${opacity};"></div>`;
            }
        }
        
        // Generate some connection lines between visible dots
        let linesHTML = '';
        for (let i = 0; i < 20; i++) {
            const startX = 20 + Math.random() * 60;
            const startY = 20 + Math.random() * 60;
            const length = 10 + Math.random() * 25;
            const angle = Math.random() * 360;
            
            linesHTML += `<div class="globe-connection-line" style="top: ${startY}%; left: ${startX}%; width: ${length}%; transform: rotate(${angle}deg);"></div>`;
        }
        
        this.container.innerHTML = `
            <div class="globe-3d-canvas">
                <div class="globe-orbital-ring ring-1"></div>
                <div class="globe-orbital-ring ring-2"></div>
                <div class="globe-orbital-ring ring-3"></div>
                
                ${dotsHTML}
                ${linesHTML}
            </div>
        `;
        
        this.createFloatingCards();
    }
    
    latLngToVector3(lat, lng, radius) {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lng + 180) * (Math.PI / 180);
        
        return new THREE.Vector3(
            -radius * Math.sin(phi) * Math.cos(theta),
            radius * Math.cos(phi),
            radius * Math.sin(phi) * Math.sin(theta)
        );
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        if (this.globe) {
            this.globe.rotation.y += this.rotationSpeed;
        }
        
        // Animate connection dots
        this.dots.forEach((dot, index) => {
            const time = Date.now() * 0.001;
            dot.material.opacity = 0.7 + 0.3 * Math.sin(time * 2 + index);
        });
        
        // Animate connection lines with golden glow
        this.connections.forEach((line, index) => {
            const time = Date.now() * 0.001;
            line.material.opacity = 0.6 + 0.4 * Math.sin(time * 2 + index * 0.8);
        });
        
        // Animate connection particles flowing along lines
        if (this.connectionParticles) {
            this.connectionParticles.forEach(particle => {
                particle.userData.progress += particle.userData.speed;
                if (particle.userData.progress > 1) {
                    particle.userData.progress = 0;
                }
                
                const point = particle.userData.curve.getPoint(particle.userData.progress);
                particle.position.copy(point);
                
                // Fade in/out effect
                const fadeDistance = 0.1;
                if (particle.userData.progress < fadeDistance) {
                    particle.material.opacity = particle.userData.progress / fadeDistance * 0.7;
                } else if (particle.userData.progress > 1 - fadeDistance) {
                    particle.material.opacity = (1 - particle.userData.progress) / fadeDistance * 0.7;
                } else {
                    particle.material.opacity = 0.7;
                }
            });
        }
        
        // Animate particles
        if (this.particles) {
            this.particles.animate();
        }
        
        if (this.renderer) {
            this.renderer.render(this.scene, this.camera);
        }
    }
    
    handleResize() {
        window.addEventListener('resize', () => {
            if (!this.camera || !this.renderer) return;
            
            this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        });
    }
}

// Initialize globe when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Load Three.js dynamically
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js';
    script.onload = function() {
        // Initialize globe after Three.js loads
        setTimeout(() => {
            const globeContainer = document.getElementById('globe-3d-container');
            if (globeContainer) {
                new Globe3D('globe-3d-container');
            }
        }, 100);
    };
    script.onerror = function() {
        console.warn('Three.js failed to load, using CSS fallback');
        const globeContainer = document.getElementById('globe-3d-container');
        if (globeContainer) {
            new Globe3D('globe-3d-container');
        }
    };
    document.head.appendChild(script);
});