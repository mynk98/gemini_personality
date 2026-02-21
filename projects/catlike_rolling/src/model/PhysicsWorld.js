import * as CANNON from 'cannon-es';
import { CustomGravity } from './CustomGravity.js';
import * as THREE from 'three';

export class PhysicsWorld {
    constructor() {
        this.world = new CANNON.World({
            gravity: new CANNON.Vec3(0, 0, 0),
        });
        
        this.world.allowSleep = true;
        this.world.broadphase = new CANNON.NaiveBroadphase();
        this.world.solver.iterations = 10;
        
        const groundMat = new CANNON.Material();
        const sphereMat = new CANNON.Material();
        
        const contactMat = new CANNON.ContactMaterial(groundMat, sphereMat, {
            friction: 1.0,
            restitution: 0.1,
            contactEquationStiffness: 1e8,
            contactEquationRelaxation: 3
        });
        this.world.addContactMaterial(contactMat);

        const objectContactMat = new CANNON.ContactMaterial(sphereMat, sphereMat, {
            friction: 1.0,
            restitution: 0.1,
            contactEquationStiffness: 1e8,
            contactEquationRelaxation: 3
        });
        this.world.addContactMaterial(objectContactMat);

        this.materials = { ground: groundMat, sphere: sphereMat };
    }

    addBody(body) {
        this.world.addBody(body);
    }

    step(dt) {
        // ALWAYS apply gravity to all dynamic bodies
        // This ensures they stay pinned to surfaces correctly
        for (const body of this.world.bodies) {
            if (body.type === CANNON.Body.DYNAMIC) {
                const pos = new THREE.Vector3(body.position.x, body.position.y, body.position.z);
                const gravity = CustomGravity.getGravity(pos);
                
                // Direct force vector addition at center of mass
                body.force.x += gravity.x * body.mass;
                body.force.y += gravity.y * body.mass;
                body.force.z += gravity.z * body.mass;
            }
        }
        this.world.step(dt);
    }
}
