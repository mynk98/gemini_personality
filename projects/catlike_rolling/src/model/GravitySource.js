import * as THREE from 'three';

export class GravitySource {
    constructor(position = new THREE.Vector3(), strength = 9.82, inverted = false) {
        this.position = position.clone();
        this.strength = strength;
        this.inverted = inverted;
    }

    /**
     * Calculate gravity vector at a given position
     * @param {THREE.Vector3} targetPosition - Position to calculate gravity at
     * @returns {THREE.Vector3} Gravity vector (acceleration)
     */
    getGravity(targetPosition) {
        const direction = new THREE.Vector3()
            .subVectors(this.position, targetPosition)
            .normalize();
        
        const distance = targetPosition.distanceTo(this.position);
        
        // Inverse square law gravity
        const gravityMagnitude = this.strength / (distance * distance);
        
        const gravity = direction.multiplyScalar(gravityMagnitude);
        
        // Invert if this is an inverted gravity source
        if (this.inverted) {
            gravity.negate();
        }
        
        return gravity;
    }

    /**
     * Get 'up' direction for a position relative to this gravity source
     * @param {THREE.Vector3} targetPosition - Position to calculate up direction
     * @returns {THREE.Vector3} Up direction vector
     */
    getUpDirection(targetPosition) {
        const up = new THREE.Vector3()
            .subVectors(targetPosition, this.position)
            .normalize();
        
        if (this.inverted) {
            up.negate();
        }
        
        return up;
    }
}