#!/usr/bin/env python3
"""
Test script to validate the webapp structure and basic functionality
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} NOT FOUND")
        return False

def check_directory_exists(dirpath, description):
    """Check if a directory exists"""
    if Path(dirpath).is_dir():
        print(f"✓ {description}: {dirpath}")
        return True
    else:
        print(f"✗ {description}: {dirpath} NOT FOUND")
        return False

def main():
    print("🧪 Testing Pi Chat Web Application Structure")
    print("=" * 50)
    
    webapp_dir = Path(__file__).parent
    os.chdir(webapp_dir)
    
    all_checks_passed = True
    
    # Check core files
    print("\n📁 Checking core files...")
    all_checks_passed &= check_file_exists("app.py", "Main application")
    all_checks_passed &= check_file_exists("requirements.txt", "Dependencies")
    all_checks_passed &= check_file_exists("Dockerfile", "Docker configuration")
    all_checks_passed &= check_file_exists(".env.example", "Environment template")
    all_checks_passed &= check_file_exists("README.md", "Documentation")
    all_checks_passed &= check_file_exists("deploy.sh", "Deployment script")
    
    # Check directories
    print("\n📂 Checking directories...")
    all_checks_passed &= check_directory_exists("templates", "Templates directory")
    all_checks_passed &= check_directory_exists("static", "Static files directory")
    
    # Check frontend files
    print("\n🎨 Checking frontend files...")
    all_checks_passed &= check_file_exists("templates/index.html", "Main HTML template")
    all_checks_passed &= check_file_exists("static/style.css", "CSS stylesheet")
    all_checks_passed &= check_file_exists("static/script.js", "JavaScript")
    
    # Check Python syntax
    print("\n🐍 Validating Python syntax...")
    try:
        import py_compile
        py_compile.compile("app.py", doraise=True)
        print("✓ app.py syntax is valid")
    except py_compile.PyCompileError as e:
        print(f"✗ Python syntax error in app.py: {e}")
        all_checks_passed = False
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    with open("requirements.txt", "r") as f:
        dependencies = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    print(f"✓ Found {len(dependencies)} dependencies:")
    for dep in dependencies:
        print(f"  - {dep}")
    
    # Check environment variables documented
    print("\n🔐 Checking environment variable documentation...")
    with open(".env.example", "r") as f:
        env_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
    print(f"✓ Found {len(env_lines)} environment variables documented")
    
    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("✅ All checks passed!")
        return 0
    else:
        print("❌ Some checks failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
