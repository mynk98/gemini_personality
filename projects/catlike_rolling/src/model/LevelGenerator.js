import * as CANNON from 'cannon-es';
import * as THREE from 'three';

export class LevelGenerator {
    constructor(world, scene) {
        this.world = world;
        this.scene = scene;
        this.platforms = [];
        this.gridTexture = this.createGridTexture();
    }

    createGridTexture() {
        const canvas = document.createElement('canvas');
        canvas.width = 128; canvas.height = 128;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#f0f0f0'; ctx.fillRect(0, 0, 128, 128);
        ctx.strokeStyle = '#cccccc'; ctx.lineWidth = 2;
        ctx.strokeRect(0, 0, 128, 128);
        const texture = new THREE.CanvasTexture(canvas);
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.repeat.set(1, 1);
        return texture;
    }

    createStaticBox(position, size, color = 0xeeeeee, rotation = null) {
        const shape = new CANNON.Box(new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2));
        const body = new CANNON.Body({ mass: 0, position: new CANNON.Vec3(position.x, position.y, position.z), shape: shape, material: this.world.materials.ground });
        if (rotation) body.quaternion.copy(rotation);
        this.world.addBody(body);

        const tex = this.gridTexture.clone();
        tex.repeat.set(size.x / 2, size.z / 2);
        const mat = new THREE.MeshStandardMaterial({ map: tex, color: color });
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(size.x, size.y, size.z), mat);
        mesh.position.copy(position);
        if (rotation) mesh.quaternion.copy(rotation);
        mesh.receiveShadow = true;
        mesh.castShadow = true;
        this.scene.add(mesh);
        return { body, mesh };
    }

    createClimbingLevel() {
        // Ground
        this.createStaticBox(new THREE.Vector3(0, -1, 0), new THREE.Vector3(100, 2, 100), 0x99cc99);

        // Tall Wall 1
        this.createStaticBox(new THREE.Vector3(0, 10, -10), new THREE.Vector3(20, 20, 2));
        
        // Corner Wall
        this.createStaticBox(new THREE.Vector3(-10, 10, 0), new THREE.Vector3(2, 20, 20));

        // Arch structure
        this.createStaticBox(new THREE.Vector3(15, 15, 0), new THREE.Vector3(2, 30, 10)); // Pillar
        this.createStaticBox(new THREE.Vector3(25, 15, 0), new THREE.Vector3(2, 30, 10)); // Pillar
        this.createStaticBox(new THREE.Vector3(20, 30, 0), new THREE.Vector3(12, 2, 10)); // Roof

        // Zig-zag platforms (raised)
        this.createStaticBox(new THREE.Vector3(0, 5, 15), new THREE.Vector3(10, 1, 10), 0xffcc99);
        this.createStaticBox(new THREE.Vector3(10, 8, 25), new THREE.Vector3(10, 1, 10), 0xffcc99);
        this.createStaticBox(new THREE.Vector3(0, 11, 35), new THREE.Vector3(10, 1, 10), 0xffcc99);

        // Cylinder-like climbable wall (approximated)
        for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI;
            const x = Math.cos(angle) * 15 + 40;
            const z = Math.sin(angle) * 15 - 20;
            const rot = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 1, 0), -angle + Math.PI/2);
            this.createStaticBox(new THREE.Vector3(x, 10, z), new THREE.Vector3(10, 20, 1), 0xeeeeee, rot);
        }
    }

    createRamp(position, dimensions, rotationZ) {
        const rot = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), rotationZ);
        this.createStaticBox(position, dimensions, 0x555555, rot);
    }

    createStairs(startPos, stepCount, stepHeight, stepDepth, stepWidth) {
        for (let i = 0; i < stepCount; i++) {
            const pos = new THREE.Vector3(startPos.x + (i * stepDepth), startPos.y + (i * stepHeight), startPos.z);
            this.createStaticBox(pos, new THREE.Vector3(stepDepth, stepHeight, stepWidth), 0x666666);
        }
    }

    createMovingPlatform(position, size, range, speed) {
        const body = new CANNON.Body({ type: CANNON.Body.KINEMATIC, position: new CANNON.Vec3(position.x, position.y, position.z), shape: new CANNON.Box(new CANNON.Vec3(size.x/2, size.y/2, size.z/2)) });
        this.world.addBody(body);
        const mesh = new THREE.Mesh(new THREE.BoxGeometry(size.x, size.y, size.z), new THREE.MeshStandardMaterial({ color: 0x0088ff }));
        this.scene.add(mesh);
        this.platforms.push({ body, mesh, origin: position.clone(), range, speed, time: 0 });
    }

    createHollowSphere(center, radius, segments) {
        const shellThickness = 1;
        for (let phi = 0; phi < Math.PI; phi += Math.PI / segments) {
            if (phi < Math.PI / 4) continue; 
            for (let theta = 0; theta < Math.PI * 2; theta += (Math.PI * 2) / (segments * 2)) {
                const x = radius * Math.sin(phi) * Math.cos(theta);
                const y = radius * Math.cos(phi);
                const z = radius * Math.sin(phi) * Math.sin(theta);
                const pos = new THREE.Vector3(x, y, z).add(center);
                const up = new THREE.Vector3(x, y, z).normalize();
                const quat = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), up);
                const size = (2 * Math.PI * radius * Math.sin(phi)) / (segments * 2);
                const height = (Math.PI * radius) / segments;
                const body = new CANNON.Body({ mass: 0, position: new CANNON.Vec3(pos.x, pos.y, pos.z), shape: new CANNON.Box(new CANNON.Vec3(size/2 + 0.1, shellThickness/2, height/2 + 0.1)) });
                body.quaternion.copy(quat);
                this.world.addBody(body);
                const mesh = new THREE.Mesh(new THREE.BoxGeometry(size + 0.2, shellThickness, height + 0.2), new THREE.MeshStandardMaterial({ color: 0x777777, transparent: true, opacity: 0.8 }));
                mesh.position.copy(pos); mesh.quaternion.copy(quat);
                this.scene.add(mesh);
            }
        }
    }

    createBoxLevel(center, size) {
        this.createStaticBox(center, size, 0x44aa44);
    }

    createDynamicCube(position, size, color = 0xffffff) {
        const shape = new CANNON.Box(new CANNON.Vec3(size.x / 2, size.y / 2, size.z / 2));
        const body = new CANNON.Body({
            mass: 1,
            position: new CANNON.Vec3(position.x, position.y, position.z),
            shape: shape,
            material: this.world.materials.sphere,
            linearDamping: 0.5, // Increased from 0.1
            angularDamping: 0.5, // Increased from 0.1
            allowSleep: true,
            sleepSpeedLimit: 0.1,
            sleepTimeLimit: 1
        });
        this.world.addBody(body);

        const geo = new THREE.BoxGeometry(size.x, size.y, size.z);
        const mat = new THREE.MeshStandardMaterial({ color: color });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        this.scene.add(mesh);

        this.platforms.push({
            body: body,
            mesh: mesh,
            isDynamic: true // Tag for the update loop
        });
    }

    update(dt) {
        this.platforms.forEach(p => {
            if (p.isDynamic) {
                p.mesh.position.copy(p.body.position);
                p.mesh.quaternion.copy(p.body.quaternion);
            } else if (p.speed) {
                p.time += dt * p.speed;
                const offset = Math.sin(p.time) * p.range;
                p.body.position.set(p.origin.x + offset, p.origin.y, p.origin.z);
                p.mesh.position.copy(p.body.position);
            }
        });
    }
}
