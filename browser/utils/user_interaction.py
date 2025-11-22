"""
User interaction utilities for requesting information or permissions from the user.
"""

import time
from agent.tools import tool

# This tool doesn't need a page reference since it interacts with the terminal directly

@tool
def ask_user(json_input) -> str:
    """
    Requests a single piece of information from the user.
    
    Input (json_input) - JSON object with:
    - "prompt": Question to ask (required)
    - "type": "text", "password", or "choice" (optional, default: text)
    - "choices": Array of options for choice type (optional)
    - "default": Default value if user provides no input (optional)
    
    Examples:
    - {"prompt": "Enter username"}
    - {"prompt": "Password", "type": "password"}
    - {"prompt": "Choose option", "type": "choice", "choices": ["A", "B"]}
    
    Returns: User's response as string. Make separate calls for multiple fields.
    """
    try:
        # Parse input
        import json
        
        if isinstance(json_input, str):
            try:
                # Try to parse as JSON
                input_data = json.loads(json_input)
            except json.JSONDecodeError:
                # If not valid JSON, try to parse as a Python dictionary string
                try:
                    # Clean up the input by replacing single quotes with double quotes
                    formatted_input = json_input.replace("'", "\"")
                    input_data = json.loads(formatted_input)
                except Exception:
                    # Last resort: treat the entire string as a prompt
                    input_data = {"prompt": json_input}
        else:
            # Already a dictionary
            input_data = json_input
        
        # Extract values - ensure we're only handling one value
        prompt = input_data.get("prompt", "Please provide one specific value:")
        input_type = input_data.get("type", "text").lower()
        choices = input_data.get("choices", [])
        default = input_data.get("default", "")
        
        # Validate required parameters
        if not prompt:
            return "Error: 'prompt' is required - specify what single value you need"
        
        # Format the prompt based on input type
        formatted_prompt = f"\n🔹 {prompt} (single value)"
        
        # If there are choices, display them
        if choices and isinstance(choices, list) and len(choices) > 0:
            formatted_prompt += "\n   Choose one option:"
            for i, choice in enumerate(choices, 1):
                formatted_prompt += f"\n   {i}. {choice}"
            
            if default:
                default_index = next((i+1 for i, c in enumerate(choices) if c == default), "")
                if default_index:
                    formatted_prompt += f"\n   Default: {default_index}. {default}"
                else:
                    formatted_prompt += f"\n   Default: {default}"
            
            formatted_prompt += "\n   Enter single selection (number or option name): "
        else:
            # Regular text input
            if default:
                formatted_prompt += f" (default: {default}): "
            else:
                formatted_prompt += ": "
        
        # Display prompt and get user input for this single value
        if input_type == "password":
            # For password input, use getpass if available
            try:
                import getpass
                user_input = getpass.getpass(formatted_prompt)
            except ImportError:
                # Fallback for environments where getpass isn't available
                print(formatted_prompt + " (your input will be visible)")
                user_input = input()
        else:
            # Regular input for a single value
            user_input = input(formatted_prompt)
        
        # Use default value if input is empty
        if not user_input and default:
            user_input = default
            print(f"Using default single value: {default}")
        
        # Process choices if applicable
        if choices and isinstance(choices, list) and len(choices) > 0:
            # Check if input is a number corresponding to a choice
            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(choices):
                    user_input = choices[index]
                    print(f"Selected single option: {user_input}")
        
        return user_input
        
    except Exception as e:
        return f"Error getting single input value from user: {str(e)}"

def initialize():
    """Initialize the user interaction module (no-op for now)."""
    pass