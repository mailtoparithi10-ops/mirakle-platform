/**
 * Particle system for the 3D Globe
 * Adds floating particles around the globe for extra visual appeal
 */

class GlobeParticles {
    constructor(scene, globeRadius) {
        this.scene = scene;
        this.globeRadius = globeRadius;
        this.particles = [];
        this.particleSystem = null;
        
        this.createParticleSystem();
    }
    
    createParticleSystem() {
        const particleCount = 200;
        const particles = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        const sizes = new Float32Array(particleCount);
        
        const color = new THREE.Color();
        
        for (let i = 0; i < particleCount; i++) {
            // Random position around the globe
            const radius = this.globeRadius + 50 + Math.random() * 100;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.random() * Math.PI;
            
            positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i * 3 + 1] = radius * Math.cos(phi);
            positions[i * 3 + 2] = radius * Math.sin(phi) * Math.sin(theta);
            
            // Enhanced golden color variations to match startup theme
            const hue = 0.12 + Math.random() * 0.08; // Golden hue range
            const saturation = 0.7 + Math.random() * 0.3;
            const lightness = 0.4 + Math.random() * 0.4;
            color.setHSL(hue, saturation, lightness);
            colors[i * 3] = color.r;
            colors[i * 3 + 1] = color.g;
            colors[i * 3 + 2] = color.b;
            
            sizes[i] = Math.random() * 3 + 1;
        }
        
        particles.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particles.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        particles.setAttribute('size', new THREE.BufferAttribute(sizes, 1));
        
        const particleMaterial = new THREE.PointsMaterial({
            size: 3,
            transparent: true,
            opacity: 0.8,
            vertexColors: true,
            blending: THREE.AdditiveBlending,
            sizeAttenuation: true,
            map: this.createParticleTexture()
        });
        
        this.particleSystem = new THREE.Points(particles, particleMaterial);
        this.scene.add(this.particleSystem);
    }
    
    createParticleTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 32;
        canvas.height = 32;
        const context = canvas.getContext('2d');
        
        // Create golden glowing dot
        const gradient = context.createRadialGradient(16, 16, 0, 16, 16, 16);
        gradient.addColorStop(0, 'rgba(252, 184, 46, 1)');
        gradient.addColorStop(0.5, 'rgba(252, 184, 46, 0.5)');
        gradient.addColorStop(1, 'rgba(252, 184, 46, 0)');
        
        context.fillStyle = gradient;
        context.fillRect(0, 0, 32, 32);
        
        const texture = new THREE.CanvasTexture(canvas);
        return texture;
    }
    
    animate() {
        if (this.particleSystem) {
            this.particleSystem.rotation.y += 0.001;
            this.particleSystem.rotation.x += 0.0005;
            
            // Animate particle opacity
            const time = Date.now() * 0.001;
            this.particleSystem.material.opacity = 0.4 + 0.2 * Math.sin(time);
        }
    }
}

// Export for use in globe-3d.js
window.GlobeParticles = GlobeParticles;