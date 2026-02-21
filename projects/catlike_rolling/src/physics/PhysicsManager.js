import * as CANNON from 'cannon-es';
import * as THREE from 'three';
import { GravitySystem } from './GravitySystem.js';

export class PhysicsManager {
    constructor() {
        this.world = new CANNON.World();
        this.world.gravity.set(0, 0, 0); // Always handled by GravitySystem
        this.world.allowSleep = true;
        this.world.broadphase = new CANNON.NaiveBroadphase();
        this.world.solver.iterations = 15; // Higher precision

        // Modular Materials
        this.materials = {
            ground: new CANNON.Material('ground'),
            sphere: new CANNON.Material('sphere')
        };

        this.setupContactMaterials();
    }

    setupContactMaterials() {
        // Sphere vs Ground
        this.world.addContactMaterial(new CANNON.ContactMaterial(
            this.materials.ground, this.materials.sphere, {
                friction: 1.0, restitution: 0.1, contactEquationStiffness: 1e8
            }
        ));
        // Object vs Object (Sphere/Cubes)
        this.world.addContactMaterial(new CANNON.ContactMaterial(
            this.materials.sphere, this.materials.sphere, {
                friction: 1.0, restitution: 0.1, contactEquationStiffness: 1e8
            }
        ));
    }

    step(dt) {
        // Global Law Application
        for (const body of this.world.bodies) {
            if (body.type === CANNON.Body.DYNAMIC) {
                const pos = new THREE.Vector3(body.position.x, body.position.y, body.position.z);
                const g = GravitySystem.getGravityAt(pos);
                body.force.x += g.x * body.mass;
                body.force.y += g.y * body.mass;
                body.force.z += g.z * body.mass;
            }
        }
        this.world.step(dt);
    }

    addBody(body) {
        this.world.addBody(body);
    }
}
