# Installation and Setup Guide
## Orange Disease Detection System

## Prerequisites

Before starting, ensure you have:
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **MySQL**: 5.7 or higher
- **Git**: Latest version
- **RAM**: Minimum 4 GB (8 GB recommended)
- **Storage**: 5 GB free space
- **Internet**: For downloading models and dependencies

## Step-by-Step Installation

### Step 1: Download and Install Required Software

#### 1.1 Install Python (if not already installed)
```bash
# Windows
# Download from https://www.python.org/downloads/
# Run installer, check "Add Python to PATH"

# macOS
brew install python3

# Linux (Ubuntu)
sudo apt-get update
sudo apt-get install python3 python3-pip
```

Verify Python installation:
```bash
python --version  # Should show 3.8 or higher
```

#### 1.2 Install MySQL (if not already installed)
```bash
# Windows
# Download from https://dev.mysql.com/downloads/installer/
# Run installer, setup MySQL Server

# macOS
brew install mysql

# Linux (Ubuntu)
sudo apt-get install mysql-server
```

Verify MySQL installation:
```bash
mysql --version
```

Start MySQL service:
```bash
# Windows (from Services or)
net start MySQL80  # Adjust version number as needed

# macOS
brew services start mysql

# Linux
sudo service mysql start
```

### Step 2: Clone or Download Project

```bash
# If using Git (recommended)
git clone <your-repository-url>
cd Orange_Disease_Project

# Or download ZIP and extract
# Then navigate to project folder
```

### Step 3: Create Python Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` prefix in terminal after activation.

### Step 4: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This will take 5-10 minutes depending on internet speed.

### Step 5: Configure Database

#### 5.1 Create Database User (Optional but Recommended)
```sql
# Login to MySQL
mysql -u root -p

# Create new user
CREATE USER 'orange_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON orange_disease_db.* TO 'orange_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 5.2 Update Database Credentials

Edit `database/db_setup.py`:
```python
db_manager = DatabaseManager(
    host='localhost',
    user='root',        # Change if using different user
    password='',        # Enter your MySQL password
    database='orange_disease_db'
)
```

#### 5.3 Initialize Database

```bash
cd database
python db_setup.py
```

You should see output:
```
✓ Connected to MySQL server
✓ Database 'orange_disease_db' ready
✓ Users table created successfully
✓ Predictions table created successfully
✓ Disease Info table created successfully
✓ Inserted 5 disease records into database
```

### Step 6: Prepare Dataset

#### 6.1 Download Dataset

1. Visit: https://www.kaggle.com/datasets/oriekhidas/orange-disease
2. Download the dataset
3. Extract to `dataset/` folder

#### 6.2 Organize Dataset

Structure should be:
```
dataset/
├── Citrus Canker/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── Black Spot/
├── Citrus Greening/
├── Leaf Miner/
└── Healthy/
```

If dataset has different structure, rename folders or adjust preprocessing script.

#### 6.3 Preprocess Dataset

```bash
cd training
python data_preprocessing.py
```

This will:
- Load all images
- Display class distribution
- Resize to 224×224
- Normalize to [0,1]
- Perform train-test split (70-15-15)
- Save to `dataset/preprocessed/`

Expected output:
```
Loading images from directory...
Found disease classes: ['Citrus Canker', 'Black Spot', ...]
Total images loaded: 500
Training set size: 350
Validation set size: 75
Test set size: 75
```

### Step 7: Train Models

```bash
cd training
python model_trainer.py
```

This will:
- Build MobileNetV2, ResNet50, EfficientNetB0
- Train all three models (18-22 minutes total)
- Evaluate on test set
- Compare metrics
- Select best model (EfficientNetB0)
- Save models to `models/` folder
- Generate comparison report

Expected training time: 20-30 minutes on CPU, 5-10 minutes on GPU.

### Step 8: Update Backend Configuration

Edit `backend/app.py`:

```python
# Line ~50 - API Configuration
app.config['SECRET_KEY'] = 'your-very-secure-secret-key-change-this'

# Line ~80 - Database Configuration
db_manager = DatabaseManager(
    host='localhost',
    user='root',        # Your MySQL user
    password='',        # Your MySQL password
    database='orange_disease_db'
)
```

### Step 9: Run Backend Server

```bash
cd backend
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000/
 * Use CTRL+C to exit
✓ Model loaded successfully
✓ Database connected
```

Backend is now running and ready for requests.

### Step 10: Access Frontend

Open browser and visit:
```
http://localhost:5000/
```

Or directly open:
```
templates/index.html
```

## Verification & Testing

### Test 1: Check API Health
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "timestamp": "2024-05-23T10:30:00"
}
```

### Test 2: Get Diseases List
```bash
curl http://localhost:5000/api/diseases?language=en
```

### Test 3: Test Prediction with Image
```bash
curl -X POST -F "image=@test_image.jpg" \
  -F "language=en" \
  http://localhost:5000/api/predict
```

### Test 4: Get Statistics
```bash
curl http://localhost:5000/api/statistics
```

