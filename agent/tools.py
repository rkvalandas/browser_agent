"""
Custom tool decorator and wrapper to replace langchain_core.tools.
Provides a simple decorator that wraps functions with tool metadata.
"""

import json
import inspect
from typing import Any, Callable, Dict, Optional


class Tool:
    """Represents a tool that can be invoked by the agent."""
    
    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        self.name = name or func.__name__
        self.full_docstring = func.__doc__ or ""
        
        if description:
            self.description = description
        elif self.full_docstring:
            lines = self.full_docstring.strip().split("\n")
            description_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("Parameters:", "Returns:", "Examples:", "Example:", "Args:", "Input format:", "Usage:", "Raises:", "Attributes:", "Input:")):
                    break
                if stripped:
                    description_lines.append(stripped)
            
            self.description = " ".join(description_lines) if description_lines else ""
        else:
            self.description = ""
        
        sig = inspect.signature(func)
        self.parameters = {}
        for param_name, param in sig.parameters.items():
            if param_name != 'self':
                param_type = param.annotation if param.annotation != inspect.Parameter.empty else "string"
                param_desc = self._extract_param_description(param_name)
                
                self.parameters[param_name] = {
                    "type": str(param_type).replace("<class '", "").replace("'>", ""),
                    "description": param_desc
                }
    
    def _extract_param_description(self, param_name: str) -> str:
        """Extract parameter description from docstring."""
        if not self.full_docstring:
            return f"Parameter: {param_name}"
        
        lines = self.full_docstring.split("\n")
        in_params = False
        param_lines = []
        found_param = False
        
        for i, line in enumerate(lines):
            # Check for various parameter section headers
            if "Parameters:" in line or "Args:" in line or "Input format:" in line or "Input:" in line:
                in_params = True
                # For sections like "Input format:", check if this is describing our param
                if ("Input format:" in line or "Input:" in line) and not any(x in line for x in ["Parameters:", "Args:"]):
                    # For input format style docs, collect from here
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j]
                        next_stripped = next_line.strip()
                        
                        # Stop at empty lines followed by new sections
                        if not next_stripped:
                            if j + 1 < len(lines) and lines[j + 1].strip() and lines[j + 1][0] != ' ':
                                break
                            continue
                        
                        # Stop if we hit Returns, Examples, Usage, etc. at start of line
                        if next_stripped and not next_line[0].isspace() and next_stripped.endswith(":"):
                            break
                        
                        # Add content
                        if next_stripped:
                            param_lines.append(next_stripped)
                    
                    if param_lines:
                        return " ".join(param_lines)
                continue
            
            if in_params:
                stripped = line.strip()
                
                # Check if we've reached a new section
                if stripped and not line[0].isspace() and ":" in line and param_name not in line:
                    # New section (like "Returns:")
                    break
                
                # Look for the parameter name with colon (handles both "param:" and "param (type):")
                if param_name in line and ":" in line:
                    found_param = True
                    # Start collecting lines
                    # Get everything after the first colon
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        desc_start = parts[1].strip()
                        if desc_start:
                            param_lines.append(desc_start)
                    
                    # Continue collecting indented lines until we hit a non-indented line
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j]
                        next_stripped = next_line.strip()
                        
                        # Stop if we hit a new section or parameter at start of line
                        if next_stripped and not next_line[0].isspace():
                            break
                        
                        # Stop if we hit Returns, Examples, etc.
                        if next_stripped.startswith(("Returns:", "Return:", "Examples:", "Example:", "Usage:", "Raises:", "Attributes:")):
                            break
                        
                        # Add indented content
                        if next_stripped:
                            param_lines.append(next_stripped)
                    
                    break
        
        if param_lines:
            return " ".join(param_lines)
        
        return f"Parameter: {param_name}"
    
    def invoke(self, args: Dict[str, Any]) -> Any:
        """Execute the tool with the given arguments."""
        return self.func(**args)
    
    def __call__(self, *args, **kwargs):
        """Make the tool callable."""
        return self.func(*args, **kwargs)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert tool to JSON schema for LLM."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": list(self.parameters.keys())
                }
            }
        }


def tool(func: Callable) -> Tool:
    """
    Decorator to mark a function as a tool.
    
    Usage:
        @tool
        def my_tool(param1: str, param2: int):
            '''Tool description'''
            return result
    """
    return Tool(func)
