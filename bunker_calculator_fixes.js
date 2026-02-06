/**
 * CRITICAL FIXES FOR BUNKER DESIGN CALCULATOR
 * File: bunker_calculator_fixes.js
 *
 * Apply these fixes to the main HTML file
 */

// ============================================================================
// FIX 1: Corrected 3D Model Creation with Proper Units
// ============================================================================

function create3DModelCorrected(inp, geom, hopperGeom) {
    const container = document.getElementById('canvas3d');

    // Setup scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);

    // Camera with better positioning
    const maxDim = Math.max(geom.L, geom.W, geom.H_total);
    camera = new THREE.PerspectiveCamera(60, container.clientWidth / 650, 0.1, maxDim * 10);
    camera.position.set(maxDim * 1.5, geom.H_total * 0.8, maxDim * 1.5);
    camera.lookAt(0, geom.H_total / 2, 0);

    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, 650);
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0x606060, 1);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(10, 20, 10);
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-10, 10, -10);
    scene.add(directionalLight2);

    // Create bunker group
    bunkerGroup = new THREE.Group();

    // Materials
    const wallMaterial = new THREE.MeshPhongMaterial({
        color: 0x4a90e2,
        transparent: true,
        opacity: 0.6,
        side: THREE.DoubleSide
    });

    const girderMaterial = new THREE.MeshPhongMaterial({
        color: 0x2c3e50,
        shininess: 30
    });

    const hopperMaterial = new THREE.MeshPhongMaterial({
        color: 0xe74c3c,
        transparent: true,
        opacity: 0.7,
        side: THREE.DoubleSide
    });

    const stiffenerMaterial = new THREE.MeshPhongMaterial({
        color: 0x34495e,
        shininess: 20
    });

    // ========================================================================
    // CORRECTED: Create vertical walls as individual panels
    // ========================================================================
    const wallThickness = inp.t_plate_vert / 1000; // Convert mm to m

    // Front wall (-Y direction)
    const frontWall = new THREE.BoxGeometry(inp.L, inp.h1, wallThickness);
    const frontMesh = new THREE.Mesh(frontWall, wallMaterial);
    frontMesh.position.set(0, inp.h1 / 2, -inp.W / 2);
    bunkerGroup.add(frontMesh);

    // Back wall (+Y direction)
    const backWall = new THREE.BoxGeometry(inp.L, inp.h1, wallThickness);
    const backMesh = new THREE.Mesh(backWall, wallMaterial);
    backMesh.position.set(0, inp.h1 / 2, inp.W / 2);
    bunkerGroup.add(backMesh);

    // Left wall (-X direction)
    const leftWall = new THREE.BoxGeometry(wallThickness, inp.h1, inp.W);
    const leftMesh = new THREE.Mesh(leftWall, wallMaterial);
    leftMesh.position.set(-inp.L / 2, inp.h1 / 2, 0);
    bunkerGroup.add(leftMesh);

    // Right wall (+X direction)
    const rightWall = new THREE.BoxGeometry(wallThickness, inp.h1, inp.W);
    const rightMesh = new THREE.Mesh(rightWall, wallMaterial);
    rightMesh.position.set(inp.L / 2, inp.h1 / 2, 0);
    bunkerGroup.add(rightMesh);

    // ========================================================================
    // CORRECTED: Create vertical girders with proper dimensions
    // ========================================================================
    const girderDepth = inp.girder_depth / 1000; // Convert mm to m
    const girderWidth = inp.top_flange_width / 1000;
    const girderHeight = geom.H_total;

    // Corner girders
    const corners = [
        { x: -inp.L/2, z: -inp.W/2 },
        { x:  inp.L/2, z: -inp.W/2 },
        { x:  inp.L/2, z:  inp.W/2 },
        { x: -inp.L/2, z:  inp.W/2 }
    ];

    corners.forEach((corner, i) => {
        const girderGeom = new THREE.BoxGeometry(girderWidth, girderHeight, girderDepth);
        const girder = new THREE.Mesh(girderGeom, girderMaterial);
        girder.position.set(corner.x, girderHeight / 2, corner.z);
        bunkerGroup.add(girder);
    });

    // ========================================================================
    // CORRECTED: Create eccentric pyramidal hopper
    // ========================================================================
    const hopperGeometry = createEccentricHopperGeometry(
        hopperGeom.corners_top,
        hopperGeom.corners_bottom,
        inp.h2
    );

    const hopperMesh = new THREE.Mesh(hopperGeometry, hopperMaterial);
    hopperMesh.position.set(0, 0, 0); // Position at bottom of vertical walls
    bunkerGroup.add(hopperMesh);

    // ========================================================================
    // Add horizontal stiffeners
    // ========================================================================
    const numHorizontalRings = Math.floor(inp.h1 / (inp.h_spacing / 1000));
    const stiffenerSize = 0.05; // 50mm approximation

    for (let i = 1; i <= numHorizontalRings; i++) {
        const y = (inp.h_spacing / 1000) * i;

        // Create ring segments
        const ringGeom = new THREE.TorusGeometry(
            Math.sqrt(Math.pow(inp.L/2, 2) + Math.pow(inp.W/2, 2)),
            stiffenerSize,
            8,
            4
        );
        const ring = new THREE.Mesh(ringGeom, stiffenerMaterial);
        ring.position.set(0, y, 0);
        ring.rotation.x = Math.PI / 2;
        bunkerGroup.add(ring);
    }

    // ========================================================================
    // Add coordinate axes helper
    // ========================================================================
    const axesHelper = new THREE.AxesHelper(maxDim);
    bunkerGroup.add(axesHelper);

    // Add grid
    const gridHelper = new THREE.GridHelper(maxDim * 2, 20);
    gridHelper.position.y = -inp.h2;
    scene.add(gridHelper);

    scene.add(bunkerGroup);

    // ========================================================================
    // IMPROVED: Mouse controls with zoom
    // ========================================================================
    let mouseDown = false;
    let previousMousePosition = { x: 0, y: 0 };

    container.addEventListener('mousedown', (e) => {
        mouseDown = true;
        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    container.addEventListener('mouseup', () => {
        mouseDown = false;
    });

    container.addEventListener('mousemove', (e) => {
        if (!mouseDown) return;

        const deltaMove = {
            x: e.clientX - previousMousePosition.x,
            y: e.clientY - previousMousePosition.y
        };

        bunkerGroup.rotation.y += deltaMove.x * 0.01;
        bunkerGroup.rotation.x += deltaMove.y * 0.01;

        previousMousePosition = { x: e.clientX, y: e.clientY };
    });

    // Zoom with mouse wheel
    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY * 0.01;
        camera.position.multiplyScalar(1 + delta * 0.05);
    });

    // Render loop
    function animate() {
        requestAnimationFrame(animate);
        renderer.render(scene, camera);
    }
    animate();
}

