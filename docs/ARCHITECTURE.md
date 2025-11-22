# 🏗️ Architecture Guide

Technical overview of the Browser Agent's architecture and design patterns.

## System Overview

The Browser Agent is built using a modular architecture that separates concerns across multiple layers:

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                       │
│                      (CLI Commands)                         │
├─────────────────────────────────────────────────────────────┤
│                       Agent Layer                           │
│              (Custom LLM + Agentic Loop)                    │
├─────────────────────────────────────────────────────────────┤
│                       Tools Layer                           │
│                  (Browser Controllers)                      │
├─────────────────────────────────────────────────────────────┤
│                      Browser Layer                          │
│                     (Playwright)                            │
├─────────────────────────────────────────────────────────────┤
│                        Web Layer                            │
│                   (Target Websites)                         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Agent Layer (`agent/`)

The AI reasoning and decision-making component with custom LLM integration.

**Key Files:**

- `agent.py` - Main agent initialization and LLM setup
- `agent_graph.py` - Custom agentic loop executor
- `llm_providers.py` - LLM provider wrappers (OpenAI, Azure, Anthropic, Groq)
- `tools.py` - Custom tool decorator and JSON schema generation
- `messages.py` - Message types for conversation flow

**Responsibilities:**

- Natural language understanding
- Task planning and decomposition
- Tool selection and execution
- Progress monitoring and adaptation
- Error handling and recovery

**Technology Stack:**

- **Custom Agent Executor** - Synchronous agentic loop with tool binding
- **Direct SDK Integration** - OpenAI, Azure OpenAI, Anthropic, Groq APIs
- **Custom Tool System** - Tool decorator with JSON schema generation

### 2. Browser Layer (`browser/`)

Browser automation and control interface.

#### Analyzers (`browser/analyzers/`)

- `page_analyzer.py` - DOM analysis and element mapping

**Functions:**

- Scan visible elements
- Assign unique IDs to interactive elements
- Extract element properties and attributes
- Handle dynamic content updates

#### Controllers (`browser/controllers/`)

- `browser_controller.py` - Main browser interface and tool coordination
- `element_controller.py` - Element interaction (click, type, select)
- `keyboard_controller.py` - Keyboard actions and shortcuts

**Functions:**

- Browser lifecycle management
- Element identification and interaction
- Form handling and input simulation
- Keyboard event generation

#### Navigation (`browser/navigation/`)

- `navigator.py` - URL navigation and history management
- `scroll_manager.py` - Viewport scrolling and positioning

**Functions:**

- URL handling and validation
- History navigation (back/forward)
- Scroll detection and boundary management
- Viewport positioning

#### Utils (`browser/utils/`)

- `dom_helpers.py` - DOM manipulation utilities
- `input_helpers.py` - Input processing and validation
- `user_interaction.py` - User prompt and interaction tools

### 3. CLI Layer (`cli/`)

Command-line interface and system management.

**Key Files:**

- `commands.py` - CLI command definitions and argument parsing
- `chrome_launcher.py` - Chrome browser launching and debug setup

**Responsibilities:**

- Command-line argument processing
- Browser profile management
- System diagnostics and health checks
- Configuration management

### 4. Configuration Layer (`configurations/`)

Centralized configuration management.

**Key Files:**

- `config.py` - All configuration settings and environment variables

**Features:**

- Multi-provider LLM configuration
- Browser behavior settings
- Performance optimization options
- Security and debugging preferences

## Data Flow Architecture

### 1. Task Initiation

```
User Input → CLI Parser → Agent Creation → Task Execution
```

1. User provides natural language task via CLI
2. CLI parses arguments and initializes configuration
3. Agent is created with appropriate LLM provider
4. Task is passed to agent for execution

### 2. Agent Processing

```
Task → Planning → Tool Selection → Execution → Monitoring
```

1. **Planning Phase:**

   - Parse user intent
   - Break down complex tasks
   - Identify required browser actions

2. **Tool Selection:**

   - Choose appropriate browser tools
   - Plan action sequence
   - Set up error handling

3. **Execution Phase:**
   - Execute browser actions sequentially
   - Monitor page state changes
   - Adapt strategy based on results

### 3. Browser Interaction

```
Tool Call → Browser Controller → Playwright → Web Page → Result
```

1. Agent calls browser tool (e.g., `click`, `type`)
2. Controller translates to Playwright commands
3. Playwright executes browser actions
4. Web page responds with state changes
5. Results are captured and returned

### 4. Page Analysis

```
Page Load → DOM Scan → Element Mapping → ID Assignment → Tool Response
```

1. Page content loads completely
2. JavaScript scans DOM for interactive elements
3. Elements are categorized and mapped
4. Unique IDs assigned for tool reference
5. Structured data returned to agent

## State Management

### Agent State

