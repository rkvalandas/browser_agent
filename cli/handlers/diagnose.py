"""
Diagnostics command implementation.
"""

import os
import sys
import json
import urllib.request
from datetime import datetime
from pathlib import Path
from cli.core import print_section_header, print_status_bar, print_colored, Colors
from cli.utils import get_system_info, count_chrome_processes, check_dependencies, list_debug_profiles, list_temp_profiles
from configurations.config import BROWSER_OPTIONS, CURRENT_LLM_CONFIG

def command_diagnose(args):
    """Run system diagnostics."""
    print_section_header("System Diagnostics")
    
    if args.full or not any([args.chrome, args.deps, args.config, args.network]):
        # Run all diagnostics
        run_all_diagnostics()
    else:
        if args.chrome:
            diagnose_chrome()
        if args.deps:
            diagnose_dependencies()
        if args.config:
            diagnose_configuration()
        if args.network:
            diagnose_network()
    
    if args.export:
        export_diagnostic_report(args.export)
    
    return True

def run_all_diagnostics():
    """Run complete diagnostic suite."""
    print_status_bar("Running comprehensive diagnostics...", "PROGRESS")
    
    diagnose_chrome()
    diagnose_dependencies()
    diagnose_configuration()
    diagnose_network()
    
    print_status_bar("Diagnostics complete", "SUCCESS")

def diagnose_chrome():
    """Diagnose Chrome installation and processes with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🌐 Chrome Diagnostics:{Colors.RESET}")
    
    # Check Chrome processes
    chrome_count = count_chrome_processes()
    print_colored(f"  • Running Chrome processes: {chrome_count}", Colors.BRIGHT_CYAN)
    
    # Check for Chrome executable
    chrome_paths = []
    if sys.platform == "darwin":
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary"
        ]
    elif sys.platform == "linux":
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium"
        ]
    else:  # Windows
        chrome_paths = [
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            print_colored(f"  • Chrome executable found: {path}", Colors.BRIGHT_GREEN)
            chrome_found = True
            break
    
    if not chrome_found:
        print_colored("  • ⚠️  Chrome executable not found in standard locations", Colors.BRIGHT_YELLOW)
    
    # Test debug port
    if test_chrome_connection(9222):
        print_colored("  • ✅ Debug port 9222 accessible", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ Debug port 9222 not accessible", Colors.BRIGHT_RED)

def diagnose_dependencies():
    """Diagnose Python dependencies with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🐍 Python Dependencies:{Colors.RESET}")
    
    deps = check_dependencies()
    for dep, version in deps.items():
        if "❌" in str(version):
            print_colored(f"  • ❌ {dep}: Not installed", Colors.BRIGHT_RED)
        else:
            print_colored(f"  • ✅ {dep}: {version}", Colors.BRIGHT_GREEN)

def diagnose_configuration():
    """Diagnose configuration issues with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}⚙️  Configuration:{Colors.RESET}")
    
    # Check API key
    if CURRENT_LLM_CONFIG.get("api_key"):
        print_colored("  • ✅ API key configured", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ API key not configured", Colors.BRIGHT_RED)
    
    # Check .env file
    env_file = Path(".env")
    if env_file.exists():
        print_colored("  • ✅ .env file found", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ⚠️  .env file not found", Colors.BRIGHT_YELLOW)
    
    # Check browser options
    headless_status = BROWSER_OPTIONS.get('headless', False)
    headless_color = Colors.BRIGHT_YELLOW if headless_status else Colors.BRIGHT_GREEN
    print_colored(f"  • Browser headless: {headless_status}", headless_color)
    
    channel = BROWSER_OPTIONS.get('channel', 'unknown')
    print_colored(f"  • Browser channel: {channel}", Colors.BRIGHT_CYAN)

def diagnose_network():
    """Diagnose network connectivity with colors."""
    print(f"\n{Colors.BRIGHT_BLUE}🌐 Network Connectivity:{Colors.RESET}")
    
    # Test localhost connection
    if test_chrome_connection(9222):
        print_colored("  • ✅ localhost:9222 accessible", Colors.BRIGHT_GREEN)
    else:
        print_colored("  • ❌ localhost:9222 not accessible", Colors.BRIGHT_RED)
    
    # Test internet connectivity
    try:
        with urllib.request.urlopen("https://www.google.com", timeout=5):
            print_colored("  • ✅ Internet connectivity available", Colors.BRIGHT_GREEN)
    except:
        print_colored("  • ❌ Internet connectivity issues", Colors.BRIGHT_RED)

def test_chrome_connection(port: int, host: str = "localhost", timeout: int = 10) -> bool:
    """Test if Chrome debug port is accessible."""
    try:
        url = f"http://{host}:{port}/json/version"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
            return True
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return False

def export_diagnostic_report(filename: str):
    """Export diagnostic report to file."""
    print_status_bar(f"Exporting diagnostic report to {filename}...", "PROGRESS")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_info": get_system_info(),
        "dependencies": check_dependencies(),
        "chrome_processes": count_chrome_processes(),
        "debug_port_accessible": test_chrome_connection(9222),
        "profiles": {
            "debug": list_debug_profiles(),
            "temp": list_temp_profiles()
        }
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print_status_bar(f"Report exported successfully", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to export report: {str(e)}", "ERROR")
