"""
Config command implementation.
"""

import json
from datetime import datetime
from cli.core import print_section_header, print_status_bar, print_colored, Colors
from configurations.config import BROWSER_OPTIONS, LLM_PROVIDER, CURRENT_LLM_CONFIG
from cli.utils import get_version

def command_config(args):
    """View and manage configuration."""
    print_section_header("Configuration Management")
    
    if args.show:
        show_configuration()
    elif args.set:
        key, value = args.set
        set_configuration(key, value)
    elif args.get:
        get_configuration(args.get)
    elif args.reset:
        reset_configuration()
    elif args.export:
        export_configuration(args.export)
    elif getattr(args, 'import', None):
        import_configuration(getattr(args, 'import'))
    else:
        show_configuration()
    
    return True

def show_configuration():
    """Show current configuration with colors."""
    print_colored("📋 Current Configuration:", Colors.BRIGHT_CYAN, Colors.BOLD)
    
    api_status = "✅ Set" if CURRENT_LLM_CONFIG.get("api_key") else "❌ Not set"
    api_color = Colors.BRIGHT_GREEN if CURRENT_LLM_CONFIG.get("api_key") else Colors.BRIGHT_RED
    
    config = {
        f"{LLM_PROVIDER.upper()} API Key": (api_status, api_color),
        "LLM Provider": (LLM_PROVIDER.upper(), Colors.BRIGHT_BLUE),
        "Model": (CURRENT_LLM_CONFIG.get("model", "Unknown"), Colors.BRIGHT_MAGENTA),
        "Browser Options": (None, None),  # Special handling for dict
    }
    
    for key, (value, color) in config.items():
        if key == "Browser Options":
            print_colored(f"  {key}:", Colors.BRIGHT_YELLOW)
            for sub_key, sub_value in BROWSER_OPTIONS.items():
                print_colored(f"    {sub_key}: {sub_value}", Colors.WHITE)
        else:
            print_colored(f"  {key}: ", Colors.BRIGHT_WHITE, end="")
            print_colored(value, color)

def set_configuration(key: str, value: str):
    """Set configuration value."""
    print_status_bar(f"Setting {key} = {value}", "INFO")
    print_status_bar("Configuration setting not yet implemented", "WARNING")

def get_configuration(key: str):
    """Get configuration value."""
    print_status_bar(f"Getting configuration for: {key}", "INFO")
    print_status_bar("Configuration getting not yet implemented", "WARNING")

def reset_configuration():
    """Reset configuration to defaults."""
    print_status_bar("Resetting configuration to defaults...", "PROGRESS")
    print_status_bar("Configuration reset not yet implemented", "WARNING")

def export_configuration(filename: str):
    """Export configuration to file."""
    print_status_bar(f"Exporting configuration to {filename}...", "PROGRESS")
    
    config = {
        "browser_options": BROWSER_OPTIONS,
        "version": get_version(),
        "export_timestamp": datetime.now().isoformat()
    }
    
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=2)
        print_status_bar("Configuration exported successfully", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to export configuration: {str(e)}", "ERROR")

def import_configuration(filename: str):
    """Import configuration from file."""
    print_status_bar(f"Importing configuration from {filename}...", "PROGRESS")
    print_status_bar("Configuration import not yet implemented", "WARNING")
