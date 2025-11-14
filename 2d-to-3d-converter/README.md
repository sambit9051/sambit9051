# 2D to 3D Model Converter - One-Stop Solution

A comprehensive, production-ready system that converts 2D technical drawings into 3D models compatible with all major engineering software packages.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-production-green.svg)

## 🚀 Features

### **Input Formats**
- ✅ **DXF/DWG** - AutoCAD drawings
- ✅ **PDF** - Technical drawings with dimension extraction
- ✅ **PNG/JPEG** - Scanned drawings with OpenCV processing

### **Output Formats**
- ✅ **IFC** - Industry Foundation Classes (Revit, Tekla, Navisworks, ArchiCAD)
- ✅ **STEP** - ISO 10303 (ANSYS, Abaqus, AVEVA, SolidWorks, CATIA)
- ✅ **IGES** - Initial Graphics Exchange (FEA tools, CAD software)
- ✅ **OBJ** - Universal 3D format
- ✅ **STL** - 3D printing and meshing

### **Supported Software**

| Software | Recommended Format | Status |
|----------|-------------------|--------|
| **Revit** | IFC | ✅ |
| **Tekla Structures** | IFC, STEP | ✅ |
| **STAAD Pro** | STEP | ✅ |
| **Navisworks** | IFC | ✅ |
| **AVEVA** | STEP | ✅ |
| **ANSYS** | STEP, IGES | ✅ |
| **Abaqus** | STEP, IGES | ✅ |

### **Capabilities**
- 🔄 **Automatic geometry extraction** from all input formats
- 📏 **Dimension recognition** from annotated drawings
- 🎯 **Smart entity classification** (beams, columns, plates, bolts)
- 🎨 **Real-time 3D visualization** with Three.js
- ⚙️ **Customizable conversion parameters** (extrusion height, thickness, scale)
- 📦 **Batch export** to multiple formats simultaneously
- 🖥️ **Modern web interface** with drag & drop

---

## 📋 Table of Contents

- [Architecture](#-architecture)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Technical Details](#-technical-details)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🏗️ Architecture

### **Hybrid System Design**

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Web)                    │
│  ┌────────────┬────────────┬──────────────────────┐ │
│  │  HTML/CSS  │  Three.js  │  JavaScript (ES6)    │ │
│  └────────────┴────────────┴──────────────────────┘ │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│               Backend (Python/Flask)                 │
│  ┌─────────────────────────────────────────────┐    │
│  │  API Server (Flask + CORS)                  │    │
│  └─────────────────────────────────────────────┘    │
│  ┌──────────┬──────────────┬──────────────────┐    │
│  │ Parsers  │  Converters  │    Exporters     │    │
│  ├──────────┼──────────────┼──────────────────┤    │
│  │ DXF      │  Geometry    │  IFC (BIM)       │    │
│  │ PDF      │  Engine      │  STEP (CAD)      │    │
│  │ Image    │  3D Model    │  IGES (FEA)      │    │
│  │          │  Generator   │  OBJ/STL         │    │
│  └──────────┴──────────────┴──────────────────┘    │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                  Core Libraries                      │
│  ezdxf • pdfplumber • OpenCV • trimesh               │
│  ifcopenshell • numpy • scipy • shapely              │
└─────────────────────────────────────────────────────┘
```

### **Technology Stack**

**Frontend:**
- HTML5 + CSS3 (Modern responsive design)
- Vanilla JavaScript (ES6+)
- Three.js (3D visualization)
- Font Awesome (Icons)

**Backend:**
- Python 3.8+
- Flask (Web framework)
- Flask-CORS (Cross-origin support)

**Core Processing:**
- **ezdxf** - DXF/DWG parsing
- **pdfplumber** - PDF analysis
- **OpenCV** - Image processing
- **NumPy/SciPy** - Numerical computations
- **Shapely** - 2D geometry operations
- **trimesh** - 3D mesh handling
- **ifcopenshell** - IFC export

---

## 🔧 Installation

### **Prerequisites**

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser (Chrome, Firefox, Edge)

### **Step 1: Clone Repository**

```bash
git clone <repository-url>
cd 2d-to-3d-converter
```

### **Step 2: Create Virtual Environment** (Recommended)

```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
cd backend
pip install -r requirements.txt
```

### **Step 4: Install System Dependencies** (For OpenCV)

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3-opencv libgl1-mesa-glx
```

