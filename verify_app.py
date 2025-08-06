#!/usr/bin/env python3
"""
Script to verify the app bundle has the correct icon and structure.
"""

import os
import subprocess
import sys

def verify_app_bundle():
    """Verify the app bundle structure and icon."""
    app_path = "dist/FitBlock.app"
    
    if not os.path.exists(app_path):
        print("✗ App bundle not found: dist/FitBlock.app")
        return False
    
    print(f"✓ App bundle found: {app_path}")
    
    # Check app bundle structure
    contents_path = os.path.join(app_path, "Contents")
    if not os.path.exists(contents_path):
        print("✗ App bundle missing Contents directory")
        return False
    
    # Check Info.plist
    info_plist = os.path.join(contents_path, "Info.plist")
    if not os.path.exists(info_plist):
        print("✗ App bundle missing Info.plist")
        return False
    
    # Check executable
    macos_path = os.path.join(contents_path, "MacOS")
    if not os.path.exists(macos_path):
        print("✗ App bundle missing MacOS directory")
        return False
    
    executable = os.path.join(macos_path, "FitBlock")
    if not os.path.exists(executable):
        print("✗ App bundle missing FitBlock executable")
        return False
    
    print("✓ App bundle structure is correct")
    
    # Check if icon is included
    resources_path = os.path.join(contents_path, "Resources")
    if os.path.exists(resources_path):
        icon_in_resources = os.path.join(resources_path, "icon.icns")
        if os.path.exists(icon_in_resources):
            print("✓ Icon found in app bundle resources")
        else:
            print("⚠️  Icon not found in app bundle resources")
    
    # Check app icon using file command
    try:
        result = subprocess.run(["file", app_path], capture_output=True, text=True)
        if "Mach-O" in result.stdout:
            print("✓ App bundle is a valid macOS application")
        else:
            print("⚠️  App bundle may not be a valid macOS application")
    except Exception as e:
        print(f"⚠️  Could not verify app bundle type: {e}")
    
    # Check if icon is set in Info.plist
    try:
        result = subprocess.run([
            "defaults", "read", info_plist, "CFBundleIconFile"
        ], capture_output=True, text=True)
        if result.returncode == 0:
            icon_file = result.stdout.strip()
            print(f"✓ App icon set to: {icon_file}")
        else:
            print("⚠️  No icon specified in Info.plist")
    except Exception as e:
        print(f"⚠️  Could not read Info.plist: {e}")
    
    return True

if __name__ == "__main__":
    success = verify_app_bundle()
    if success:
        print("\n✓ App bundle verification completed!")
    else:
        print("\n✗ App bundle verification failed!")
    sys.exit(0 if success else 1) 