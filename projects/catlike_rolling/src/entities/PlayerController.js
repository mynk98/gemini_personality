import * as CANNON from 'cannon-es';
import * as THREE from 'three';
import { GravitySystem } from '../physics/GravitySystem.js';

export class PlayerController {
    constructor(physics, scene, radius, position) {
        this.radius = radius;
        this.config = {
            maxSpeed: 12,
            maxAccel: 40, // Increased for power
            maxClimbSpeed: 5,
            maxClimbAccel: 25,
            jumpHeight: 6.0
        };

        this.body = new CANNON.Body({
            mass: 2, // Increased mass to ensure it can push props
            shape: new CANNON.Sphere(radius),
            position: new CANNON.Vec3(position.x, position.y, position.z),
            material: physics.materials.sphere,
            linearDamping: 0.05, // Tiny damping to help stability when pinned
            angularDamping: 0.1
        });
        physics.addBody(this.body);

        const canvas = document.createElement('canvas');
        canvas.width = 256; canvas.height = 256;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#FFD700'; ctx.fillRect(0,0,256,256);
        ctx.fillStyle = '#333333'; ctx.fillRect(0,0,128,128); ctx.fillRect(128,128,128,128); 
        this.mesh = new THREE.Mesh(
            new THREE.SphereGeometry(radius, 32, 32),
            new THREE.MeshStandardMaterial({ map: new THREE.CanvasTexture(canvas), roughness: 0.2, metalness: 0.5 })
        );
        this.mesh.castShadow = true;
        scene.add(this.mesh);

        this.isGrounded = false;
        this.isClimbing = false;
        this.jumpCount = 0;
        this.maxJumps = 4; 
        this.connectionVelocity = new THREE.Vector3();
        this.lastJumpPressed = false;
        this.meshQuaternion = new THREE.Quaternion();
        this.currentUp = new THREE.Vector3(0, 1, 0);
    }

    update(dt, input, camera, contacts) {
        if (dt === 0) return;

        const pos = new THREE.Vector3(this.body.position.x, this.body.position.y, this.body.position.z);
        const up = GravitySystem.getUpVector(pos);
        this.currentUp.lerp(up, 0.1);

        this.processContacts(contacts);

        const camDir = new THREE.Vector3();
        camera.getWorldDirection(camDir);
        const activeNormal = this.isClimbing ? this.climbNormal : this.groundNormal;
        
        const forward = camDir.projectOnPlane(activeNormal).normalize();
        const right = new THREE.Vector3().crossVectors(forward, activeNormal).normalize();

        // --- POWERFUL MOVEMENT LOGIC (Friction Overriding) ---
        const moveDir = new THREE.Vector3();
        if(input.x !== 0 || input.y !== 0) {
            moveDir.add(forward.multiplyScalar(input.y)).add(right.multiplyScalar(input.x));
            if (moveDir.length() > 1) moveDir.normalize();
        }

        const maxS = this.isClimbing ? this.config.maxClimbSpeed : this.config.maxSpeed;
        const maxA = this.isClimbing ? this.config.maxClimbAccel : this.config.maxAccel;

        const currentVel = new THREE.Vector3(this.body.velocity.x, this.body.velocity.y, this.body.velocity.z);
        const targetVel = moveDir.clone().multiplyScalar(maxS).add(this.connectionVelocity);
        
        // Calculate difference only on the tangent plane
        const planarVel = currentVel.clone().projectOnPlane(activeNormal);
        const diff = targetVel.sub(planarVel);
        
        if (diff.length() > 0.01) {
            const accel = maxA * dt;
            if (diff.length() > accel) diff.setLength(accel);
            
            // Apply as a FORCE to ensure we can overcome friction from heavy objects pinning us
            // F = m * a / dt
            const pushForce = new CANNON.Vec3(diff.x * this.body.mass / dt, diff.y * this.body.mass / dt, diff.z * this.body.mass / dt);
            this.body.applyForce(pushForce, this.body.position);
        }

        this.handleJump(input.z > 0, GravitySystem.getGravityAt(pos).length(), activeNormal, currentVel);

        // Visual Sync
        this.mesh.position.copy(pos);
        if (planarVel.length() > 0.01) {
            const axis = new THREE.Vector3().crossVectors(activeNormal, planarVel).normalize();
            this.meshQuaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(axis, (planarVel.length() * dt) / this.radius));
            this.mesh.quaternion.copy(this.meshQuaternion);
        }
    }

    processContacts(contacts) {
        this.isGrounded = false; this.isClimbing = false;
        this.connectionVelocity.set(0, 0, 0);
        const gNorm = new THREE.Vector3(); const cNorm = new THREE.Vector3();
        let gc = 0; let cc = 0;

        for (const contact of contacts) {
            if (contact.bi.id === this.body.id || contact.bj.id === this.body.id) {
                let n = new CANNON.Vec3();
                let other = (contact.bi.id === this.body.id) ? contact.bj : contact.bi;
                if (contact.bi.id === this.body.id) contact.ni.negate(n); else n.copy(contact.ni);
                const nVec = new THREE.Vector3(n.x, n.y, n.z);
                const dot = nVec.dot(this.currentUp);

                if (dot > 0.6) { gNorm.add(nVec); gc++; this.isGrounded = true; 
                    if(other.velocity) this.connectionVelocity.set(other.velocity.x, other.velocity.y, other.velocity.z);
                }
                else if (dot > 0.3) { cNorm.add(nVec); cc++; this.isClimbing = true; }
            }
        }
        this.groundNormal = gc > 0 ? gNorm.normalize() : this.currentUp.clone();
        this.climbNormal = cc > 0 ? cNorm.normalize() : this.currentUp.clone();
        if (this.isGrounded) this.jumpCount = 0;
    }

    handleJump(pressed, gStrength, normal, currentVel) {
        if (pressed && !this.lastJumpPressed) {
            if (this.isGrounded || this.isClimbing || this.jumpCount < this.maxJumps) {
                const jumpV = Math.sqrt(2 * gStrength * this.config.jumpHeight);
                const impulse = new CANNON.Vec3(normal.x * jumpV, normal.y * jumpV, normal.z * jumpV);
                
                // Clear downward momentum for snappy jump
                const verticalComponent = currentVel.dot(normal);
                if (verticalComponent < 0) {
                    this.body.velocity.x -= normal.x * verticalComponent;
                    this.body.velocity.y -= normal.y * verticalComponent;
                    this.body.velocity.z -= normal.z * verticalComponent;
                }
                
                // Use velocity addition for the jump impulse to ensure it's instant
                this.body.velocity.x += impulse.x;
                this.body.velocity.y += impulse.y;
                this.body.velocity.z += impulse.z;
                this.jumpCount++;
            }
        }
        this.lastJumpPressed = pressed;
    }
}
