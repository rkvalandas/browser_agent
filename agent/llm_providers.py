"""
Custom LLM provider implementations to replace langchain integrations.
Wraps OpenAI, Anthropic, Groq, and Azure APIs directly.
"""

import json
import os
from typing import Any, Dict, List, Optional
from agent.messages import AIMessage
from agent.tools import Tool


class LLMBase:
    """Base class for LLM providers."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, api_key: Optional[str] = None):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.tools = []
    
    def bind_tools(self, tools: List[Tool]) -> "LLMBase":
        """Bind tools to the LLM instance."""
        self.tools = tools
        return self
    
    def invoke(self, messages: List[Any]) -> AIMessage:
        """Invoke the LLM. Must be implemented by subclass."""
        raise NotImplementedError


class ChatOpenAI(LLMBase):
    """OpenAI ChatGPT wrapper."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(model, temperature, max_tokens, api_key)
        self.base_url = base_url or "https://api.openai.com/v1"
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
    
    def invoke(self, messages: List[Any]) -> AIMessage:
        """Call OpenAI API."""
        try:
            import openai
            
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            tools_param = None
            if self.tools:
                tools_param = [tool.to_json_schema() for tool in self.tools]
            
            api_kwargs = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
            }
            if tools_param:
                api_kwargs["tools"] = tools_param
                api_kwargs["tool_choice"] = "auto"
            if self.max_tokens:
                api_kwargs["max_tokens"] = self.max_tokens
            
            response = client.chat.completions.create(**api_kwargs)
            
            content = response.choices[0].message.content or ""
            tool_calls = []
            
            # Parse tool calls if present
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments)
                    })
            
            return AIMessage(content=content, tool_calls=tool_calls)
        
        except Exception as e:
            return AIMessage(content=f"Error calling OpenAI: {str(e)}")


class ChatAnthropic(LLMBase):
    """Anthropic Claude wrapper."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, api_key: Optional[str] = None):
        super().__init__(model, temperature, max_tokens, api_key)
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
    
    def invoke(self, messages: List[Any]) -> AIMessage:
        """Call Anthropic API."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            formatted_messages = []
            system_prompt = None
            
            for msg in messages:
                if msg.role == "system":
                    system_prompt = msg.content
                else:
                    formatted_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            tools_param = None
            if self.tools:
                tools_param = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": {
                            "type": "object",
                            "properties": tool.parameters,
                            "required": list(tool.parameters.keys())
                        }
                    }
                    for tool in self.tools
                ]
            
            api_kwargs = {
                "model": self.model,
                "messages": formatted_messages,
                "system": system_prompt,
                "temperature": self.temperature,
            }
            if tools_param:
                api_kwargs["tools"] = tools_param
            if self.max_tokens:
                api_kwargs["max_tokens"] = self.max_tokens
            
            response = client.messages.create(**api_kwargs)
            
            content = ""
            tool_calls = []
            
            for block in response.content:
                if hasattr(block, 'text'):
                    content += block.text
                elif block.type == "tool_use":
                    tool_calls.append({
                        "id": block.id,
                        "name": block.name,
                        "args": block.input
                    })
            
            return AIMessage(content=content, tool_calls=tool_calls)
        
        except Exception as e:
            return AIMessage(content=f"Error calling Anthropic: {str(e)}")


class ChatGroq(LLMBase):
    """Groq API wrapper."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, api_key: Optional[str] = None):
        super().__init__(model, temperature, max_tokens, api_key)
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
    
    def invoke(self, messages: List[Any]) -> AIMessage:
        """Call Groq API."""
        try:
            from groq import Groq
            
            client = Groq(api_key=self.api_key)
            
            formatted_messages = []
            for msg in messages:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            tools_param = None
            if self.tools:
                tools_param = [tool.to_json_schema() for tool in self.tools]
            
            api_kwargs = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
            }
            if tools_param:
                api_kwargs["tools"] = tools_param
                api_kwargs["tool_choice"] = "auto"
            if self.max_tokens:
                api_kwargs["max_tokens"] = self.max_tokens
            
            response = client.chat.completions.create(**api_kwargs)
            
            content = response.choices[0].message.content or ""
            tool_calls = []
            
            # Parse tool calls if present
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments)
                    })
            
            return AIMessage(content=content, tool_calls=tool_calls)
        
        except Exception as e:
            return AIMessage(content=f"Error calling Groq: {str(e)}")


class AzureChatOpenAI(LLMBase):
    """Azure OpenAI wrapper."""
    
    def __init__(self, model: str, temperature: float = 0.7, max_tokens: int = 4096, 
                 openai_api_key: Optional[str] = None, azure_endpoint: Optional[str] = None,
                 api_version: str = "2024-02-15-preview"):
        super().__init__(model, temperature, max_tokens, openai_api_key)
        self.azure_endpoint = azure_endpoint or os.getenv("AZURE_ENDPOINT")
        self.api_version = api_version
        self.api_key = openai_api_key or os.getenv("AZURE_OPENAI_API_KEY")
    
    def invoke(self, messages: List[Any]) -> AIMessage:
        """Call Azure OpenAI API."""
        try:
            from openai import AzureOpenAI
            
            client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
            
            formatted_messages = []
            for msg in messages:
                msg_dict = {
                    "role": msg.role,
                    "content": msg.content
                }
                if msg.role == "assistant" and hasattr(msg, 'tool_calls') and msg.tool_calls:
                    msg_dict["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc["args"])
                            }
                        }
                        for tc in msg.tool_calls
                    ]
                if msg.role == "tool" and hasattr(msg, 'tool_call_id'):
                    msg_dict["tool_call_id"] = msg.tool_call_id
                formatted_messages.append(msg_dict)
            
            tools_param = None
            if self.tools:
                tools_param = [tool.to_json_schema() for tool in self.tools]
            
            api_kwargs = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": self.temperature,
            }
            if tools_param:
                api_kwargs["tools"] = tools_param
                api_kwargs["tool_choice"] = "auto"
            if self.max_tokens:
                api_kwargs["max_tokens"] = self.max_tokens
            
            response = client.chat.completions.create(**api_kwargs)
            
            content = response.choices[0].message.content or ""
            tool_calls = []
            
            # Parse tool calls if present
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                for tc in response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments)
                    })
            
            return AIMessage(content=content, tool_calls=tool_calls)
        
        except Exception as e:
            return AIMessage(content=f"Error calling Azure OpenAI: {str(e)}")
