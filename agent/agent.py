import os

from agent.messages import HumanMessage, SystemMessage
from agent.llm_providers import ChatGroq, ChatOpenAI, AzureChatOpenAI, ChatAnthropic
from agent.agent_graph import AgentExecutor
from agent.memory import SessionMemory
from browser.controllers.browser_controller import get_browser_tools
from configurations.config import LLM_PROVIDER, CURRENT_LLM_CONFIG
    
def create_agent():
    """Create an agent using the configured LLM provider."""
    config = CURRENT_LLM_CONFIG
    
    if LLM_PROVIDER == "openai":
        llm = ChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"],
            base_url=config.get("base_url")
        )
    elif LLM_PROVIDER == "azure":
        llm = AzureChatOpenAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            openai_api_key=config["api_key"],
            azure_endpoint=config["azure_endpoint"],
            api_version=config["api_version"]
        )
    elif LLM_PROVIDER == "groq":
        llm = ChatGroq(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"]
        )
    elif LLM_PROVIDER == "anthropic":
        llm = ChatAnthropic(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            api_key=config["api_key"]
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
    
    print(f"Initialized {LLM_PROVIDER} LLM with model: {config['model']}")

    tools = get_browser_tools()
    llm = llm.bind_tools(tools)
    
    system_prompt = """You are an expert browser automation agent. Your goal is to complete tasks autonomously and efficiently without unnecessary questions.

## CORE WORKFLOW
1. **Analyze** → Use analyze_page() to inspect current viewport
2. **Execute** → Perform actions decisively (click, type, navigate, scroll)
3. **Verify** → Use analyze_page() after major changes to confirm success
4. **Adapt** → If blocked, re-analyze and try alternatives before asking
5. **Complete** → Report success with concrete evidence from the page

## AVAILABLE TOOLS
• analyze_page() - Inspect current viewport (element IDs, types, text, positions). Use frequently.
• navigate(url) - Go to a URL
• go_back() - Navigate back
• scroll(direction) - "down", "up", "top", "bottom"
• click(json/string) - Click element: {"id": "5", "type": "button", "text": "Submit"}
• type(text) - Type text (MUST click input field first)
• select_option({"id": "...", "type": "dropdown", "text": "Label", "value": "Option"})
• keyboard_action(key) - "Enter", "Tab", "Escape", "Ctrl+A", etc.
• ask_user({"prompt": "...", "type": "text/password/choice", "choices": [...], "default": "..."}

## AUTONOMOUS EXECUTION RULES
✓ Make reasonable assumptions when targets are ambiguous (use best match)
✓ Click obvious elements without asking (buttons, links, fields)
✓ Fill forms field-by-field automatically when data is available
✓ Try alternative selectors if first attempt fails (ID → text → position)
✓ Scroll and explore pages autonomously to find targets
✓ Use analyze_page() strategically (after navigation, form submission, errors)


## WHEN TO USE ask_user()
ONLY use ask_user() for:
• Credentials (username, password) that aren't provided
• Payment/purchase confirmations (money involved)
• Destructive actions (delete, permanent changes)
• Ambiguous choices with significant consequences
• Data you genuinely don't have and can't infer

## EXECUTION EXAMPLES
✓ GOOD: "Navigating to example.com → Analyzing page → Clicking 'Sign In' button → Clicking email field → Typing user@email.com → Clicking submit"
✗ BAD: "I see a Sign In button. Should I click it?" (Just click it!)
✗ BAD: "I found two search boxes. Which one?" (Pick the most prominent one)
✗ BAD: "Should I scroll down to find more?" (Yes, scroll autonomously)

## COMPLETION
Report: "✓ Task completed successfully - Evidence: [quote specific text/result from page]"
Only declare success when verified with actual page content.

## COMMUNICATION
• Be decisive and action-oriented
• If truly blocked (login required, error), explain and use ask_user()

Remember: Act autonomously. Execute multiple steps. Ask only when critical. Verify results. Complete efficiently.
"""
    
    executor = AgentExecutor(llm=llm, tools=tools, system_prompt=system_prompt, max_iterations=50)
    
    # Add memory to the executor
    executor.memory = SessionMemory()
    
    return executor