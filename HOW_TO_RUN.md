# How to Run the Orange Disease Detection System

## 🚀 Quick Start (Recommended)

### Option 1: Windows Users (Easiest)
Simply **double-click** the `run_app.bat` file in the project root:
```
Orange_Disease_Project/
└── run_app.bat ← Double-click this
```

This will:
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Create necessary folders
- ✅ Start the Flask server
- ✅ Open the application in browser

---

### Option 2: All Users (Python Method)

Run this command from the project root:
```bash
python run_app.py
```

This script will:
- ✅ Verify Python version (3.8+)
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Set up directories
- ✅ Launch the Flask backend

---

## 🔧 Manual Setup (Step-by-Step)

### Step 1: Open Terminal/PowerShell
Navigate to the project root:
```bash
cd "C:\Users\user\OneDrive\Desktop\best project\Orange_Disease_Project"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv

# macOS/Linux
python3 -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
# Windows - PowerShell
.\venv\Scripts\Activate.ps1

# Windows - Command Prompt
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed numpy, pandas, tensorflow, flask, ...
```

### Step 5: Create Necessary Directories
```bash
mkdir dataset/preprocessed models static/uploads logs
```

### Step 6: Run the Application
```bash
cd backend
python app.py
```

**Expected Output:**
```
============================================================
ORANGE DISEASE DETECTION - FLASK API SERVER
============================================================

⚠ Running in DEMO mode (model/database not available)
✓ Mock model initialized for testing
✓ Database connection skipped (optional in demo)
✓ Server starting at http://localhost:5000/

WARNING in werkzeug: Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

---

## 🌐 Access the Application

### Web Interface
Open your browser and go to:
```
http://localhost:5000/
```

You should see the Orange Disease Detection interface with:
- Upload area for images
- Language selector (English, Hindi, Marathi)
- Disease detection results
- Recommendations

### API Endpoints
Test the API directly:

```bash
# Health check
curl http://localhost:5000/api/health

# Get available languages
curl http://localhost:5000/api/languages

# Get available diseases
curl http://localhost:5000/api/diseases

# Make a prediction (upload image)
curl -X POST -F "image=@path/to/image.jpg" http://localhost:5000/api/predict
```

---

## ✅ Verification Checklist

After starting the app, you should see:

- ✅ Terminal shows `Running on http://0.0.0.0:5000/`
- ✅ Browser can access http://localhost:5000/
- ✅ You see the app interface (upload area, language selector)
- ✅ No Python errors in terminal

---

## ⚠️ Troubleshooting

### Issue: "Port 5000 already in use"
**Solution**: Kill the process using port 5000
```bash
# Windows - PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process

# Windows - Command Prompt
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:5000 | xargs kill -9
```

Then restart: `python backend/app.py`

---

### Issue: "Module not found" error
**Solution**: Make sure you're in the venv:
```bash
# Check if venv is active (should show (venv) in prompt)
pip list  # Should show installed packages
```

If not activated:
```bash
# Windows
venv\Scripts\activate.bat

# macOS/Linux
source venv/bin/activate
```

Then retry: `python backend/app.py`

---

### Issue: "Failed to Load Page" in browser
**Solution**: 
1. Check if terminal shows `Running on http://0.0.0.0:5000/`
2. Wait 5-10 seconds for app to fully start
3. Refresh browser (Ctrl+R or Cmd+R)
4. Try http://localhost:5000/ instead of http://127.0.0.1:5000/

---

### Issue: "ModuleNotFoundError: No module named 'tensorflow'"
**Solution**: Reinstall dependencies
```bash
pip install -r requirements.txt --upgrade
```

---

## 📊 Features Available in Demo Mode

When running without the full ML model, these features work:

✅ **Web Interface**
- Upload images
- See mock predictions
- Multilingual support
- Responsive design

✅ **API Endpoints**
- /api/health - Server status
- /api/predict - Generate predictions
- /api/diseases - List diseases
- /api/languages - Supported languages

✅ **Mock Predictions**
- Random disease classification
- Realistic confidence scores (85-99%)
- Proper JSON responses

---

## 🔧 Next Steps

### After Initial Run (Optional):

1. **Setup Real ML Model**
   ```bash
   python training/model_trainer.py
   ```
   This trains the models (requires dataset)

2. **Setup Database**
   ```bash
   python database/db_setup.py
   ```
   This creates MySQL tables (requires MySQL running)

3. **Add Dataset**
   - Place orange disease images in `dataset/` folder
   - Organize by disease class folder
   - Run preprocessing

---

## 📚 Full Project Setup (Complete Implementation)

For complete setup with ML training:

1. Follow INSTALLATION_GUIDE.md
2. Download dataset from Kaggle
3. Run model training
4. Initialize database
5. Start backend with: `python backend/app.py`

---

## 🎯 Quick Test Commands

After app is running, test it:

```bash
# Test 1: Health check
curl http://localhost:5000/api/health

# Test 2: Get languages
curl http://localhost:5000/api/languages

# Test 3: Get disease info (English)
curl "http://localhost:5000/api/diseases?language=en"

# Test 4: Get disease info (Hindi)
curl "http://localhost:5000/api/diseases?language=hi"
```

---

## 💡 Tips

- **Keep terminal open** while using the app
- **Use Ctrl+C** in terminal to stop the server
- **Refresh browser** if page doesn't load
- **Check terminal** for error messages if something fails
- **Use localhost** instead of IP address for local testing

---

## 📞 Support

If you encounter any issues:

1. Check the terminal output for error messages
2. Verify all files are in the correct location
3. Make sure Python 3.8+ is installed
4. Ensure no antivirus is blocking the connection
5. Try restarting the application

---

**🎉 That's it! You're ready to use the Orange Disease Detection System!**

For more information, see:
- README.md - Project overview
- INSTALLATION_GUIDE.md - Detailed setup
- DEPLOYMENT_GUIDE.md - Production deployment
- ARCHITECTURE_DIAGRAMS.md - System design
