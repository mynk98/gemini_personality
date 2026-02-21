import * as THREE from 'three';

export class CustomGravity {
    static sources = []; // Array of sources: { type, position, strength, [radius], [size] }

    static registerSource(source) {
        this.sources.push(source);
    }

    static clearSources() {
        this.sources = [];
    }

    static getGravity(position) {
        const totalGravity = new THREE.Vector3(0, 0, 0);
        
        if (this.sources.length === 0) {
            return new THREE.Vector3(0, -30.0, 0); 
        }

        for (const source of this.sources) {
            if (source.type === 'spherical-shell') {
                const dir = new THREE.Vector3().subVectors(position, source.position);
                const dist = dir.length();
                if (dist === 0) continue;
                const multiplier = (dist < source.radius) ? 1 : -1;
                totalGravity.add(dir.normalize().multiplyScalar(source.strength * multiplier));
            } 
            else if (source.type === 'box') {
                // Catlike Coding Box Gravity Logic
                // 1. Position relative to box center
                const localP = new THREE.Vector3().subVectors(position, source.position);
                // 2. Determine if outside faces
                const half = source.size.clone().multiplyScalar(0.5);
                const vector = new THREE.Vector3(0, 0, 0);
                
                if (localP.x > half.x) vector.x = half.x - localP.x;
                else if (localP.x < -half.x) vector.x = -half.x - localP.x;

                if (localP.y > half.y) vector.y = half.y - localP.y;
                else if (localP.y < -half.y) vector.y = -half.y - localP.y;

                if (localP.z > half.z) vector.z = half.z - localP.z;
                else if (localP.z < -half.z) vector.z = -half.z - localP.z;

                // 3. If vector is zero, we are inside. 
                // Catlike usually pulls towards nearest face from inside too.
                if (vector.lengthSq() === 0) {
                    // Inside logic: find nearest face
                    const dx = half.x - Math.abs(localP.x);
                    const dy = half.y - Math.abs(localP.y);
                    const dz = half.z - Math.abs(localP.z);
                    if (dx < dy && dx < dz) vector.x = localP.x > 0 ? dx : -dx;
                    else if (dy < dz) vector.y = localP.y > 0 ? dy : -dy;
                    else vector.z = localP.z > 0 ? dz : -dz;
                }

                totalGravity.add(vector.normalize().multiplyScalar(source.strength));
            }
            else if (source.type === 'standard') {
                totalGravity.add(new THREE.Vector3(0, -source.strength, 0));
            }
        }

        return totalGravity;
    }

    static getUp(position) {
        const g = this.getGravity(position);
        if (g.length() < 0.001) return new THREE.Vector3(0, 1, 0);
        return g.clone().normalize().negate();
    }
}