The agent maintains state across interactions using LangGraph's memory system:

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    # Additional state can be added here
```

**State Components:**

- **Message History** - Complete conversation context
- **Tool Results** - Outputs from browser interactions
- **Page Context** - Current page state and element mappings
- **Error Context** - Error history for recovery strategies

### Browser State

Browser state is managed through:

```python
# Global browser state
page = None  # Current Playwright page instance
current_x = 100  # Mouse cursor X position
current_y = 100  # Mouse cursor Y position
page_elements = []  # Current page element mappings
```

### Session Persistence

- **Thread-based Sessions** - Each conversation has a unique thread ID
- **Memory Checkpointing** - State is preserved across interactions
- **Profile Persistence** - Browser profiles maintain user data

## Tool Architecture

### Tool Interface

All browser tools follow a consistent interface:

```python
@tool
def tool_name(parameters) -> str:
    """
    Tool description and usage information.

    Parameters:
        param: Description of parameter

    Returns: String description of action result
    """
    try:
        # Tool implementation
        return "Success message"
    except Exception as e:
        return f"Error: {str(e)}"
```

### Tool Categories

1. **Analysis Tools**

   - `analyze_page()` - DOM scanning and element mapping

2. **Navigation Tools**

   - `navigate(url)` - URL navigation
   - `go_back()` - History navigation
   - `scroll(direction)` - Viewport movement

3. **Interaction Tools**

   - `click(target)` - Element clicking
   - `type(value)` - Text input
   - `select_option(config)` - Dropdown selection
   - `keyboard_action(key)` - Keyboard commands

4. **User Tools**
   - `ask_user(prompt)` - User interaction and input

### Tool Registration

Tools are automatically discovered and registered:

```python
def get_browser_tools():
    """Collect all browser tools for agent use."""
    return [
        analyze_page,
        navigate,
        click,
        type,
        select_option,
        keyboard_action,
        scroll,
        go_back,
        ask_user
    ]
```

## Error Handling Architecture

### Multi-Level Error Handling

1. **Tool Level** - Individual tool error handling
2. **Controller Level** - Browser interaction error recovery
3. **Agent Level** - Strategic error recovery and alternative approaches
4. **CLI Level** - User-friendly error reporting

### Error Recovery Strategies

```python
# Example error recovery flow
try:
    # Primary action attempt
    element = find_element_by_id(element_id)
    click_element(element)
except ElementNotFoundError:
    # Fallback 1: Scroll and retry
    scroll("down")
    element = find_element_by_id(element_id)
    click_element(element)
except StaleElementError:
    # Fallback 2: Re-analyze page
    analyze_page()
    element = find_element_by_text(element_text)
    click_element(element)
except Exception as e:
    # Final fallback: Report to agent for alternative strategy
    return f"Failed to click element: {str(e)}"
```

## Performance Architecture

### Optimization Strategies

1. **Minimal Tool Calls**

   - Batch related operations
   - Reduce unnecessary page analysis
   - Cache element mappings when possible

2. **Fast Mode Configuration**

   - Reduced artificial delays
   - Optimized mouse movements
   - Minimized CSS transitions

3. **Selective Loading**
   - Optional image loading
   - JavaScript-only when needed
   - Streamlined browser arguments

### Memory Management

- **Automatic Cleanup** - Browser profiles and temporary files
- **State Pruning** - Old conversation history management
- **Resource Limits** - Maximum token usage and timeout controls

## Security Architecture

### Sandboxing

- **Browser Isolation** - Separate profiles for different tasks
- **Network Restrictions** - Optional domain filtering
- **Download Controls** - Automatic download blocking

### Data Protection

- **No Persistent Storage** - Sensitive data not saved by default
- **Encrypted Communication** - HTTPS enforcement where possible
- **API Key Management** - Secure environment variable handling

## Extensibility Architecture

### Adding New Tools

1. Create tool function with `@tool` decorator
2. Add to tool registration in `get_browser_tools()`
3. Update agent prompts to include new tool description

### Adding New LLM Providers

1. Add provider configuration to `config.py`
2. Implement provider initialization in `agent.py`
3. Add provider-specific settings and validation

### Custom Browser Behavior

1. Extend browser controllers with new functionality
2. Add configuration options in `config.py`
3. Integrate with existing tool interfaces

## Testing Architecture

### Unit Testing

- **Tool Testing** - Individual tool functionality
- **Controller Testing** - Browser interaction components
- **Configuration Testing** - Settings validation

### Integration Testing

- **End-to-End Workflows** - Complete task execution
- **Multi-Provider Testing** - LLM provider compatibility
- **Browser Compatibility** - Different browser versions

### Performance Testing

- **Load Testing** - Multiple concurrent agents
- **Memory Testing** - Long-running sessions
- **Speed Testing** - Task execution benchmarks

## Monitoring and Debugging

### Logging Architecture

```python
# Hierarchical logging system
logger = logging.getLogger("browser_agent")
logger.addHandler(console_handler)
logger.addHandler(file_handler)  # Optional

# Component-specific loggers
agent_logger = logging.getLogger("browser_agent.agent")
browser_logger = logging.getLogger("browser_agent.browser")
cli_logger = logging.getLogger("browser_agent.cli")
```

### Debug Features

- **Verbose Mode** - Detailed operation logging
- **Screenshot Capture** - Visual debugging on errors
- **Page Source Saving** - HTML capture for analysis
- **Execution Tracing** - Step-by-step action logging

This architecture provides a robust, scalable, and maintainable foundation for browser automation with AI-driven natural language control.
