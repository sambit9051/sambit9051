/**
 * 3D Viewer Module
 * Handles Three.js visualization
 */

class Viewer3D {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas not found');
            return;
        }

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.mesh = null;
        this.grid = null;
        this.axes = null;
        this.wireframeMode = false;

        this.init();
    }

    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x1a1a2e);

        // Create camera
        const aspect = this.canvas.clientWidth / this.canvas.clientHeight;
        this.camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 10000);
        this.camera.position.set(200, 200, 200);
        this.camera.lookAt(0, 0, 0);

        // Create renderer
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(this.canvas.clientWidth, this.canvas.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);

        // Add orbit controls
        this.controls = new THREE.OrbitControls(this.camera, this.canvas);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.rotateSpeed = 0.5;

        // Add lights
        this.addLights();

        // Add grid and axes
        this.grid = new THREE.GridHelper(1000, 20, 0x444444, 0x222222);
        this.scene.add(this.grid);

        this.axes = new THREE.AxesHelper(100);
        this.scene.add(this.axes);

        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());

        // Start animation loop
        this.animate();
    }

    addLights() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        // Directional lights
        const light1 = new THREE.DirectionalLight(0xffffff, 0.8);
        light1.position.set(100, 200, 100);
        this.scene.add(light1);

        const light2 = new THREE.DirectionalLight(0xffffff, 0.4);
        light2.position.set(-100, 200, -100);
        this.scene.add(light2);

        // Point light for highlights
        const pointLight = new THREE.PointLight(0xffffff, 0.5, 1000);
        pointLight.position.set(0, 300, 0);
        this.scene.add(pointLight);
    }

    loadModel(modelData) {
        // Remove existing mesh
        if (this.mesh) {
            this.scene.remove(this.mesh);
            this.mesh.geometry.dispose();
            this.mesh.material.dispose();
        }

        try {
            const vertices = modelData.vertices;
            const faces = modelData.faces;

            if (!vertices || !faces || vertices.length === 0 || faces.length === 0) {
                throw new Error('Invalid model data');
            }

            // Create geometry
            const geometry = new THREE.BufferGeometry();

            // Convert vertices to Float32Array
            const positions = new Float32Array(vertices.flat());
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

            // Convert faces to indices
            const indices = new Uint32Array(faces.flat());
            geometry.setIndex(new THREE.BufferAttribute(indices, 1));

            // Compute normals for lighting
            geometry.computeVertexNormals();

            // Create material
            const material = new THREE.MeshPhongMaterial({
                color: 0x2563eb,
                specular: 0x111111,
                shininess: 30,
                flatShading: false,
                side: THREE.DoubleSide
            });

            // Create mesh
            this.mesh = new THREE.Mesh(geometry, material);
            this.scene.add(this.mesh);

            // Add wireframe (initially hidden)
            const wireframeGeometry = new THREE.WireframeGeometry(geometry);
            const wireframeMaterial = new THREE.LineBasicMaterial({
                color: 0xffffff,
                opacity: 0.3,
                transparent: true
            });
            this.wireframe = new THREE.LineSegments(wireframeGeometry, wireframeMaterial);
            this.wireframe.visible = false;
            this.scene.add(this.wireframe);

            // Center camera on model
            this.fitCameraToModel();

            console.log(`Model loaded: ${vertices.length} vertices, ${faces.length} faces`);

        } catch (error) {
            console.error('Failed to load model:', error);
            throw error;
        }
    }

    fitCameraToModel() {
        if (!this.mesh) return;

        // Compute bounding box
        const box = new THREE.Box3().setFromObject(this.mesh);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());

        // Calculate camera distance
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = this.camera.fov * (Math.PI / 180);
        let cameraDistance = Math.abs(maxDim / 2 / Math.tan(fov / 2));
        cameraDistance *= 1.5; // Add some margin

        // Position camera
        const direction = this.camera.position.clone().sub(center).normalize();
        this.camera.position.copy(direction.multiplyScalar(cameraDistance).add(center));
        this.camera.lookAt(center);

        // Update controls target
        this.controls.target.copy(center);
        this.controls.update();
    }

    resetCamera() {
        if (this.mesh) {
            this.fitCameraToModel();
        } else {
            this.camera.position.set(200, 200, 200);
            this.camera.lookAt(0, 0, 0);
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
    }

    toggleWireframe() {
        this.wireframeMode = !this.wireframeMode;

        if (this.mesh) {
            if (this.wireframeMode) {
                this.mesh.material.wireframe = true;
                if (this.wireframe) this.wireframe.visible = false;
            } else {
                this.mesh.material.wireframe = false;
                if (this.wireframe) this.wireframe.visible = false;
            }
        }
    }

    toggleGrid() {
        if (this.grid) {
            this.grid.visible = !this.grid.visible;
        }
        if (this.axes) {
            this.axes.visible = !this.axes.visible;
        }
    }

    onWindowResize() {
        if (!this.canvas || !this.camera || !this.renderer) return;

        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;

        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();

        this.renderer.setSize(width, height);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        if (this.controls) {
            this.controls.update();
        }

        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
    }

    dispose() {
        if (this.mesh) {
            this.scene.remove(this.mesh);
            this.mesh.geometry.dispose();
            this.mesh.material.dispose();
        }

        if (this.renderer) {
            this.renderer.dispose();
        }

        window.removeEventListener('resize', () => this.onWindowResize());
    }
}

// Export for global use
window.Viewer3D = Viewer3D;
