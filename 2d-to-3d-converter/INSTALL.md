# Installation Guide
## 2D to 3D Model Converter

This guide will help you set up the 2D to 3D Converter on your system.

---

## Quick Installation (Recommended)

### Linux/macOS

```bash
# 1. Make startup script executable
chmod +x start.sh

# 2. Run the startup script (handles everything automatically)
./start.sh
```

### Windows

```cmd
# Simply double-click start.bat
# Or run from command prompt:
start.bat
```

The startup script will:
- Create a virtual environment if needed
- Install all Python dependencies
- Start the backend server

Once running, open your browser to: **http://localhost:5000**

---

## Manual Installation

### Prerequisites

Before you begin, ensure you have:
- **Python 3.8+** installed
- **pip** (Python package manager)
- **Git** (to clone repository)

Check your Python version:
```bash
python --version
# or
python3 --version
```

---

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd 2d-to-3d-converter
```

---

### Step 2: Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

You should see `(venv)` in your terminal prompt.

---

### Step 3: Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- ezdxf (DXF/DWG parsing)
- pdfplumber (PDF processing)
- OpenCV (image processing)
- ifcopenshell (IFC export)
- trimesh (3D mesh handling)
- and more...

**Note:** Installation may take 5-10 minutes depending on your internet speed.

---

### Step 4: Install System Dependencies (Optional)

Some features require additional system libraries:

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y python3-opencv libgl1-mesa-glx libglib2.0-0
```

#### macOS:
```bash
brew install opencv
```

#### Windows:
No additional installation needed (OpenCV is installed via pip).

---

### Step 5: Start the Server

```bash
# From the backend directory:
python app.py
```

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
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
```

---

### Step 6: Access the Web Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

You should see the 2D to 3D Converter interface!

---

## Troubleshooting Installation

### Issue: "python: command not found"

**Solution:** Install Python 3.8+ from:
- **Linux:** `sudo apt-get install python3`
- **macOS:** `brew install python3` or download from python.org
- **Windows:** Download from https://python.org

### Issue: "pip: command not found"

**Solution:** Install pip:
```bash
# Linux/macOS
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install pip                  # macOS

# Windows
python -m ensurepip --upgrade
```

### Issue: "Permission denied" when running start.sh

**Solution:**
```bash
chmod +x start.sh
```

### Issue: OpenCV import errors

**Ubuntu/Debian:**
```bash
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0
pip install opencv-python-headless
```

**macOS:**
```bash
brew install opencv
```

### Issue: ifcopenshell installation fails

**Solution:** Try installing from wheel:
```bash
pip install --upgrade pip
pip install ifcopenshell==0.7.0
```

If still failing, skip ifcopenshell for now:
```bash
# Edit requirements.txt and comment out ifcopenshell
# IFC export will be unavailable, but other formats will work
```

### Issue: Port 5000 already in use

**Solution:** Kill the process using port 5000:

**Linux/macOS:**
```bash
lsof -ti:5000 | xargs kill -9
```

**Windows:**
```cmd
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

Or change the port in `backend/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use port 5001 instead
```

---

## Verifying Installation

### 1. Check Backend API

Test the health endpoint:
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "2D to 3D Converter",
  "version": "1.0.0",
  "timestamp": "2025-11-14T12:00:00"
}
```

### 2. Check Frontend

Open browser to `http://localhost:5000` and you should see:
- Header with "2D to 3D Converter" logo
- Four-step progress indicator
- Upload zone with drag & drop

### 3. Test Upload

Try uploading a sample file:
- Drag a DXF, PDF, or image file to the upload zone
- Click "Parse Drawing"
- You should see parsing results with entity statistics

---

## Updating

To update to the latest version:

```bash
# 1. Pull latest changes
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 3. Update dependencies
pip install -r backend/requirements.txt --upgrade

# 4. Restart server
cd backend
python app.py
```

---

## Uninstalling

To completely remove the application:

```bash
# 1. Deactivate virtual environment
deactivate

# 2. Remove directory
cd ..
rm -rf 2d-to-3d-converter

# 3. (Optional) Remove system dependencies
# Ubuntu/Debian
sudo apt-get remove python3-opencv

# macOS
brew uninstall opencv
```

---

## Production Deployment

For production use, consider:

### 1. Use a Production WSGI Server

Replace Flask development server with Gunicorn:

```bash
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. Set Up Reverse Proxy

Use Nginx to serve the application:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable HTTPS

```bash
# Using Certbot
sudo certbot --nginx -d your-domain.com
```

### 4. Set Up as System Service

Create `/etc/systemd/system/2d3d-converter.service`:

```ini
[Unit]
Description=2D to 3D Converter
After=network.target

[Service]
User=youruser
WorkingDirectory=/path/to/2d-to-3d-converter/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable 2d3d-converter
sudo systemctl start 2d3d-converter
```

---

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review the main README.md
3. Check server logs in terminal
4. Open an issue on GitHub with:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce

---

**Happy Converting! 🚀**