**macOS:**
```bash
brew install opencv
```

**Windows:**
OpenCV will be installed via pip (included in requirements.txt)

---

## 🚀 Quick Start

### **1. Start the Backend Server**

```bash
cd backend
python app.py
```

The server will start on `http://localhost:5000`

You should see:
```
====================================================================
2D to 3D Model Converter API
====================================================================
Upload folder: /path/to/uploads
Temp folder: /path/to/temp
Allowed file types: {'pdf', 'dxf', 'dwg', 'png', 'jpg', 'jpeg'}
Max file size: 50 MB
====================================================================
Starting server on http://localhost:5000
====================================================================
```

### **2. Access the Web Interface**

Open your browser and navigate to:
```
http://localhost:5000
```

### **3. Convert Your First Drawing**

1. **Upload** - Drag & drop your 2D drawing (DXF, PDF, PNG, etc.)
2. **Parse** - Click "Parse Drawing" to extract entities
3. **Adjust Parameters** - Set extrusion height, thickness, and scale
4. **Generate** - Click "Generate 3D Model" to create your model
5. **Preview** - View and interact with your 3D model
6. **Export** - Download in your desired format(s)

---

## 📖 Usage Guide

### **Workflow Overview**

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Upload  │ → │  Parse   │ → │ Generate │ → │  Export  │
│  2D File │   │ Geometry │   │ 3D Model │   │  Formats │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

### **1. Uploading Files**

**Supported Formats:**
- `.dxf`, `.dwg` - CAD drawings
- `.pdf` - Technical drawings
- `.png`, `.jpg`, `.jpeg` - Scanned/raster images

**File Size Limit:** 50 MB

**Tips:**
- For best results with images, use high-resolution scans (300 DPI+)
- PDF files should contain vector graphics, not just scanned images
- DXF/DWG files provide the most accurate results

### **2. Parsing Options**

The parser automatically detects:
- Lines, circles, arcs, polylines
- Rectangles and polygons
- Text annotations and dimensions
- Layers and organization

**For Images:**
- Line detection using Hough transform
- Contour detection for shapes
- Circle detection
- Optional OCR for text (requires pytesseract)

### **3. Conversion Parameters**

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| **Extrusion Height** | Height of 3D extrusion (Z-axis) | 100 mm | 1-1000+ |
| **Thickness** | Wall/beam thickness | 10 mm | 0.1-100+ |
| **Scale Factor** | Global scaling multiplier | 1.0 | 0.1-10 |

### **4. Export Options**

#### **For BIM (Building Information Modeling):**
- **IFC** - Use for Revit, Tekla, Navisworks
  - Full BIM structure with proper element classification
  - Supports project/site/building hierarchy
  - Configurable units (mm, m, ft)

#### **For CAD (Computer-Aided Design):**
- **STEP** - Use for SolidWorks, CATIA, AVEVA
  - ISO standard format
  - Precise geometry representation
  - Supports assemblies

#### **For FEA (Finite Element Analysis):**
- **STEP** or **IGES** - Use for ANSYS, Abaqus
  - Clean mesh geometry
  - Suitable for meshing operations
  - Legacy compatibility (IGES)

#### **For General 3D:**
- **OBJ** - Universal format, good for visualization
- **STL** - 3D printing, meshing

### **5. Batch Export**

Select multiple formats and click "Download All Selected Formats" to export as a single ZIP file containing all formats.

---

## 🔌 API Documentation

### **Endpoints**

#### **Health Check**
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "2D to 3D Converter",
  "version": "1.0.0",
  "timestamp": "2025-11-14T12:00:00"
}
```

#### **Upload File**
```http
POST /api/upload
Content-Type: multipart/form-data

file: <binary>
```

**Response:**
```json
{
  "success": true,
  "file_id": "20251114_120000_drawing.dxf",
  "original_name": "drawing.dxf",
  "file_type": "cad",
  "file_size": 1048576,
  "upload_time": "20251114_120000"
}
```

#### **Parse File**
```http
POST /api/parse
Content-Type: application/json

