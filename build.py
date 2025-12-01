#!/usr/bin/env python3
# build.py
# Build script for WSC Decompiler GUI and CLI

import os
import sys
import subprocess
import shutil
from pathlib import Path


def create_app_icon():
    """Create a simple app icon if it doesn't exist."""
    icon_path = Path("assets/app.ico")
    if not icon_path.exists():
        print("Creating placeholder icon directory...")
        icon_path.parent.mkdir(exist_ok=True)
        # Create a simple placeholder file
        icon_path.touch()
        print("Note: Consider adding a proper .ico file to assets/app.ico")


def build_executable(target_file, name, icon=None, console=True):
    """Build an executable using PyInstaller."""
    cmd = ["pyinstaller", target_file, "--onefile"]

    if not console:
        cmd.append("--noconsole")

    if icon and Path(icon).exists():
        cmd.extend(["--icon", icon])

    cmd.extend(["--name", name])

    print(f"Building {name}...")
    print(f"Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {name} built successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build {name}:")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it:")
        print("   pip install pyinstaller")
        return False


def main():
    """Main build function."""
    print("WSC Decompiler Build Script")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("decompiler.py").exists():
        print("❌ Error: decompiler.py not found. Please run this script from the wsc-gui directory.")
        return 1

    # Create icon directory
    create_app_icon()

    # Check for PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ PyInstaller not found. Please install it:")
        print("   pip install pyinstaller")
        return 1

    success_count = 0
    total_builds = 3

    # Build CLI version (always with console)
    if build_executable("cli.py", "wsc-cli", console=True):
        success_count += 1

    # Build Simple GUI (if tkinter is available)
    try:
        import tkinter
        if build_executable("gui_simple.py", "wsc-gui-simple", console=False, icon="assets/app.ico"):
            success_count += 1
    except ImportError:
        print("⚠️  tkinter not available, skipping GUI build")
        total_builds -= 1

    # Build Full GUI (if tkinterdnd2 is available)
    try:
        import tkinterdnd2
        if build_executable("gui.py", "wsc-gui", console=False, icon="assets/app.ico"):
            success_count += 1
    except ImportError:
        print("⚠️  tkinterdnd2 not available, skipping full GUI build")
        total_builds -= 1

    # Summary
    print("\n" + "=" * 40)
    print(f"Build Summary: {success_count}/{total_builds} successful")

    if success_count == total_builds:
        print("🎉 All builds completed successfully!")
        print("\nExecutables are located in the 'dist/' directory:")

        dist_dir = Path("dist")
        if dist_dir.exists():
            for exe in dist_dir.iterdir():
                if exe.is_file():
                    print(f"  - {exe.name}")

        return 0
    else:
        print("⚠️  Some builds failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())