/**
 * API Communication Module
 * Handles all backend API calls
 */

const API_BASE_URL = window.location.origin;

const API = {
    /**
     * Upload file to backend
     */
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE_URL}/api/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        return await response.json();
    },

    /**
     * Parse uploaded file
     */
    async parseFile(fileId, options = {}) {
        const response = await fetch(`${API_BASE_URL}/api/parse`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: fileId,
                options: options
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Parsing failed');
        }

        return await response.json();
    },

    /**
     * Convert 2D entities to 3D model
     */
    async convertTo3D(entities, parameters = {}) {
        const response = await fetch(`${API_BASE_URL}/api/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                entities: entities,
                parameters: parameters
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Conversion failed');
        }

        return await response.json();
    },

    /**
     * Export model to specific format
     */
    async exportModel(modelData, format, options = {}) {
        const response = await fetch(`${API_BASE_URL}/api/export/${format}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_data: modelData,
                options: options
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `Export to ${format} failed`);
        }

        // Return blob for file download
        return await response.blob();
    },

    /**
     * Export model to multiple formats (batch)
     */
    async batchExport(modelData, formats, options = {}) {
        const response = await fetch(`${API_BASE_URL}/api/batch-export`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                model_data: modelData,
                formats: formats,
                options: options
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Batch export failed');
        }

        // Return blob for zip file download
        return await response.blob();
    },

    /**
     * Health check
     */
    async healthCheck() {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        return await response.json();
    }
};

// Export for use in other modules
window.API = API;
