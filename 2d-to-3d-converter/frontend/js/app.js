/**
 * Main Application Logic
 * 2D to 3D Converter
 */

// Global state
const AppState = {
    currentStep: 1,
    uploadedFile: null,
    fileId: null,
    parseResult: null,
    modelData: null,
    viewer: null
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('2D to 3D Converter initialized');

    // Setup file upload
    setupFileUpload();

    // Check API health
    checkAPIHealth();
});

/**
 * Setup drag & drop file upload
 */
function setupFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');

    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // File selected
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0]);
    });

    // Drag & drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });

    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        handleFileSelect(file);
    });
}

/**
 * Handle file selection
 */
async function handleFileSelect(file) {
    if (!file) return;

    // Validate file type
    const allowedTypes = ['dxf', 'dwg', 'pdf', 'png', 'jpg', 'jpeg'];
    const extension = file.name.split('.').pop().toLowerCase();

    if (!allowedTypes.includes(extension)) {
        showToast('error', `File type .${extension} is not supported`);
        return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
        showToast('error', 'File size exceeds 50MB limit');
        return;
    }

    AppState.uploadedFile = file;

    // Show file info
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    document.getElementById('fileType').textContent = extension.toUpperCase();

    // Update file icon
    const iconMap = {
        'dxf': 'fa-file-code',
        'dwg': 'fa-file-code',
        'pdf': 'fa-file-pdf',
        'png': 'fa-file-image',
        'jpg': 'fa-file-image',
        'jpeg': 'fa-file-image'
    };

    const fileIcon = document.querySelector('.file-icon');
    fileIcon.className = `fas ${iconMap[extension] || 'fa-file'} file-icon`;

    // Hide upload zone, show file info
    document.getElementById('uploadZone').classList.add('hidden');
    document.getElementById('fileInfo').classList.remove('hidden');

    // Upload file to backend
    try {
        showLoading('Uploading file...');

        const result = await API.uploadFile(file);
        AppState.fileId = result.file_id;

        hideLoading();
        showToast('success', 'File uploaded successfully!');

    } catch (error) {
        hideLoading();
        showToast('error', `Upload failed: ${error.message}`);
        removeFile();
    }
}

/**
 * Remove selected file
 */
function removeFile() {
    AppState.uploadedFile = null;
    AppState.fileId = null;

    document.getElementById('uploadZone').classList.remove('hidden');
    document.getElementById('fileInfo').classList.add('hidden');
    document.getElementById('fileInput').value = '';
}

/**
 * Parse uploaded file
 */
async function parseFile() {
    if (!AppState.fileId) {
        showToast('error', 'No file uploaded');
        return;
    }

    try {
        showLoading('Parsing drawing...');

        const result = await API.parseFile(AppState.fileId);
        AppState.parseResult = result.parse_result;

        hideLoading();

        // Display parse results
        displayParseResults(AppState.parseResult);

        // Move to step 2
        setStep(2);

        showToast('success', 'Drawing parsed successfully!');

    } catch (error) {
        hideLoading();
        showToast('error', `Parsing failed: ${error.message}`);
    }
}

/**
 * Display parsing results
 */
function displayParseResults(parseResult) {
    const { entities, metadata } = parseResult;

    // Display stats
    const statsHtml = `
        <div class="stat-card">
            <h4>Total Entities</h4>
            <div class="value">${entities.length}</div>
        </div>
        <div class="stat-card">
            <h4>File Type</h4>
            <div class="value">${metadata.filename.split('.').pop().toUpperCase()}</div>
        </div>
        <div class="stat-card">
            <h4>Layers</h4>
            <div class="value">${parseResult.layers?.length || 1}</div>
        </div>
        <div class="stat-card">
            <h4>Dimensions</h4>
            <div class="value">${parseResult.dimensions?.length || 0}</div>
        </div>
    `;

    document.getElementById('parseStats').innerHTML = statsHtml;

    // Display entities by type
    const entityTypes = {};
    entities.forEach(entity => {
        const type = entity.type;
        entityTypes[type] = (entityTypes[type] || 0) + 1;
    });

    const entityIconMap = {
        'line': 'fa-minus',
        'circle': 'fa-circle',
        'arc': 'fa-bezier-curve',
        'polyline': 'fa-draw-polygon',
        'rectangle': 'fa-square',
        'polygon': 'fa-draw-polygon',
        'text': 'fa-font'
    };

    const entitiesHtml = Object.entries(entityTypes)
        .map(([type, count]) => `
            <div class="entity-item">
                <div class="entity-icon">
                    <i class="fas ${entityIconMap[type] || 'fa-shapes'}"></i>
                </div>
                <div class="entity-info">
                    <h5>${type.charAt(0).toUpperCase() + type.slice(1)}s</h5>
                    <p>${count} found</p>
                </div>
            </div>
        `)
        .join('');

    document.getElementById('entitiesList').innerHTML = entitiesHtml;
}

/**
 * Convert to 3D
 */
