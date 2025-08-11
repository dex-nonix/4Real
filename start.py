#!/usr/bin/env python3
"""
4Real Music Application Startup Script
This script starts the nonix_mini_artist application
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def print_header():
    """Print application header"""
    print("🎵 Starting 4Real Music Application...")
    print("======================================")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    print("📦 Checking dependencies...")
    
    # Check for tkinter (GUI framework)
    try:
        import tkinter
        print("✅ tkinter available")
    except ImportError:
        print("❌ Error: tkinter not available")
        print("Please install tkinter for your system")
        return False
    
    # Check for other common dependencies
    try:
        import sqlite3
        print("✅ sqlite3 available")
    except ImportError:
        print("⚠️  sqlite3 not available")
    
    return True

def find_entry_point():
    """Find the main entry point for the application"""
    print("🔍 Looking for application entry point...")
    
    # Check for main.py in root
    if Path("main.py").exists():
        print("✅ Found main.py in root directory")
        return "main.py"
    
    # Check for app.py in UI directory
    ui_app_path = Path("src/nonix_mini_artist/ui/app.py")
    if ui_app_path.exists():
        print("✅ Found UI app.py")
        return str(ui_app_path)
    
    # Check for other potential entry points
    potential_files = [
        "app.py",
        "run.py",
        "main.py",
        "src/main.py"
    ]
    
    for file_path in potential_files:
        if Path(file_path).exists():
            print(f"✅ Found potential entry point: {file_path}")
            return file_path
    
    return None

def start_application(entry_point):
    """Start the application using the found entry point"""
    print(f"🚀 Launching application from: {entry_point}")
    print("")
    
    try:
        if entry_point == "main.py":
            # Import and run main.py
            spec = importlib.util.spec_from_file_location("main", "main.py")
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
        else:
            # Run the file directly
            subprocess.run([sys.executable, entry_point], check=True)
            
    except KeyboardInterrupt:
        print("\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Find entry point
    entry_point = find_entry_point()
    if not entry_point:
        print("❌ Error: Could not find application entry point")
        print("Available Python files:")
        
        # List Python files in current directory
        for py_file in Path(".").glob("*.py"):
            print(f"  - {py_file}")
        
        # List Python files in src directory
        src_path = Path("src")
        if src_path.exists():
            for py_file in src_path.rglob("*.py"):
                print(f"  - {py_file}")
        
        sys.exit(1)
    
    # Start the application
    success = start_application(entry_point)
    
    print("")
    if success:
        print("👋 Application closed successfully")
    else:
        print("💥 Application encountered an error")
        sys.exit(1)

if __name__ == "__main__":
    main()