// ============================================================================
// FIX 2: Create Eccentric Hopper Geometry (NEW FUNCTION)
// ============================================================================

function createEccentricHopperGeometry(corners_top, corners_bottom, height) {
    const geometry = new THREE.BufferGeometry();

    // Define vertices
    const vertices = new Float32Array([
        // Bottom vertices (0-3) - at bottom opening
        corners_bottom.c1.x, -height, corners_bottom.c1.y,
        corners_bottom.c2.x, -height, corners_bottom.c2.y,
        corners_bottom.c3.x, -height, corners_bottom.c3.y,
        corners_bottom.c4.x, -height, corners_bottom.c4.y,

        // Top vertices (4-7) - at junction with vertical walls
        corners_top.c1.x, 0, corners_top.c1.y,
        corners_top.c2.x, 0, corners_top.c2.y,
        corners_top.c3.x, 0, corners_top.c3.y,
        corners_top.c4.x, 0, corners_top.c4.y
    ]);

    // Define faces (each face is split into 2 triangles)
    const indices = new Uint16Array([
        // Face 1 (c1-c2 edge): -Y direction
        0, 1, 5,  0, 5, 4,

        // Face 2 (c2-c3 edge): +X direction
        1, 2, 6,  1, 6, 5,

        // Face 3 (c3-c4 edge): +Y direction
        2, 3, 7,  2, 7, 6,

        // Face 4 (c4-c1 edge): -X direction
        3, 0, 4,  3, 4, 7,

        // Bottom face (closing the pyramid)
        0, 2, 1,  0, 3, 2
    ]);

    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    geometry.setIndex(new THREE.BufferAttribute(indices, 1));
    geometry.computeVertexNormals();

    return geometry;
}

// ============================================================================
// FIX 3: Improved 2D Section Drawing
// ============================================================================

