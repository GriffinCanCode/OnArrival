#!/usr/bin/env python3
"""
Helper script to start the OnArrival backend server on port 5001 for frontend development.
Run this from the frontend directory to ensure backend compatibility.
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the project root directory (parent of frontend)
    frontend_dir = Path(__file__).parent
    project_root = frontend_dir.parent
    src_dir = project_root / "src"
    web_app_path = src_dir / "web_app.py"
    
    # Check if web_app.py exists
    if not web_app_path.exists():
        print(f"❌ Error: Could not find {web_app_path}")
        print("   Make sure you're running this from the frontend directory")
        print("   and that the OnArrival backend exists in ../src/")
        sys.exit(1)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment doesn't appear to be activated")
        print("   Consider running: source ../.venv/bin/activate")
        print()
    
    print("🚀 Starting OnArrival backend server on port 5001...")
    print("   This will make the backend accessible to the React frontend")
    print("   Press Ctrl+C to stop the server")
    print()
    
    try:
        # Change to project root and run the web app on port 5001
        os.chdir(project_root)
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root)
        
        subprocess.run([
            sys.executable, 
            str(web_app_path), 
            "--port", "5001",
            "--host", "0.0.0.0"
        ], env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n❌ Error: Python interpreter not found")
        print("   Make sure Python is installed and the virtual environment is activated")
        sys.exit(1)

if __name__ == "__main__":
    main() 