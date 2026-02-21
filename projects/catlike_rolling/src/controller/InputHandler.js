import * as THREE from 'three';

export class InputHandler {
    constructor() {
        this.input = new THREE.Vector3(0, 0, 0); // X: Horizontal, Y: Vertical, Z: Jump
        this.keys = {};
        
        window.addEventListener('keydown', (e) => this.keys[e.code] = true);
        window.addEventListener('keyup', (e) => this.keys[e.code] = false);
    }

    update() {
        // Reset
        this.input.set(0, 0, 0);

        // Movement
        if (this.keys['KeyW']) this.input.y += 1;
        if (this.keys['KeyS']) this.input.y -= 1;
        if (this.keys['KeyA']) this.input.x -= 1;
        if (this.keys['KeyD']) this.input.x += 1;
        
        // Jump
        if (this.keys['Space']) this.input.z = 1;

        // Clamp diagonal movement
        if (this.input.length() > 1) {
            this.input.normalize();
        }

        return this.input;
    }
}