function createSectionDrawingImproved(inp, geom) {
    const canvas = document.getElementById('drawing2d_section');
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 600;

    // Clear background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Drawing parameters
    const margin = 80;
    const scale = Math.min(
        (canvas.width - 2 * margin) / inp.W,
        (canvas.height - 2 * margin) / geom.H_total
    );

    const baseY = canvas.height - margin;
    const centerX = canvas.width / 2;

    // Draw section (cutting through Y-axis)
    ctx.strokeStyle = '#1e3c72';
    ctx.lineWidth = 2;

    // Left vertical wall
    ctx.beginPath();
    ctx.moveTo(centerX - inp.W/2 * scale, baseY);
    ctx.lineTo(centerX - inp.W/2 * scale, baseY - inp.h1 * scale);
    ctx.stroke();

    // Right vertical wall
    ctx.beginPath();
    ctx.moveTo(centerX + inp.W/2 * scale, baseY);
    ctx.lineTo(centerX + inp.W/2 * scale, baseY - inp.h1 * scale);
    ctx.stroke();

    // Left hopper slope
    ctx.beginPath();
    ctx.moveTo(centerX - inp.W/2 * scale, baseY - inp.h1 * scale);
    ctx.lineTo(
        centerX - (inp.W1/2 + inp.offset_y) * scale,
        baseY - geom.H_total * scale
    );
    ctx.stroke();

    // Right hopper slope
    ctx.beginPath();
    ctx.moveTo(centerX + inp.W/2 * scale, baseY - inp.h1 * scale);
    ctx.lineTo(
        centerX + (inp.W1/2 + inp.offset_y) * scale,
        baseY - geom.H_total * scale
    );
    ctx.stroke();

    // Draw horizontal stiffeners
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = 3;
    const numStiffeners = Math.floor(inp.h1 / (inp.h_spacing / 1000));

    for (let i = 1; i <= numStiffeners; i++) {
        const y = baseY - (inp.h_spacing / 1000) * i * scale;
        ctx.beginPath();
        ctx.moveTo(centerX - inp.W/2 * scale, y);
        ctx.lineTo(centerX + inp.W/2 * scale, y);
        ctx.stroke();
    }

    // Dimensions
    ctx.fillStyle = '#000000';
    ctx.font = '12px Arial';

    // Height dimension
    ctx.fillText(`H = ${geom.H_total.toFixed(2)} m`, 20, baseY - geom.H_total * scale / 2);

    // Width dimension
    ctx.fillText(`W = ${inp.W.toFixed(2)} m`, centerX - 30, baseY + 30);

    // Hopper angle
    const hopperAngle = Math.atan2(inp.h2, (inp.W - inp.W1) / 2) * 180 / Math.PI;
    ctx.fillText(
        `Slope: ${hopperAngle.toFixed(1)}°`,
        centerX - inp.W/4 * scale,
        baseY - inp.h1 * scale - 20
    );

    // Title
    ctx.font = 'bold 16px Arial';
    ctx.fillText('SECTION A-A (Y-Z PLANE)', centerX - 100, 30);

    // Grid
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < canvas.width; i += 50) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < canvas.height; i += 50) {
        ctx.beginPath();
        ctx.moveTo(0, i);
        ctx.lineTo(canvas.width, i);
        ctx.stroke();
    }
}

// ============================================================================
// FIX 4: Add Detail Drawing for Connections
// ============================================================================

function createDetailDrawingImproved(inp, geom) {
    const canvas = document.getElementById('drawing2d_details');
    const ctx = canvas.getContext('2d');

    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = 600;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const detailWidth = canvas.width / 2 - 40;
    const detailHeight = 250;

    // Detail 1: Vertical Stiffener Connection
    drawStiffenerDetail(ctx, 30, 60, detailWidth, detailHeight, inp);

    // Detail 2: Hopper-Wall Junction
    drawHopperJunctionDetail(ctx, canvas.width/2 + 10, 60, detailWidth, detailHeight, inp);

    // Title
    ctx.fillStyle = '#000000';
    ctx.font = 'bold 18px Arial';
    ctx.fillText('CONNECTION DETAILS', canvas.width / 2 - 100, 30);
}

function drawStiffenerDetail(ctx, x, y, w, h, inp) {
    ctx.save();
    ctx.translate(x, y);

    // Title
    ctx.font = 'bold 14px Arial';
    ctx.fillText('Detail A: Vertical Stiffener to Shell', 10, 0);

    // Shell plate
    ctx.fillStyle = '#4a90e2';
    ctx.fillRect(10, 20, 20, 180);

    // Stiffener
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(30, 80, 60, 60);

    // Weld symbols
    ctx.strokeStyle = '#e74c3c';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(30, 80);
    ctx.lineTo(20, 70);
    ctx.moveTo(30, 140);
    ctx.lineTo(20, 150);
    ctx.stroke();

    // Dimensions
    ctx.fillStyle = '#000000';
    ctx.font = '11px Arial';
    ctx.fillText(`Shell: ${inp.t_plate_vert}mm`, 100, 110);
    ctx.fillText(`Stiffener: ${inp.v_stiff_size}`, 100, 130);
    ctx.fillText('Fillet weld', 100, 150);
    ctx.fillText('both sides', 100, 165);

    ctx.restore();
}

function drawHopperJunctionDetail(ctx, x, y, w, h, inp) {
    ctx.save();
    ctx.translate(x, y);

    // Title
    ctx.font = 'bold 14px Arial';
    ctx.fillText('Detail B: Hopper-Wall Junction', 10, 0);

    // Vertical wall
    ctx.fillStyle = '#4a90e2';
    ctx.fillRect(50, 20, 20, 80);

    // Hopper plate
    ctx.fillStyle = '#e74c3c';
    ctx.beginPath();
    ctx.moveTo(70, 100);
    ctx.lineTo(120, 160);
    ctx.lineTo(140, 160);
    ctx.lineTo(90, 100);
    ctx.closePath();
    ctx.fill();

    // Junction stiffener
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(60, 95, 40, 10);

    // Dimensions
    ctx.fillStyle = '#000000';
    ctx.font = '11px Arial';
    ctx.fillText(`Vertical: ${inp.t_plate_vert}mm`, 10, 60);
    ctx.fillText(`Hopper: ${inp.t_plate_hopper}mm`, 150, 130);
    ctx.fillText('Junction ring', 110, 105);

    ctx.restore();
}

// ============================================================================
// USAGE INSTRUCTIONS:
// Replace the corresponding functions in the main HTML file with these
// corrected versions.
// ============================================================================
