"""
Custom message types to replace langchain_core.messages.
Provides SystemMessage, HumanMessage, AIMessage, and ToolMessage classes.
"""

from typing import Any, Dict, Optional, List


class BaseMessage:
    """Base class for all message types."""
    
    def __init__(self, content: str, **kwargs):
        self.content = content
        self.metadata = kwargs
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(content={self.content[:50]}...)"


class SystemMessage(BaseMessage):
    """System message from the system."""
    role = "system"
    
    def pretty_print(self):
        print(f"System: {self.content}")


class HumanMessage(BaseMessage):
    """Message from a human user."""
    role = "user"
    
    def pretty_print(self):
        print(f"User: {self.content}")


class AIMessage(BaseMessage):
    """Message from the AI agent."""
    role = "assistant"
    
    def __init__(self, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, **kwargs):
        super().__init__(content, **kwargs)
        self.tool_calls = tool_calls or []
    
    def pretty_print(self):
        print(f"Assistant: {self.content}")
        if self.tool_calls:
            print(f"Tool calls: {len(self.tool_calls)}")


class ToolMessage(BaseMessage):
    """Message containing tool execution result."""
    role = "tool"
    
    def __init__(self, content: str, tool_call_id: str, **kwargs):
        super().__init__(content, **kwargs)
        self.tool_call_id = tool_call_id
    
    def pretty_print(self):
        print(f"Tool result ({self.tool_call_id}): {self.content[:100]}...")
