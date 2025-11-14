"""
2D to 3D Model Converter - Main Flask API
Converts 2D drawings (PDF, DWG, DXF, JPEG, PNG) to 3D models
Exports to multiple formats: IFC, STEP, IGES, SAT for various software
"""

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import logging
from pathlib import Path
import traceback
from datetime import datetime

# Import parsers
from parsers.dxf_parser import DXFParser
from parsers.pdf_parser import PDFParser
from parsers.image_parser import ImageParser

# Import converters
from converters.geometry_engine import GeometryEngine
from converters.model_generator import ModelGenerator

# Import exporters
from exporters.ifc_exporter import IFCExporter
from exporters.step_exporter import STEPExporter
from exporters.iges_exporter import IGESExporter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__,
            static_folder='../frontend',
            template_folder='../frontend')
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(__file__).parent / 'uploads'
TEMP_FOLDER = Path(__file__).parent / 'temp'
ALLOWED_EXTENSIONS = {'pdf', 'dxf', 'dwg', 'png', 'jpg', 'jpeg'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Create directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
TEMP_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['dxf', 'dwg']:
        return 'cad'
    elif ext == 'pdf':
        return 'pdf'
    elif ext in ['png', 'jpg', 'jpeg']:
        return 'image'
    return 'unknown'

@app.route('/')
def index():
    """Serve the main frontend page"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': '2D to 3D Converter',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Upload and validate 2D drawing file
    Returns: file_id, file_type, metadata
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Allowed: {ALLOWED_EXTENSIONS}'}), 400

        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / unique_filename

        file.save(str(filepath))

        # Get file metadata
        file_size = os.path.getsize(filepath)
        file_type = get_file_type(filename)

        logger.info(f"File uploaded: {unique_filename} ({file_size} bytes, type: {file_type})")

        return jsonify({
            'success': True,
            'file_id': unique_filename,
            'original_name': filename,
            'file_type': file_type,
            'file_size': file_size,
            'upload_time': timestamp
        })

    except Exception as e:
        logger.error(f"Upload error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/api/parse', methods=['POST'])
def parse_file():
    """
    Parse 2D drawing and extract geometry
    Input: file_id, parse_options
    Returns: entities, dimensions, metadata
    """
    try:
        data = request.json
        file_id = data.get('file_id')
        options = data.get('options', {})

        if not file_id:
            return jsonify({'error': 'No file_id provided'}), 400

        filepath = UPLOAD_FOLDER / file_id

        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        file_type = get_file_type(file_id)

        # Select appropriate parser
        if file_type == 'cad':
            parser = DXFParser()
            result = parser.parse(str(filepath), options)
        elif file_type == 'pdf':
            parser = PDFParser()
            result = parser.parse(str(filepath), options)
        elif file_type == 'image':
            parser = ImageParser()
            result = parser.parse(str(filepath), options)
        else:
            return jsonify({'error': 'Unknown file type'}), 400

        logger.info(f"Parsed {file_id}: {len(result.get('entities', []))} entities found")

        return jsonify({
            'success': True,
            'file_id': file_id,
            'parse_result': result
        })

    except Exception as e:
        logger.error(f"Parse error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Parsing failed: {str(e)}'}), 500

@app.route('/api/convert', methods=['POST'])
def convert_to_3d():
    """
    Convert parsed 2D entities to 3D model
    Input: entities, conversion_parameters
    Returns: 3d_model (mesh data for preview)
    """
    try:
        data = request.json
        entities = data.get('entities', [])
        params = data.get('parameters', {})

        if not entities:
            return jsonify({'error': 'No entities provided'}), 400

        # Process geometry
        geometry_engine = GeometryEngine()
        processed_geometry = geometry_engine.process(entities, params)

        # Generate 3D model
        model_generator = ModelGenerator()
        model_3d = model_generator.generate(processed_geometry, params)

        logger.info(f"3D model generated: {model_3d.get('stats', {})}")

        return jsonify({
            'success': True,
            'model_3d': model_3d,
            'preview_url': f'/api/preview/{model_3d.get("model_id")}'
        })

    except Exception as e:
        logger.error(f"Conversion error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@app.route('/api/export/<format_type>', methods=['POST'])
def export_model(format_type):
    """
    Export 3D model to specified format
    Formats: ifc, step, iges, sat, obj, stl
    Returns: downloadable file
    """
    try:
        data = request.json
        model_data = data.get('model_data')
        export_options = data.get('options', {})

        if not model_data:
            return jsonify({'error': 'No model data provided'}), 400

        format_type = format_type.lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Select appropriate exporter
        if format_type == 'ifc':
            exporter = IFCExporter()
            output_file = TEMP_FOLDER / f'model_{timestamp}.ifc'
            exporter.export(model_data, str(output_file), export_options)

        elif format_type == 'step' or format_type == 'stp':
            exporter = STEPExporter()
            output_file = TEMP_FOLDER / f'model_{timestamp}.step'
            exporter.export(model_data, str(output_file), export_options)

        elif format_type == 'iges' or format_type == 'igs':
            exporter = IGESExporter()
            output_file = TEMP_FOLDER / f'model_{timestamp}.iges'
            exporter.export(model_data, str(output_file), export_options)

        elif format_type == 'obj':
            # Simple OBJ export for general 3D viewing
            output_file = TEMP_FOLDER / f'model_{timestamp}.obj'
            export_obj(model_data, str(output_file))

        elif format_type == 'stl':
            # STL export for 3D printing/meshing
            output_file = TEMP_FOLDER / f'model_{timestamp}.stl'
            export_stl(model_data, str(output_file))

        else:
            return jsonify({'error': f'Unsupported format: {format_type}'}), 400

        logger.info(f"Exported model to {format_type.upper()}: {output_file.name}")

        return send_file(
            str(output_file),
            as_attachment=True,
            download_name=output_file.name,
            mimetype='application/octet-stream'
        )

    except Exception as e:
        logger.error(f"Export error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/batch-export', methods=['POST'])
def batch_export():
    """
    Export model to multiple formats simultaneously
    Returns: zip file with all formats
    """
    try:
        import zipfile

        data = request.json
        model_data = data.get('model_data')
        formats = data.get('formats', ['ifc', 'step', 'iges'])

        if not model_data:
            return jsonify({'error': 'No model data provided'}), 400

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f'model_export_{timestamp}.zip'
        zip_path = TEMP_FOLDER / zip_filename

        with zipfile.ZipFile(str(zip_path), 'w') as zipf:
            for fmt in formats:
                try:
                    # Export each format
                    if fmt == 'ifc':
                        exporter = IFCExporter()
                        file_path = TEMP_FOLDER / f'model_{timestamp}.ifc'
                        exporter.export(model_data, str(file_path), {})
                        zipf.write(str(file_path), file_path.name)

                    elif fmt == 'step':
                        exporter = STEPExporter()
                        file_path = TEMP_FOLDER / f'model_{timestamp}.step'
                        exporter.export(model_data, str(file_path), {})
                        zipf.write(str(file_path), file_path.name)

                    elif fmt == 'iges':
                        exporter = IGESExporter()
                        file_path = TEMP_FOLDER / f'model_{timestamp}.iges'
                        exporter.export(model_data, str(file_path), {})
                        zipf.write(str(file_path), file_path.name)

                except Exception as e:
                    logger.warning(f"Failed to export {fmt}: {str(e)}")

        logger.info(f"Batch export completed: {zip_filename}")

        return send_file(
            str(zip_path),
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )

    except Exception as e:
        logger.error(f"Batch export error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': f'Batch export failed: {str(e)}'}), 500

def export_obj(model_data, output_path):
    """Simple OBJ export"""
    vertices = model_data.get('vertices', [])
    faces = model_data.get('faces', [])

    with open(output_path, 'w') as f:
        f.write("# 2D to 3D Converter - OBJ Export\n")

        # Write vertices
        for v in vertices:
            f.write(f"v {v[0]} {v[1]} {v[2]}\n")

        # Write faces (1-indexed)
        for face in faces:
            indices = ' '.join([str(i+1) for i in face])
            f.write(f"f {indices}\n")

def export_stl(model_data, output_path):
    """Simple STL export (ASCII)"""
    faces = model_data.get('faces', [])
    vertices = model_data.get('vertices', [])

    with open(output_path, 'w') as f:
        f.write("solid Model\n")

        for face in faces:
            # Calculate normal (simplified)
            v0, v1, v2 = [vertices[i] for i in face[:3]]
            f.write(f"  facet normal 0 0 1\n")
            f.write(f"    outer loop\n")
            f.write(f"      vertex {v0[0]} {v0[1]} {v0[2]}\n")
            f.write(f"      vertex {v1[0]} {v1[1]} {v1[2]}\n")
            f.write(f"      vertex {v2[0]} {v2[1]} {v2[2]}\n")
            f.write(f"    endloop\n")
            f.write(f"  endfacet\n")

        f.write("endsolid Model\n")

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size: 50MB'}), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("2D to 3D Model Converter API")
    print("=" * 60)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Temp folder: {TEMP_FOLDER}")
    print(f"Allowed file types: {ALLOWED_EXTENSIONS}")
    print(f"Max file size: {MAX_FILE_SIZE / (1024*1024):.0f} MB")
    print("=" * 60)
    print("Starting server on http://localhost:5000")
    print("=" * 60)

    app.run(debug=True, host='0.0.0.0', port=5000)
