#!/usr/bin/env python3
"""
Orange Disease Detection System - Startup Script
Handles environment setup and application launch
"""

import os
import sys
import subprocess
import platform

def main():
    print("\n" + "="*70)
    print(" 🍊 ORANGE DISEASE DETECTION SYSTEM - STARTUP")
    print("="*70 + "\n")
    
    # Get current directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"📁 Project Root: {project_root}\n")
    
    # Step 1: Check Python version
    print("✓ Step 1: Checking Python version...")
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print(f"  ✓ Python {python_version.major}.{python_version.minor} detected\n")
    else:
        print(f"  ✗ Python 3.8+ required (found {python_version.major}.{python_version.minor})")
        sys.exit(1)
    
    # Step 2: Create/activate virtual environment
    print("✓ Step 2: Setting up virtual environment...")
    venv_path = os.path.join(project_root, 'venv')
    
    if not os.path.exists(venv_path):
        print(f"  Creating virtual environment at {venv_path}...")
        subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
        print("  ✓ Virtual environment created\n")
    else:
        print("  ✓ Virtual environment already exists\n")
    
    # Step 3: Install requirements
    print("✓ Step 3: Installing dependencies...")
    requirements_file = os.path.join(project_root, 'requirements.txt')
    
    if platform.system() == 'Windows':
        pip_exe = os.path.join(venv_path, 'Scripts', 'pip')
        python_exe = os.path.join(venv_path, 'Scripts', 'python')
    else:
        pip_exe = os.path.join(venv_path, 'bin', 'pip')
        python_exe = os.path.join(venv_path, 'bin', 'python')
    
    print(f"  Installing from {requirements_file}...")
    result = subprocess.run([pip_exe, 'install', '-r', requirements_file])
    if result.returncode == 0:
        print("  ✓ Dependencies installed\n")
    else:
        print("  ⚠ Warning: Some dependencies may not have installed properly\n")
    
    # Step 4: Create necessary directories
    print("✓ Step 4: Creating necessary directories...")
    dirs_to_create = [
        os.path.join(project_root, 'dataset', 'preprocessed'),
        os.path.join(project_root, 'models'),
        os.path.join(project_root, 'static', 'uploads'),
        os.path.join(project_root, 'logs')
    ]
    
    for dir_path in dirs_to_create:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✓ {dir_path}")
    print()
    
    # Step 5: Launch the backend
    print("✓ Step 5: Starting Flask backend...\n")
    print("="*70)
    print(" 🚀 STARTING APPLICATION")
    print("="*70)
    print("\n  🌐 Web Interface: http://localhost:5000/")
    print("  📡 API Endpoint: http://localhost:5000/api/")
    print("  ⚕️  Health Check: http://localhost:5000/api/health")
    print("\n  Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    # Change to backend directory and run the app
    backend_path = os.path.join(project_root, 'backend')
    os.chdir(backend_path)
    
    # Run Flask app
    subprocess.run([python_exe, 'app.py'])

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped gracefully")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
