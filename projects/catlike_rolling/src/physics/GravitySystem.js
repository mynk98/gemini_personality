import * as THREE from 'three';

/**
 * GravitySystem: Handles mathematical calculations for various gravity types.
 * Stateless utility class for modular reuse.
 */
export class GravitySystem {
    static sources = [];

    static addSource(source) {
        this.sources.push(source);
    }

    static clear() {
        this.sources = [];
    }

    /**
     * Calculates the total gravity vector at a specific point in space.
     * @param {THREE.Vector3} position 
     * @returns {THREE.Vector3}
     */
    static getGravityAt(position) {
        const total = new THREE.Vector3(0, 0, 0);
        
        if (this.sources.length === 0) {
            return new THREE.Vector3(0, -30.0, 0); // Default high-G
        }

        for (const source of this.sources) {
            switch(source.type) {
                case 'shell':
                    const sDir = new THREE.Vector3().subVectors(position, source.position);
                    const sDist = sDir.length();
                    if (sDist === 0) continue;
                    const sMult = (sDist < source.radius) ? 1 : -1;
                    total.add(sDir.normalize().multiplyScalar(source.strength * sMult));
                    break;

                case 'box':
                    const localP = new THREE.Vector3().subVectors(position, source.position);
                    const half = source.size.clone().multiplyScalar(0.5);
                    const bVec = new THREE.Vector3(0, 0, 0);
                    
                    // Face Detection
                    if (localP.x > half.x) bVec.x = half.x - localP.x;
                    else if (localP.x < -half.x) bVec.x = -half.x - localP.x;
                    if (localP.y > half.y) bVec.y = half.y - localP.y;
                    else if (localP.y < -half.y) bVec.y = -half.y - localP.y;
                    if (localP.z > half.z) bVec.z = half.z - localP.z;
                    else if (localP.z < -half.z) bVec.z = -half.z - localP.z;

                    if (bVec.lengthSq() === 0) { // Inside
                        const dx = half.x - Math.abs(localP.x);
                        const dy = half.y - Math.abs(localP.y);
                        const dz = half.z - Math.abs(localP.z);
                        if (dx < dy && dx < dz) bVec.x = localP.x > 0 ? dx : -dx;
                        else if (dy < dz) bVec.y = localP.y > 0 ? dy : -dy;
                        else bVec.z = localP.z > 0 ? dz : -dz;
                    }
                    total.add(bVec.normalize().multiplyScalar(source.strength));
                    break;

                case 'standard':
                    total.add(new THREE.Vector3(0, -source.strength, 0));
                    break;
            }
        }
        return total;
    }

    static getUpVector(position) {
        const g = this.getGravityAt(position);
        if (g.length() < 0.001) return new THREE.Vector3(0, 1, 0);
        return g.clone().normalize().negate();
    }
}
