import * as THREE from 'three';

export class SceneManager {
    constructor(canvas) {
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x111111);
        this.scene.fog = new THREE.Fog(0x111111, 20, 100);

        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 10);
        
        this.renderer = new THREE.WebGLRenderer({ antialias: true, canvas: canvas });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Lighting
        const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 1.5);
        hemiLight.position.set(0, 20, 0);
        this.scene.add(hemiLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 1.5);
        dirLight.position.set(20, 40, 20);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 4096; // Higher res shadows
        dirLight.shadow.mapSize.height = 4096;
        dirLight.shadow.camera.left = -50;
        dirLight.shadow.camera.right = 50;
        dirLight.shadow.camera.top = 50;
        dirLight.shadow.camera.bottom = -50;
        this.scene.add(dirLight);

        // Add a warm point light near the start
        const warmPoint = new THREE.PointLight(0xffaa00, 200, 50);
        warmPoint.position.set(5, 10, 5);
        warmPoint.castShadow = true;
        this.scene.add(warmPoint);

        // Add a cool point light in the distance
        const coolPoint = new THREE.PointLight(0x00aaff, 300, 100);
        coolPoint.position.set(-20, 15, -30);
        coolPoint.castShadow = true;
        this.scene.add(coolPoint);

        // Ground Plane (Physics matches visual)
        const planeGeo = new THREE.PlaneGeometry(100, 100);
        const planeMat = new THREE.MeshStandardMaterial({ 
            color: 0x333333, roughness: 0.8, metalness: 0.2 
        });
        const plane = new THREE.Mesh(planeGeo, planeMat);
        plane.rotation.x = -Math.PI / 2;
        plane.receiveShadow = true;
        this.scene.add(plane);
        
        // Grid Helper
        const grid = new THREE.GridHelper(100, 20, 0x555555, 0x222222);
        this.scene.add(grid);
    }

    resize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    render() {
        this.renderer.render(this.scene, this.camera);
    }
}
