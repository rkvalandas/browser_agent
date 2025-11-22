"""
Keyboard controller for browser interactions related to typing and keyboard events.
"""

import re
import time
import random
from agent.tools import tool

# Global variable to store the page
page = None

def initialize(browser_page):
    """Initialize the keyboard controller."""
    global page
    page = browser_page

@tool
def keyboard_action(input_text) -> str:
    """
    Simulates keyboard shortcuts and special keys (not for typing text).
    
    Input (input_text) - Key commands:
    - Special keys: "enter", "tab", "escape", "up", "down", "f5"
    - Combinations: "ctrl+a", "shift+tab", "ctrl+c", "cmd+v"
    - Sequences: "tab, enter" (comma-separated)
    
    Returns: Confirmation of action or error message.
    """
    try:
        # Check if this is a special key command
        special_keys = {
            # Basic navigation keys
            "enter": "Enter",
            "tab": "Tab",
            "shift+tab": "Shift+Tab",
            "backspace": "Backspace",
            "escape": "Escape", "esc": "Escape",
            "delete": "Delete", "del": "Delete",
            "space": " ",
            
            # Arrow keys
            "up": "ArrowUp",
            "down": "ArrowDown",
            "left": "ArrowLeft",
            "right": "ArrowRight",
            
            # Common shortcuts
            "ctrl+a": "Control+a", "cmd+a": "Meta+a",
            "ctrl+c": "Control+c", "cmd+c": "Meta+c",
            "ctrl+v": "Control+v", "cmd+v": "Meta+v",
            "ctrl+x": "Control+x", "cmd+x": "Meta+x",
            "ctrl+z": "Control+z", "cmd+z": "Meta+z",
            "ctrl+y": "Control+y", "cmd+y": "Meta+y",
            "ctrl+f": "Control+f", "cmd+f": "Meta+f",
            
            # Function keys
            "f1": "F1", "f2": "F2", "f3": "F3", "f4": "F4",
            "f5": "F5", "f6": "F6", "f7": "F7", "f8": "F8",
            "f9": "F9", "f10": "F10", "f11": "F11", "f12": "F12",
            
            # Navigation shortcuts
            "home": "Home",
            "end": "End",
            "pageup": "PageUp",
            "pagedown": "PageDown",
            
            # Special combinations
            "alt+tab": "Alt+Tab",
            "ctrl+enter": "Control+Enter", "cmd+enter": "Meta+Enter",
            "ctrl+home": "Control+Home", "cmd+home": "Meta+Home",
            "ctrl+end": "Control+End", "cmd+end": "Meta+End",
            
            # Web-specific
            "ctrl+t": "Control+t", "cmd+t": "Meta+t",  # New tab
            "ctrl+w": "Control+w", "cmd+w": "Meta+w",  # Close tab
            "ctrl+r": "Control+r", "cmd+r": "Meta+r",  # Reload
        }
        
        # Clean input
        if isinstance(input_text, str):
            input_text = input_text.strip("'\"").strip()
        
        # Handle multiple key sequence if separated by commas or semicolons
        if "," in input_text or ";" in input_text:
            key_sequence = re.split(r'[,;]', input_text)
            results = []
            
            for single_key in key_sequence:
                single_key = single_key.strip().lower()
                
                # Check if the key is a valid special key
                if single_key not in special_keys and not re.match(r'hold\s+(\w+),?\s+(?:press\s+)?(\w+)', single_key):
                    return f"Error: '{single_key}' is not a valid special key or combination. Use fill_input for typing text."
                
                result = _execute_special_key_action(single_key, special_keys)
                # Minimal delay between key actions for performance
                time.sleep(0.05)
                results.append(result)
            
            return "Executed key sequence: " + " → ".join(results)
        else:
            # Single key handling
            normalized_input = input_text.lower()
            
            # Check if the key is a valid special key
            if normalized_input not in special_keys and not re.match(r'hold\s+(\w+),?\s+(?:press\s+)?(\w+)', normalized_input):
                return f"Error: '{normalized_input}' is not a valid special key or combination. Use fill_input for typing text."
            
            return _execute_special_key_action(normalized_input, special_keys)
            
    except Exception as e:
        return f"Error with keyboard action: {str(e)}"

def _execute_special_key_action(key_input, special_keys):
    """Execute a special key action (helper for keyboard_action)."""
    if key_input in special_keys:
        key = special_keys[key_input]
        print(f"Pressing special key: {key}")
        
        # Handle special case for space
        if (key == " "):
            page.keyboard.press("Space")
        else:
            page.keyboard.press(key)
            
        return f"Pressed {key_input}"
    
    # Handle hold-and-press patterns like "hold shift, press tab"
    hold_match = re.match(r'hold\s+(\w+),?\s+(?:press\s+)?(\w+)', key_input)
    if (hold_match):
        modifier, key = hold_match.groups()
        modifier_key = special_keys.get(modifier.lower(), modifier.capitalize())
        key_to_press = special_keys.get(key.lower(), key.capitalize())
        
        print(f"Holding {modifier_key} and pressing {key_to_press}")
        page.keyboard.down(modifier_key)
        time.sleep(0.05)  # Minimal delay for key registration
        page.keyboard.press(key_to_press)
        time.sleep(0.05)  # Minimal delay before release
        page.keyboard.up(modifier_key)
        
        return f"Held {modifier} and pressed {key}"
    
    return f"Unknown key action: {key_input}"