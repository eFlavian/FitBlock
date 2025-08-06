#!/usr/bin/env python3
"""
Build script to create a macOS app bundle from the FitBlock.
"""

import os
import subprocess
import sys
import shutil

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    print("Building FitBlock macOS App...")
    print("=" * 50)
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Installing...")
        if not run_command([sys.executable, "-m", "pip", "install", "pyinstaller"], "Installing PyInstaller"):
            return False
    
    if os.path.exists("dist"):
        print("Cleaning previous build...")
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    for spec_file in ["FitBlock.spec", "TrainingBlocker.spec"]:
        if os.path.exists(spec_file + ".spec"):
            print(f"Removing old spec file: {spec_file}.spec")
            os.remove(spec_file + ".spec")
    
    if os.path.exists("icon.icns"):
        print("✓ Icon file found: icon.icns")
    else:
        print("⚠️  Icon file not found: icon.icns (app will use default icon)")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--clean",                      
        "--distpath=dist",               
        "--workpath=build",              
        "FitBlock.spec"                  
    ]
    
    pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if cmd is not None]
    
    if not run_command(pyinstaller_cmd, "Building app with PyInstaller"):
        return False
    
    app_path = "dist/FitBlock.app"
    if os.path.exists(app_path):
        print(f"✓ App created successfully at: {app_path}")
        
        launcher_script = """#!/bin/bash
# Launcher script for FitBlock
cd "$(dirname "$0")"
open FitBlock.app
"""
        
        with open("dist/launch_fitblock.sh", "w") as f:
            f.write(launcher_script)
        os.chmod("dist/launch_fitblock.sh", 0o755)
        
        print("\n" + "=" * 50)
        print("BUILD COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        print(f"App location: {os.path.abspath(app_path)}")
        print(f"Launcher script: {os.path.abspath('dist/launch_fitblock.sh')}")
        print("\nTo run the app:")
        print("1. Double-click the FitBlock.app in the dist folder")
        print("2. Or run: ./dist/launch_fitblock.sh")
        print("3. Or run: open dist/FitBlock.app")
        print("\nNote: The app will request administrator privileges on first run.")
        print("You may need to grant Accessibility permissions in System Preferences.")
        print("The app runs as a background app (no dock icon) - look for it in the menu bar.")
        
        return True
    else:
        print("✗ App was not created successfully")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 