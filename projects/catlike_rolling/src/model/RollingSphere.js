import * as CANNON from 'cannon-es';
import * as THREE from 'three';
import { CustomGravity } from './CustomGravity.js';

export class RollingSphere {
    constructor(world, scene, radius, position) {
        this.world = world;
        this.radius = radius;
        this.maxSpeed = 10;
        this.maxAcceleration = 30; // Increased for responsiveness
        this.maxClimbSpeed = 4;
        this.maxClimbAcceleration = 20;
        
        this.body = new CANNON.Body({
            mass: 1,
            shape: new CANNON.Sphere(radius),
            position: new CANNON.Vec3(position.x, position.y, position.z),
            material: world.materials.sphere,
            linearDamping: 0.0,
            angularDamping: 0.0
        });
        this.world.addBody(this.body);

        const geometry = new THREE.SphereGeometry(radius, 32, 32);
        const canvas = document.createElement('canvas');
        canvas.width = 256; canvas.height = 256;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#FFD700'; ctx.fillRect(0,0,256,256);
        ctx.fillStyle = '#333333'; ctx.fillRect(0,0,128,128); ctx.fillRect(128,128,128,128); 
        const texture = new THREE.CanvasTexture(canvas);
        this.mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({ map: texture, roughness: 0.2, metalness: 0.5 }));
        this.mesh.castShadow = true;
        if (scene) scene.add(this.mesh);

        this.currentUp = new THREE.Vector3(0, 1, 0);
        this.isGrounded = false;
        this.isClimbing = false;
        this.connectionVelocity = new THREE.Vector3(0, 0, 0);
        this.jumpCount = 0;
        this.maxJumps = 4; 
        this.meshQuaternion = new THREE.Quaternion();
        this.lastJumpPressed = false;
    }

    update(dt, inputVector, camera) {
        if (!this.mesh || !this.body || dt === 0) return;

        const pos = new THREE.Vector3(this.body.position.x, this.body.position.y, this.body.position.z);
        const gravity = CustomGravity.getGravity(pos);
        const up = CustomGravity.getUp(pos);
        this.currentUp.lerp(up, 0.1);

        // 1. Contact Detection
        this.isGrounded = false;
        this.isClimbing = false;
        const avgNormal = new THREE.Vector3();
        let contactCount = 0;
        this.connectionVelocity.set(0, 0, 0);

        if (this.world.world.contacts) {
            for (const contact of this.world.world.contacts) {
                if (contact.bi.id === this.body.id || contact.bj.id === this.body.id) {
                    let n = new CANNON.Vec3();
                    let other = (contact.bi.id === this.body.id) ? contact.bj : contact.bi;
                    if (contact.bi.id === this.body.id) contact.ni.negate(n); else n.copy(contact.ni);
                    const nVec = new THREE.Vector3(n.x, n.y, n.z);
                    
                    const dot = nVec.dot(this.currentUp);
                    if (dot > 0.6) {
                        avgNormal.add(nVec);
                        contactCount++;
                        this.isGrounded = true;
                        if (other.velocity) this.connectionVelocity.set(other.velocity.x, other.velocity.y, other.velocity.z);
                    } else if (dot > 0.3) {
                        avgNormal.add(nVec);
                        contactCount++;
                        this.isClimbing = true;
                    }
                }
            }
        }
        if (this.isGrounded) this.jumpCount = 0;
        if (contactCount > 0) avgNormal.normalize(); else avgNormal.copy(this.currentUp);

        // 3. Movement
        const camForward = new THREE.Vector3();
        camera.getWorldDirection(camForward);
        const forward = camForward.projectOnPlane(avgNormal).normalize();
        const right = new THREE.Vector3().crossVectors(forward, avgNormal).normalize();

        const moveDir = new THREE.Vector3();
        if(inputVector && (inputVector.x !== 0 || inputVector.y !== 0)) {
            moveDir.add(forward.multiplyScalar(inputVector.y)).add(right.multiplyScalar(inputVector.x));
            if (moveDir.length() > 1) moveDir.normalize();
        }

        const maxS = this.isClimbing ? this.maxClimbSpeed : this.maxSpeed;
        const maxA = this.isClimbing ? this.maxClimbAcceleration : this.maxAcceleration;

        // Correct Planar Acceleration:
        // 1. Get current velocity
        const currentVel = new THREE.Vector3(this.body.velocity.x, this.body.velocity.y, this.body.velocity.z);
        // 2. Project current velocity onto movement axes
        const currentX = currentVel.dot(right);
        const currentZ = currentVel.dot(forward);
        
        // 3. Target velocity on movement axes
        const targetX = moveDir.dot(right) * maxS + this.connectionVelocity.dot(right);
        const targetZ = moveDir.dot(forward) * maxS + this.connectionVelocity.dot(forward);
        
        // 4. Calculate change
        const accel = maxA * dt;
        let newX = THREE.MathUtils.lerp(currentX, targetX, accel / Math.max(accel, Math.abs(targetX - currentX)));
        let newZ = THREE.MathUtils.lerp(currentZ, targetZ, accel / Math.max(accel, Math.abs(targetZ - currentZ)));
        
        // 5. Apply back to body (Change = New - Old)
        const diffX = newX - currentX;
        const diffZ = newZ - currentZ;
        
        this.body.velocity.x += right.x * diffX + forward.x * diffZ;
        this.body.velocity.y += right.y * diffX + forward.y * diffZ;
        this.body.velocity.z += right.z * diffX + forward.z * diffZ;

        // 4. JUMP
        const jumpPressed = (inputVector && inputVector.z > 0);
        if (jumpPressed && !this.lastJumpPressed) {
            if (this.isGrounded || this.isClimbing || this.jumpCount < this.maxJumps) {
                // Formula: v = sqrt(2 * g * h). h=6 (3x dia). g=30. v ~ 19.
                const gMag = gravity.length();
                const jumpV = Math.sqrt(2 * gMag * 6.0);
                
                const jumpImpulse = avgNormal.clone().multiplyScalar(jumpV);
                
                // Clear downward velocity for snappy air jump
                const verticalComponent = currentVel.dot(avgNormal);
                if (verticalComponent < 0) {
                    this.body.velocity.x -= avgNormal.x * verticalComponent;
                    this.body.velocity.y -= avgNormal.y * verticalComponent;
                    this.body.velocity.z -= avgNormal.z * verticalComponent;
                }

                this.body.velocity.x += jumpImpulse.x;
                this.body.velocity.y += jumpImpulse.y;
                this.body.velocity.z += jumpImpulse.z;
                this.jumpCount++;
            }
        }
        this.lastJumpPressed = jumpPressed;

        // 5. Visuals
        this.mesh.position.copy(pos);
        const planarVel = currentVel.clone().projectOnPlane(avgNormal);
        const speed = planarVel.length();
        if (speed > 0.01) {
            const axis = new THREE.Vector3().crossVectors(avgNormal, planarVel).normalize();
            this.meshQuaternion.premultiply(new THREE.Quaternion().setFromAxisAngle(axis, (speed * dt) / this.radius));
            this.mesh.quaternion.copy(this.meshQuaternion);
        }
    }
}
