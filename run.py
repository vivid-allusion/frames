#!/usr/bin/env python3
"""
Convenience wrapper to run the Image-to-Image tool.
Automatically handles complete environment setup - zero manual steps required.

This script:
1. Creates virtual environment if it doesn't exist (using Python 3.12)
2. Installs/updates dependencies from requirements.txt
3. Runs the main entry point

Usage: python3 run.py [args]
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def find_python_executable():
    """Find best Python executable (prefer 3.12 for compatibility)."""
    # Try to find Python 3.12 specifically (best compatibility with replicate)
    for cmd in ["python3.12", "python3.11", "python3.10", "python3", sys.executable]:
        python_path = shutil.which(cmd)
        if python_path:
            return python_path

    return sys.executable  # Fallback to current Python


def find_or_create_venv():
    """Find existing venv or create a new one."""
    script_dir = Path(__file__).parent

    # Check for existing venvs (prioritize venv over venv_new)
    venv = script_dir / "venv"
    venv_new = script_dir / "venv_new"

    if venv.exists():
        return venv

    if venv_new.exists():
        return venv_new

    # No venv found - create one with Python 3.12 if available
    print("📦 No virtual environment found - creating one...")

    python_exec = find_python_executable()
    print(f"Using Python: {python_exec}")
    print(f"Creating venv at: {venv}")

    try:
        subprocess.run(
            [python_exec, "-m", "venv", str(venv)], check=True, capture_output=True
        )
        print("✅ Virtual environment created successfully")
        return venv
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        print(f"Error output: {e.stderr.decode()}")
        sys.exit(1)


def get_python_executable(venv_path):
    """Get the Python executable path for the venv."""
    if sys.platform == "win32":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        print(f"❌ Error: Python executable not found at {python_exe}")
        sys.exit(1)

    return python_exe


def install_dependencies(python_exe, requirements_file):
    """Install or update dependencies from requirements.txt."""
    if not requirements_file.exists():
        print(
            f"⚠️  Warning: {requirements_file} not found - skipping dependency installation"
        )
        return

    print("📦 Installing/updating dependencies from requirements.txt...")

    try:
        # Upgrade pip quietly
        subprocess.run(
            [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )

        # Install requirements quietly
        subprocess.run(
            [
                str(python_exe),
                "-m",
                "pip",
                "install",
                "-q",
                "-r",
                str(requirements_file),
            ],
            check=True,
            capture_output=True,
        )

        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr.decode()}")
        sys.exit(1)


def main():
    """Execute the main program with complete environment setup."""
    script_dir = Path(__file__).parent
    requirements_file = script_dir / "requirements.txt"

    # Step 1: Find or create virtual environment
    venv_path = find_or_create_venv()

    # Step 2: Get Python executable
    python_exe = get_python_executable(venv_path)

    # Step 3: Install/update dependencies
    install_dependencies(python_exe, requirements_file)

    # Step 4: Run the main module
    print()  # Blank line before script output
    cmd = [str(python_exe), "-m", "src.main"] + sys.argv[1:]

    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error running command: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
