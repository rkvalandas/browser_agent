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
        self.memory = None
        self.llm.bind_tools(tools)
    
    def invoke(self, input_text: str, thread_id: str = "main") -> Dict[str, Any]:
        """Execute the agent synchronously."""
        # Build system prompt with memory context
        system_content = self.system_prompt
        if self.memory:
            memory_context = self.memory.get_for_llm(include_recent_messages=5)
            if memory_context and self.memory.conversation.messages:
                system_content += f"\n\n## SESSION MEMORY\n{memory_context}"
        
        messages: List[BaseMessage] = [
            SystemMessage(content=system_content),
            HumanMessage(content=input_text)
        ]
        
        iteration = 0
        while iteration < self.max_iterations:
            iteration += 1
            
            response = self.llm.invoke(messages)
            messages.append(response)
            
            # Store in memory if available
            if self.memory:
                self.memory.conversation.add_base_message(response)
            
            if not response.tool_calls:
                # Store final result in memory
                if self.memory:
                    self.memory.add_exchange(
                        human_input=input_text,
                        ai_response=response.content,
                        task_result={"success": True}
                    )
                
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
        final_message = f"Max iterations ({self.max_iterations}) reached without completion"
        if self.memory:
            self.memory.add_exchange(
                human_input=input_text,
                ai_response=final_message,
                task_result={"success": False}
            )
        
        return {
            "input": input_text,
            "output": final_message,
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