async function convertTo3D() {
    if (!AppState.parseResult) {
        showToast('error', 'No parsed data available');
        return;
    }

    try {
        showLoading('Generating 3D model...');

        // Get conversion parameters
        const parameters = {
            extrusion_height: parseFloat(document.getElementById('extrusionHeight').value),
            thickness: parseFloat(document.getElementById('thickness').value),
            scale: parseFloat(document.getElementById('scale').value)
        };

        const result = await API.convertTo3D(
            AppState.parseResult.entities,
            parameters
        );

        AppState.modelData = result.model_3d;

        hideLoading();

        // Display model stats
        displayModelStats(AppState.modelData.stats);

        // Initialize 3D viewer
        if (!AppState.viewer) {
            AppState.viewer = new Viewer3D('viewer3D');
        }

        // Load model into viewer
        AppState.viewer.loadModel(AppState.modelData);

        // Move to step 3
        setStep(3);

        showToast('success', '3D model generated successfully!');

    } catch (error) {
        hideLoading();
        showToast('error', `Conversion failed: ${error.message}`);
    }
}

/**
 * Display model statistics
 */
function displayModelStats(stats) {
    const statsHtml = `
        <div class="stat-card">
            <h4>Vertices</h4>
            <div class="value">${stats.total_vertices.toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <h4>Faces</h4>
            <div class="value">${stats.total_faces.toLocaleString()}</div>
        </div>
        <div class="stat-card">
            <h4>Meshes</h4>
            <div class="value">${stats.total_meshes}</div>
        </div>
        <div class="stat-card">
            <h4>Size</h4>
            <div class="value">${stats.bounding_box ?
                Math.max(...stats.bounding_box.size).toFixed(1) : 'N/A'}</div>
        </div>
    `;

    document.getElementById('modelStats').innerHTML = statsHtml;
}

/**
 * Show export options
 */
function showExportOptions() {
    setStep(4);
}

/**
 * Export all selected formats
 */
async function exportAll() {
    if (!AppState.modelData) {
        showToast('error', 'No model data available');
        return;
    }

    // Get selected formats
    const formatCheckboxes = document.querySelectorAll('.format-option input:checked');
    const formats = Array.from(formatCheckboxes).map(cb => cb.value);

    if (formats.length === 0) {
        showToast('warning', 'Please select at least one export format');
        return;
    }

    try {
        showLoading('Exporting models...');

        // Batch export
        const blob = await API.batchExport(AppState.modelData, formats);

        // Download zip file
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `model_export_${Date.now()}.zip`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        hideLoading();
        showToast('success', `Exported ${formats.length} format(s) successfully!`);

    } catch (error) {
        hideLoading();
        showToast('error', `Export failed: ${error.message}`);
    }
}

/**
 * Export individual format
 */
async function exportSingle() {
    if (!AppState.modelData) {
        showToast('error', 'No model data available');
        return;
    }

    const formatCheckboxes = document.querySelectorAll('.format-option input:checked');
    const formats = Array.from(formatCheckboxes).map(cb => cb.value);

    if (formats.length === 0) {
        showToast('warning', 'Please select at least one export format');
        return;
    }

    try {
        showLoading('Exporting models...');

        // Export each format individually
        for (const format of formats) {
            const blob = await API.exportModel(AppState.modelData, format);

            // Download file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `model_${Date.now()}.${format}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            // Small delay between downloads
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        hideLoading();
        showToast('success', `Exported ${formats.length} file(s) successfully!`);

    } catch (error) {
        hideLoading();
        showToast('error', `Export failed: ${error.message}`);
    }
}

/**
 * 3D Viewer controls
 */
function resetCamera() {
    if (AppState.viewer) {
        AppState.viewer.resetCamera();
    }
}

function toggleWireframe() {
    if (AppState.viewer) {
        AppState.viewer.toggleWireframe();
    }
}

function toggleGrid() {
    if (AppState.viewer) {
        AppState.viewer.toggleGrid();
    }
}

/**
 * Set active step
 */
function setStep(step) {
    AppState.currentStep = step;

    // Update step indicators
    document.querySelectorAll('.step').forEach((el, index) => {
        if (index + 1 < step) {
            el.classList.add('completed');
            el.classList.remove('active');
        } else if (index + 1 === step) {
            el.classList.add('active');
            el.classList.remove('completed');
        } else {
            el.classList.remove('active', 'completed');
        }
    });

    // Show/hide sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });

    const sections = ['step-upload', 'step-parse', 'step-viewer', 'step-export'];
    document.getElementById(sections[step - 1]).classList.remove('hidden');
}

/**
 * UI Helper Functions
 */
function showLoading(message = 'Processing...') {
    document.getElementById('loadingText').textContent = message;
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

function showToast(type, message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' :
                         type === 'error' ? 'times-circle' :
                         type === 'warning' ? 'exclamation-triangle' :
                         'info-circle'}"></i>
        <span>${message}</span>
    `;

    document.getElementById('toastContainer').appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showHelp() {
    alert(`2D to 3D Converter - Help

1. UPLOAD: Drag & drop or browse to upload your 2D drawing (DXF, DWG, PDF, PNG, JPEG)
2. PARSE: The system extracts geometric entities from your drawing
3. CONVERT: Adjust parameters and generate 3D model
4. EXPORT: Download in multiple formats for your target software

Supported Software:
- Revit: IFC
- Tekla: IFC, STEP
- STAAD Pro: STEP
- Navisworks: IFC
- AVEVA: STEP
- ANSYS: STEP, IGES
- Abaqus: STEP, IGES

For support, please visit our documentation.`);
}

async function checkAPIHealth() {
    try {
        const health = await API.healthCheck();
        console.log('API Health:', health);
    } catch (error) {
        console.error('API health check failed:', error);
        showToast('warning', 'Backend API may be unavailable. Please ensure the server is running.');
    }
}
