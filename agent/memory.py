"""
Memory system for the agent to store and retrieve conversation history.
Supports different memory types: short-term, long-term, and summarized.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from agent.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage


class Memory:
    """Base memory class for storing conversation history."""
    
    def __init__(self, max_size: int = 50):
        self.messages: List[Dict[str, Any]] = []
        self.max_size = max_size
        self.created_at = datetime.now()
    
    def add_message(self, role: str, content: str, tool_calls: Optional[List[Dict]] = None, metadata: Optional[Dict] = None) -> None:
        """Add a message to memory."""
        message = {
            "timestamp": datetime.now(),
            "role": role,
            "content": content,
            "tool_calls": tool_calls or [],
            "metadata": metadata or {}
        }
        self.messages.append(message)
        
        # Keep memory size manageable
        if len(self.messages) > self.max_size:
            self.messages.pop(0)
    
    def add_base_message(self, msg: BaseMessage) -> None:
        """Add a BaseMessage to memory."""
        tool_calls = None
        if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls'):
            tool_calls = msg.tool_calls
        
        self.add_message(
            role=msg.role,
            content=msg.content,
            tool_calls=tool_calls
        )
    
    def get_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get messages from memory."""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, Any]]:
        """Get last N messages."""
        return self.messages[-n:] if len(self.messages) >= n else self.messages
    
    def clear(self) -> None:
        """Clear all messages from memory."""
        self.messages = []
    
    def get_context_window(self, max_messages: int = 10) -> str:
        """Get formatted context from recent messages."""
        recent = self.get_last_n_messages(max_messages)
        if not recent:
            return ""
        
        context = []
        for msg in recent:
            role = msg["role"].upper()
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            context.append(f"{role}: {content}")
        
        return "\n".join(context)
    
    def get_summary(self) -> str:
        """Get a summary of the memory."""
        return f"Memory contains {len(self.messages)} messages, max size: {self.max_size}"


class ConversationMemory(Memory):
    """Memory specialized for conversation tracking with context."""
    
    def __init__(self, max_size: int = 100):
        super().__init__(max_size)
        self.task_history: List[Dict[str, Any]] = []
    
    def add_task(self, task: str, result: str, success: bool, metadata: Optional[Dict] = None) -> None:
        """Record a completed task."""
        task_record = {
            "timestamp": datetime.now(),
            "task": task,
            "result": result,
            "success": success,
            "metadata": metadata or {}
        }
        self.task_history.append(task_record)
        
        # Keep task history manageable
        if len(self.task_history) > self.max_size:
            self.task_history.pop(0)
    
    def get_task_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get task history."""
        if limit:
            return self.task_history[-limit:]
        return self.task_history
    
    def get_successful_tasks(self) -> List[Dict[str, Any]]:
        """Get only successful tasks."""
        return [t for t in self.task_history if t["success"]]
    
    def get_failed_tasks(self) -> List[Dict[str, Any]]:
        """Get only failed tasks."""
        return [t for t in self.task_history if not t["success"]]


class ContextMemory(Memory):
    """Memory that maintains session context and state."""
    
    def __init__(self, max_size: int = 50):
        super().__init__(max_size)
        self.context: Dict[str, Any] = {
            "session_id": str(datetime.now().timestamp()),
            "current_url": None,
            "page_title": None,
            "user_data": {},
            "interaction_count": 0
        }
    
    def update_context(self, key: str, value: Any) -> None:
        """Update context value."""
        self.context[key] = value
    
    def get_context(self, key: str) -> Optional[Any]:
        """Get context value."""
        return self.context.get(key)
    
    def increment_interaction_count(self) -> None:
        """Increment interaction counter."""
        self.context["interaction_count"] = self.context.get("interaction_count", 0) + 1
    
    def get_session_summary(self) -> str:
        """Get session summary."""
        return f"""Session: {self.context.get('session_id')}
Current URL: {self.context.get('current_url', 'N/A')}
Page Title: {self.context.get('page_title', 'N/A')}
Interactions: {self.context.get('interaction_count', 0)}
Messages: {len(self.messages)}"""


class SessionMemory:
    """Main session memory combining all memory types."""
    
    def __init__(self, max_conversation_size: int = 100, max_context_size: int = 50):
        self.conversation = ConversationMemory(max_conversation_size)
        self.context = ContextMemory(max_context_size)
    
    def add_exchange(self, human_input: str, ai_response: str, tool_calls: Optional[List[Dict]] = None, task_result: Optional[Dict] = None) -> None:
        """Record a full exchange between human and AI."""
        # Add to conversation memory
        self.conversation.add_message("user", human_input)
        self.conversation.add_message("assistant", ai_response, tool_calls=tool_calls)
        
        # Record task if provided
        if task_result:
            self.conversation.add_task(
                task=human_input,
                result=ai_response,
                success=task_result.get("success", False),
                metadata=task_result.get("metadata")
            )
        
        # Update interaction count
        self.context.increment_interaction_count()
    
    def get_memory_report(self) -> str:
        """Get a full memory report."""
        return f"""=== SESSION MEMORY REPORT ===
{self.context.get_session_summary()}

Recent Messages: {len(self.conversation.messages)}
Successful Tasks: {len(self.conversation.get_successful_tasks())}
Failed Tasks: {len(self.conversation.get_failed_tasks())}

=== CONTEXT WINDOW ===
{self.conversation.get_context_window(max_messages=5)}"""
    
    def get_for_llm(self, include_recent_messages: int = 5) -> str:
        """Get formatted memory for LLM context."""
        context_str = f"Session ID: {self.context.context.get('session_id')}\n"
        context_str += f"Interactions: {self.context.context.get('interaction_count')}\n"
        
        if self.conversation.get_successful_tasks():
            context_str += f"\nRecent successful tasks: {len(self.conversation.get_successful_tasks())}\n"
        
        recent_context = self.conversation.get_context_window(include_recent_messages)
        if recent_context:
            context_str += f"\nRecent conversation:\n{recent_context}"
        
        return context_str
    
    def clear(self) -> None:
        """Clear all memory."""
        self.conversation.clear()
        self.context.clear()