## Common Issues and Solutions

### Issue 1: "ModuleNotFoundError: No module named 'tensorflow'"
**Solution**:
```bash
# Make sure virtual environment is activated
pip install tensorflow==2.13.0

# If still fails, try upgrading pip
pip install --upgrade pip setuptools
pip install tensorflow==2.13.0
```

### Issue 2: "Error: MySQL connection failed"
**Solution**:
```bash
# Check MySQL is running
sudo service mysql status

# Start MySQL
sudo service mysql start

# Verify credentials in db_setup.py
python database/db_setup.py
```

### Issue 3: "Model not found at ../models/best_model.h5"
**Solution**:
```bash
# Ensure model training completed
cd training
python model_trainer.py

# Check models folder has files
ls -la models/
```

### Issue 4: "Port 5000 already in use"
**Solution**:
```bash
# Change port in app.py (last line)
app.run(host='0.0.0.0', port=5001)

# Or kill process using port
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

### Issue 5: "CORS error in browser"
**Solution**:
```python
# CORS already enabled in app.py (line ~12)
# If issues persist, update CORS configuration:
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

## File Structure After Setup

```
Orange_Disease_Project/
├── dataset/
│   ├── Citrus Canker/
│   ├── Black Spot/
│   ├── Citrus Greening/
│   ├── Leaf Miner/
│   ├── Healthy/
│   └── preprocessed/
│       ├── images.npy
│       ├── labels.npy
│       └── class_mapping.json
│
├── models/
│   ├── MobileNetV2_best.h5
│   ├── MobileNetV2_final.h5
│   ├── ResNet50_best.h5
│   ├── ResNet50_final.h5
│   ├── EfficientNetB0_best.h5
│   ├── EfficientNetB0_final.h5
│   └── best_model.h5  ← Used for predictions
│
├── training/
│   ├── __pycache__/
│   ├── data_preprocessing.py
│   └── model_trainer.py
│
├── backend/
│   ├── __pycache__/
│   ├── app.py
│   ├── gradcam_explainer.py
│   └── requirements.txt
│
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   └── uploads/  ← User uploaded images
│
├── templates/
│   └── index.html
│
├── database/
│   ├── __pycache__/
│   └── db_setup.py
│
├── reports/
│   ├── PROJECT_SYNOPSIS.md
│   ├── VIVA_QUESTIONS_ANSWERS.md
│   ├── model_comparison.json
│   ├── confusion_matrices.png
│   └── training_history.png
│
├── screenshots/  ← Project screenshots
│
├── venv/  ← Virtual environment
│
├── requirements.txt
├── README.md
└── .gitignore
```

## Performance Optimization (Optional)

### For Faster Predictions (GPU Support)
```bash
# Install CUDA (for NVIDIA GPUs)
pip install tensorflow-gpu

# Or for specific CUDA version
pip install tensorflow==2.13.0 -f https://storage.googleapis.com/tensorflow/gpu/tensorflow-2.13.0-cp310-cp310-linux_x86_64.whl
```

### For Model Optimization
```python
# In backend/app.py, after loading model
from tensorflow.lite.python import lite
import tensorflow as tf

# Convert to TensorFlow Lite (reduces size by 4x)
converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
tflite_model = converter.convert()
```

### For Production Deployment
```bash
# Install Gunicorn for production server
pip install gunicorn

# Run production server with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Development Workflow

### For Making Changes

1. **Modify code** in your editor
2. **Reload Flask** (development mode auto-reloads)
3. **Test changes** in browser (refresh page)
4. **Monitor logs** in terminal

### For Adding New Disease

1. Add new class folder in `dataset/`
2. Add images to folder
3. Re-run preprocessing
4. Re-train models
5. Update `disease_classes` in `app.py`
6. Add disease info to database

## Backup and Restore

### Backup Database
```bash
mysqldump -u root -p orange_disease_db > backup_orange_db.sql
```

### Restore Database
```bash
mysql -u root -p orange_disease_db < backup_orange_db.sql
```

### Backup Models
```bash
# Copy models folder to external storage
cp -r models/ /backup/models_backup/
```

## Uninstallation

If you want to remove the project:

```bash
# Deactivate virtual environment
deactivate

# Delete project folder
rm -rf Orange_Disease_Project

# Drop MySQL database (if needed)
mysql -u root -p -e "DROP DATABASE orange_disease_db;"
```

## Support and Troubleshooting

**For issues or help:**
1. Check error messages carefully
2. Google the error message
3. Check requirements match Python version
4. Verify all dependencies installed
5. Check internet connection
6. Look at GitHub issues
7. Contact project maintainers

## Next Steps

After successful installation:

1. ✅ Test the system with sample images
2. ✅ Collect more training data if needed
3. ✅ Fine-tune model hyperparameters
4. ✅ Deploy to production server
5. ✅ Monitor prediction accuracy
6. ✅ Gather farmer feedback
7. ✅ Implement improvements

---

**Congratulations!** Your Orange Disease Detection System is ready! 🍊