{
  "file_id": "20251114_120000_drawing.dxf",
  "options": {
    "layers": ["0", "WALLS"],
    "extract_dimensions": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "file_id": "20251114_120000_drawing.dxf",
  "parse_result": {
    "entities": [...],
    "layers": [...],
    "dimensions": [...],
    "metadata": {...}
  }
}
```

#### **Convert to 3D**
```http
POST /api/convert
Content-Type: application/json

{
  "entities": [...],
  "parameters": {
    "extrusion_height": 100,
    "thickness": 10,
    "scale": 1.0
  }
}
```

**Response:**
```json
{
  "success": true,
  "model_3d": {
    "model_id": "uuid",
    "vertices": [[x, y, z], ...],
    "faces": [[i, j, k], ...],
    "stats": {...}
  }
}
```

#### **Export Model**
```http
POST /api/export/{format}
Content-Type: application/json

{
  "model_data": {...},
  "options": {
    "schema": "IFC4",
    "units": "MILLIMETRE"
  }
}
```

**Formats:** `ifc`, `step`, `iges`, `obj`, `stl`

**Response:** Binary file download

#### **Batch Export**
```http
POST /api/batch-export
Content-Type: application/json

{
  "model_data": {...},
  "formats": ["ifc", "step", "iges"]
}
```

**Response:** ZIP file download

---

## 🔬 Technical Details

### **Geometric Processing Pipeline**

```
Input File → Parser → 2D Entities → Geometry Engine → 3D Model → Exporter → Output File
```

1. **Parser Stage:**
   - File format detection
   - Entity extraction (lines, circles, polygons)
   - Dimension recognition
   - Layer/group organization

2. **Geometry Engine:**
   - Collinear line merging
   - Closed region detection
   - Polyline simplification
   - Bounding box calculation

3. **3D Model Generation:**
   - Polygon extrusion (creates solids)
   - Circle extrusion (creates cylinders)
   - Line extrusion (creates beams)
   - Mesh optimization

4. **Export Stage:**
   - Format-specific conversion
   - Metadata inclusion
   - File validation

### **Algorithms Used**

- **Hough Line Transform** - Line detection in images
- **Contour Detection** - Shape recognition
- **Polygon Triangulation** - Mesh generation
- **Bézier Curves** - Spline handling
- **Boolean Operations** - Region detection (Shapely)

### **Performance**

| Operation | Time (approx) |
|-----------|---------------|
| DXF Parse (1000 entities) | < 1s |
| PDF Parse (10 pages) | 2-5s |
| Image Parse (2000x2000px) | 3-8s |
| 3D Generation (1000 faces) | < 1s |
| IFC Export | 1-3s |
| STEP Export | 2-5s |

---

## 🛠️ Troubleshooting

### **Common Issues**

**1. "Backend API may be unavailable"**
- Ensure backend server is running: `python backend/app.py`
- Check if port 5000 is available
- Verify firewall settings

**2. "Module not found" errors**
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**3. OpenCV import errors (Linux)**
```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
```

**4. ifcopenshell installation issues**
```bash
pip install --upgrade pip
pip install ifcopenshell==0.7.0
```

**5. Large file upload fails**
- Check file size (max 50MB)
- Increase timeout in browser
- Split large drawings into sections

**6. Poor image parsing results**
- Use higher resolution scans (300 DPI minimum)
- Ensure good contrast
- Clean up noise in image editing software first

---

## 📦 Project Structure

```
2d-to-3d-converter/
├── backend/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt       # Python dependencies
│   ├── parsers/              # File parsers
│   │   ├── dxf_parser.py
│   │   ├── pdf_parser.py
│   │   └── image_parser.py
│   ├── converters/           # Geometry processing
│   │   ├── geometry_engine.py
│   │   └── model_generator.py
│   ├── exporters/            # Format exporters
│   │   ├── ifc_exporter.py
│   │   ├── step_exporter.py
│   │   └── iges_exporter.py
│   ├── uploads/              # Uploaded files (temp)
│   └── temp/                 # Export files (temp)
│
├── frontend/
│   ├── index.html            # Main web interface
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js            # API communication
│       ├── viewer.js         # 3D visualization
│       └── app.js            # Main application logic
│
├── docs/                     # Documentation
├── examples/                 # Sample files
└── README.md                # This file
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Acknowledgments

- **ezdxf** - DXF/DWG processing
- **ifcopenshell** - IFC support
- **Three.js** - 3D visualization
- **OpenCV** - Computer vision
- All open-source contributors

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check documentation in `/docs`
- Review troubleshooting section above

---

**Built with ❤️ for the engineering community**
