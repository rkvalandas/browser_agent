"""
System utilities and information gathering.
"""

import os
import sys
import subprocess
import tempfile
import json
from pathlib import Path
from typing import Dict, List
from configurations.config import BROWSER_OPTIONS, LLM_PROVIDER, CURRENT_LLM_CONFIG

def get_version():
    """Get the application version."""
    return "1.0.0"

def get_system_info():
    """Get system information for diagnostics."""
    return {
        "version": get_version(),
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "current_directory": os.getcwd(),
        "chrome_processes": count_chrome_processes(),
        "debug_profiles": list_debug_profiles(),
        "temp_profiles": list_temp_profiles(),
        "api_key_configured": bool(CURRENT_LLM_CONFIG.get("api_key")),
        "browser_options": BROWSER_OPTIONS
    }

def count_chrome_processes():
    """Count running Chrome processes."""
    try:
        if sys.platform == "darwin":  # macOS
            result = subprocess.run(["pgrep", "-c", "Chrome"], capture_output=True, text=True)
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        elif sys.platform == "linux":
            result = subprocess.run(["pgrep", "-c", "chrome"], capture_output=True, text=True)
            return int(result.stdout.strip()) if result.returncode == 0 else 0
        else:  # Windows
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq chrome.exe"], capture_output=True, text=True)
            return len([line for line in result.stdout.split('\n') if 'chrome.exe' in line])
    except:
        return 0

def list_debug_profiles():
    """List available debug profiles."""
    profiles = []
    if sys.platform == "darwin":
        debug_dir = Path.home() / "Library" / "Application Support" / "Google" / "Chrome" / "Debug"
    elif sys.platform == "linux":
        debug_dir = Path.home() / ".config" / "google-chrome" / "Debug"
    else:
        debug_dir = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Debug"
    
    if debug_dir.exists():
        for item in debug_dir.iterdir():
            if item.is_dir():
                profiles.append(str(item))
    return profiles

def list_temp_profiles():
    """List temporary profiles in system temp directory."""
    temp_dir = Path(tempfile.gettempdir())
    temp_profiles = []
    for item in temp_dir.glob("chrome_temp_*"):
        if item.is_dir():
            temp_profiles.append(str(item))
    return temp_profiles

def check_dependencies():
    """Check if required dependencies are installed."""
    deps = {}
    
    try:
        import playwright
        deps["playwright"] = getattr(playwright, '__version__', 'unknown')
    except ImportError:
        deps["playwright"] = "❌ Not installed"
    
    try:
        import openai
        deps["openai"] = getattr(openai, '__version__', 'unknown')
    except ImportError:
        deps["openai"] = "❌ Not installed"
    
    try:
        import groq
        deps["groq"] = getattr(groq, '__version__', 'unknown')
    except ImportError:
        deps["groq"] = "❌ Not installed"
    
    return deps

def validate_environment():
    """Validate that the environment is properly configured."""
    issues = []
    
    if not CURRENT_LLM_CONFIG.get("api_key"):
        issues.append(f"{LLM_PROVIDER.upper()} API key is not configured (set {LLM_PROVIDER.upper()}_API_KEY environment variable)")
    
    deps = check_dependencies()
    for dep, version in deps.items():
        if "❌" in str(version):
            issues.append(f"Missing dependency: {dep}")
    
    return issues
