import * as THREE from 'three';
import { PhysicsManager } from './physics/PhysicsManager.js';
import { GravitySystem } from './physics/GravitySystem.js';
import { SceneManager } from './view/SceneManager.js';
import { InputHandler } from './controller/InputHandler.js';
import { CameraController } from './controller/CameraController.js';
import { GameLoop } from './core/GameLoop.js';
import { LevelGenerator } from './model/LevelGenerator.js';
import { PlayerController } from './entities/PlayerController.js';

class CatlikeGame {
    constructor() {
        // 1. Core Services
        this.physics = new PhysicsManager();
        this.input = new InputHandler();
        
        // 2. Visuals
        const canvas = document.createElement('canvas');
        canvas.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; z-index:1;';
        document.body.appendChild(canvas);
        this.graphics = new SceneManager(canvas);
        this.camera = new CameraController(this.graphics.camera, canvas);
        
        // 3. Level Generation
        this.levelBuilder = new LevelGenerator(this.physics, this.graphics.scene);
        
        // 4. State Management
        const params = new URLSearchParams(window.location.search);
        this.currentLevelId = parseInt(params.get('level')) || 6;
        this.loadLevel(this.currentLevelId);
        this.setupUI();

        // 5. Entities
        this.player = new PlayerController(this.physics, this.graphics.scene, 1, new THREE.Vector3(0, 5, 0));
        this.setInitialSpawn();

        // 6. Execution
        this.loop = new GameLoop(this.update.bind(this), this.render.bind(this));
        this.loop.start();

        window.addEventListener('resize', () => this.graphics.resize());
    }

    setInitialSpawn() {
        const spawns = { 4: [0, -15, 0], 5: [0, 22, 0], 6: [-20, 5, 0] };
        if (spawns[this.currentLevelId]) {
            const [x, y, z] = spawns[this.currentLevelId];
            this.player.body.position.set(x, y, z);
        }
    }

    loadLevel(id) {
        GravitySystem.clear();
        if (id === 4) {
            GravitySystem.addSource({ type: 'shell', position: new THREE.Vector3(0,0,0), radius: 25, strength: 30 });
            this.levelBuilder.createHollowSphere(new THREE.Vector3(0,0,0), 25, 20);
            for(let i=0; i<10; i++) this.levelBuilder.createDynamicCube(new THREE.Vector3(Math.random()*10-5, 0, Math.random()*10-5), new THREE.Vector3(2,2,2), 0x00ff00);
        } else if (id === 5) {
            GravitySystem.addSource({ type: 'box', position: new THREE.Vector3(0,0,0), size: new THREE.Vector3(40,40,40), strength: 30 });
            this.levelBuilder.createBoxLevel(new THREE.Vector3(0,0,0), new THREE.Vector3(40,40,40));
            this.levelBuilder.createDynamicCube(new THREE.Vector3(0, 30, 0), new THREE.Vector3(3,3,3), 0x00aaff);
        } else if (id === 6) {
            GravitySystem.addSource({ type: 'standard', strength: 30 });
            this.levelBuilder.createClimbingLevel();
        } else {
            GravitySystem.addSource({ type: 'standard', strength: 30 });
            this.levelBuilder.createStaticBox(new THREE.Vector3(0,-1,0), new THREE.Vector3(100,2,100), 0x333333);
            if (id === 1) this.levelBuilder.createRamp(new THREE.Vector3(0, 2, -10), new THREE.Vector3(10, 1, 20), -Math.PI / 6);
            if (id === 2) this.levelBuilder.createStairs(new THREE.Vector3(-5, 0, -5), 10, 0.5, 1, 4);
            if (id === 3) this.levelBuilder.createMovingPlatform(new THREE.Vector3(10, 2, 0), new THREE.Vector3(10, 1, 10), 15, 3);
        }
    }

    update(dt) {
        // 1. Input state update
        this.input.update();

        // 2. Kinematic state update (Player defines intent)
        // Pass current world contacts to the player for ground detection
        this.player.update(dt, this.input.input, this.graphics.camera, this.physics.world.contacts);

        // 3. Physics step (Apply gravity and resolve collisions)
        this.physics.step(dt);
        this.levelBuilder.update(dt);

        // 4. Controller update (Camera follow)
        this.camera.update(this.player.mesh.position);
    }

    render() {
        this.graphics.render();
    }

    setupUI() {
        const ui = document.createElement('div');
        ui.style.cssText = 'position:absolute; top:10px; left:10px; color:white; font-family:sans-serif; background:rgba(0,0,0,0.5); padding:10px; border-radius:5px; pointer-events:auto; z-index:1000;';
        ui.innerHTML = `
            <h3>Modular Catlike Engine</h3>
            <div style="display:flex; gap:5px; flex-wrap:wrap; max-width:250px;">
                <button onclick="location.search='?level=1'">1</button>
                <button onclick="location.search='?level=2'">2</button>
                <button onclick="location.search='?level=3'">3</button>
                <button onclick="location.search='?level=4'">4</button>
                <button onclick="location.search='?level=5'">5</button>
                <button onclick="location.search='?level=6'">6</button>
            </div>
        `;
        document.body.appendChild(ui);
    }
}

// Start
new CatlikeGame();
