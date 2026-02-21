import * as THREE from 'three';
import { CustomGravity } from '../model/CustomGravity.js';

export class CameraController {
    constructor(camera, domElement) {
        this.camera = camera;
        this.domElement = domElement;
        
        this.target = new THREE.Vector3();
        this.distance = 15;
        this.minDistance = 5;
        this.maxDistance = 30;
        
        // Local Orbit State (Radians)
        this.orbitAngles = new THREE.Vector2(0, Math.PI / 4); // x: horizontal, y: vertical
        this.gravityUp = new THREE.Vector3(0, 1, 0);
        
        this.isPointerLocked = false;
        this.setupEvents();
    }

    setupEvents() {
        this.domElement.addEventListener('click', () => {
            if (!this.isPointerLocked) this.domElement.requestPointerLock();
        });

        document.addEventListener('pointerlockchange', () => {
            this.isPointerLocked = (document.pointerLockElement === this.domElement);
        });

        document.addEventListener('mousemove', (e) => {
            if (!this.isPointerLocked) return;

            const sensitivity = 0.005;
            this.orbitAngles.x -= e.movementX * sensitivity;
            this.orbitAngles.y -= e.movementY * sensitivity;

            // Clamp vertical pitch relative to local plane
            this.orbitAngles.y = Math.max(0.1, Math.min(Math.PI / 2.1, this.orbitAngles.y));
        });

        window.addEventListener('wheel', (e) => {
            this.distance = Math.max(this.minDistance, Math.min(this.maxDistance, this.distance + e.deltaY * 0.02));
        }, { passive: true });
    }

    update(targetPosition) {
        if (!targetPosition) return;

        // 1. Update Target Follow
        this.target.lerp(targetPosition, 0.1);

        // 2. Resolve Gravity Alignment
        // Lerp the UP vector to handle transitions smoothly
        const targetUp = CustomGravity.getUp(targetPosition);
        this.gravityUp.lerp(targetUp, 0.05);

        // 3. Construct Camera Orientation
        // Create an 'Orbit Frame' based on the current Up
        const orbitRotation = new THREE.Quaternion().setFromAxisAngle(this.gravityUp, this.orbitAngles.x);
        
        // Find a base 'right' and 'forward' vector relative to local up
        let right = new THREE.Vector3(1, 0, 0);
        if (Math.abs(this.gravityUp.dot(right)) > 0.99) right.set(0, 0, 1);
        const forward = new THREE.Vector3().crossVectors(right, this.gravityUp).normalize();
        right.crossVectors(this.gravityUp, forward).normalize();

        // Apply Horizontal Orbit
        forward.applyQuaternion(orbitRotation);
        right.applyQuaternion(orbitRotation);

        // Apply Vertical Pitch
        const pitchQuat = new THREE.Quaternion().setFromAxisAngle(right, this.orbitAngles.y);
        const lookDir = this.gravityUp.clone().applyQuaternion(pitchQuat); // From Up, pitch down towards target
        
        // Final Offset
        const offset = lookDir.clone().normalize().multiplyScalar(this.distance);
        
        this.camera.position.copy(this.target).add(offset);
        this.camera.up.copy(this.gravityUp);
        this.camera.lookAt(this.target);
    }
}
