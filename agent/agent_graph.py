"""
Custom agent state and execution graph to replace langgraph.
Implements a simple agentic loop without external graph library.
"""

from typing import Any, Dict, List, Optional, Callable
from agent.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage, BaseMessage


class AgentExecutor:
    """Simple agentic loop executor without langgraph."""
    
    def __init__(self, llm: Any, tools: List[Any], system_prompt: str, max_iterations: int = 50):
        self.llm = llm
        self.tools = tools
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.tool_map = {tool.name: tool for tool in tools}
        self.llm.bind_tools(tools)
    
    def invoke(self, input_text: str, thread_id: str = "main") -> Dict[str, Any]:
        """Execute the agent synchronously."""
        messages: List[BaseMessage] = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=input_text)
        ]
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            response = self.llm.invoke(messages)
            messages.append(response)
            
            if not response.tool_calls:
                return {
                    "input": input_text,
                    "output": response.content,
                    "messages": messages
                }
            
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                if tool_name in self.tool_map:
                    try:
                        tool = self.tool_map[tool_name]
                        result = tool.invoke(tool_args)
                        tool_message = ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id
                        )
                        messages.append(tool_message)
                    except Exception as e:
                        tool_message = ToolMessage(
                            content=f"Error executing {tool_name}: {str(e)}",
                            tool_call_id=tool_id
                        )
                        messages.append(tool_message)
                else:
                    tool_message = ToolMessage(
                        content=f"Tool {tool_name} not found",
                        tool_call_id=tool_id
                    )
                    messages.append(tool_message)
        
        # Max iterations reached
        return {
            "input": input_text,
            "output": f"Max iterations ({self.max_iterations}) reached without completion",
            "messages": messages
        }
    
    def stream(self, input_text: str, thread_id: str = "main") -> List[Dict[str, Any]]:
        """Stream agent execution (returns list of events)."""
        messages: List[BaseMessage] = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=input_text)
        ]
        
        results = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Call LLM with current messages
            response = self.llm.invoke(messages)
            messages.append(response)
            
            # Emit event for streaming
            event = {
                "messages": [response]
            }
            results.append(event)
            
            # Print response
            response.pretty_print()
            
            # Check if LLM wants to use tools
            if not response.tool_calls:
                # No tools, we're done
                break
            
            # Execute tools
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                # Find and execute tool
                if tool_name in self.tool_map:
                    try:
                        tool = self.tool_map[tool_name]
                        result = tool.invoke(tool_args)
                        tool_message = ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id
                        )
                        messages.append(tool_message)
                    except Exception as e:
                        tool_message = ToolMessage(
                            content=f"Error executing {tool_name}: {str(e)}",
                            tool_call_id=tool_id
                        )
                        messages.append(tool_message)
                else:
                    tool_message = ToolMessage(
                        content=f"Tool {tool_name} not found",
                        tool_call_id=tool_id
                    )
                    messages.append(tool_message)
        
        return results
