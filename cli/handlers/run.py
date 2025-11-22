"""
Main run command implementation.
"""

import os
import sys
import time
import traceback
from datetime import datetime
from argparse import Namespace

from cli.core import print_status_bar, print_section_header, print_colored, Colors, setup_terminal, reset_cursor, colorize, print_agent_response
from cli.utils import validate_environment, get_version
from configurations.config import BROWSER_OPTIONS, BROWSER_CONNECTION

def command_run(args):
    """Execute the main browser agent with enhanced error handling and status reporting."""
    from browser.browser_setup import initialize_browser, close_browser
    from browser.controllers.browser_controller import initialize
    from agent.agent import create_agent
    
    print_status_bar("Starting Browser Agent...", "PROGRESS")
    
    # Validate environment first
    issues = validate_environment()
    if issues:
        print_status_bar("Environment validation failed:", "ERROR")
        for issue in issues:
            print(f"  • {issue}")
        return False
    
    # Configure browser options
    if hasattr(args, 'headless') and args.headless:
        BROWSER_OPTIONS["headless"] = True
        print_status_bar("Running in headless mode (CLI flag)", "INFO")
    elif BROWSER_OPTIONS.get("headless", False):
        print_status_bar("Running in headless mode (from .env)", "INFO")
    
    # Create the agent with enhanced error handling
    print_status_bar("Creating AI agent with tools...", "PROGRESS")
    try:
        agent_executor = create_agent()
        print_status_bar("Agent created successfully!", "SUCCESS")
    except Exception as agent_error:
        print_status_bar(f"Failed to create agent: {str(agent_error)}", "ERROR")
        if args.verbose:
            print("\nDetailed traceback:")
            traceback.print_exc()
        return False

    # Connect to Chrome - fast and seamless (auto-launches if needed)
    print_status_bar("Initializing Chrome connection...", "PROGRESS")
    try:
        playwright, browser, page = initialize_browser(BROWSER_OPTIONS, BROWSER_CONNECTION)
        print_status_bar("Chrome ready!", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to initialize Chrome: {str(e)}", "ERROR")
        print_colored("💡 Chrome connection failed. Check if Chrome is installed.", Colors.BRIGHT_YELLOW)
        return False
    
    print_status_bar("Setting up browser controller...", "PROGRESS")
    try:
        initialize(page)
        print_status_bar("Browser controller ready!", "SUCCESS")
    except Exception as e:
        print_status_bar(f"Failed to initialize browser controller: {str(e)}", "ERROR")
        return False
    
    # Handle initial task if provided
    if hasattr(args, 'task') and args.task:
        print_section_header(f"Executing Initial Task: {args.task}")
        start_time = datetime.now()
        
        try:
            response = agent_executor.invoke(args.task)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print_status_bar(f"Task completed in {duration:.2f} seconds", "SUCCESS")
            print("\n" + "="*60)
            print("TASK RESULT:")
            print("="*60)
            print(response.get("output", "No output received"))
            print("="*60)
        except Exception as e:
            print_status_bar(f"Task execution failed: {str(e)}", "ERROR")
            if args.verbose:
                traceback.print_exc()
    
    # Interactive mode with enhanced prompts
    print_section_header("Interactive Mode")
    print_colored("💬 Enter your instructions for the browser agent", Colors.BRIGHT_GREEN)
    print_colored("💡 Type 'help' for available commands or 'exit' to quit", Colors.BRIGHT_YELLOW)
    print_colored("⌨️  Type 'shortcuts' to see keyboard shortcuts", Colors.BRIGHT_BLUE)
    print_colored("🔍 Use 'status' to check system status", Colors.BRIGHT_BLUE)
    
    # Setup terminal for better experience
    terminal_ready = setup_terminal()
    if terminal_ready:
        print_status_bar("Terminal enhanced with macOS keyboard shortcuts", "INFO")
        print_colored("✅ Text editing shortcuts enabled: Cmd+Delete, Option+Arrow, etc.", Colors.BRIGHT_GREEN)
    else:
        print_status_bar("Basic terminal mode (readline not available)", "WARNING")
    
    interaction_count = 0
    keep_running = True
    
    while keep_running:
        try:
            # Create a simple, clean prompt to avoid readline display issues with colors
            # Colored prompts can cause text overlap when using history navigation (↑/↓)
            interaction_count += 1
            prompt = f"\n[{interaction_count}] Browser Agent> "
            
            try:
                # Use input() without cursor interference to preserve history navigation
                user_query = input(prompt).strip()
            except EOFError:
                # Handle Ctrl+D gracefully
                print("\n")
                print_status_bar("Input stream closed", "INFO")
                break
            except KeyboardInterrupt:
                # Handle Ctrl+C in the input prompt
                print("\n")
                print_status_bar("Interrupted", "WARNING")
                try:
                    confirm = input("Are you sure you want to exit? (y/N): ")
                    if confirm.lower() in ['y', 'yes']:
                        break
                    else:
                        continue
                except (EOFError, KeyboardInterrupt):
                    print("\nForced exit")
                    break
            
            if not user_query:
                continue
            
            # Handle special commands
            if user_query.lower() in ['exit', 'quit', 'q']:
                print_status_bar("Goodbye! 👋", "INFO")
                break
            elif user_query.lower() == 'help':
                print_interactive_help()
                continue
            elif user_query.lower() in ['shortcuts', 'keys', 'keyboard']:
                print_keyboard_shortcuts()
                continue
            elif user_query.lower() == 'status':
                print_system_status()
                continue
            elif user_query.lower() == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
                # Reset interaction count after clear
                interaction_count = 0
                continue
            
            print_status_bar(f"Processing instruction: {user_query}", "PROGRESS")
            start_time = datetime.now()
            
            try:
                response = agent_executor.invoke(user_query)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                print_status_bar(f"Execution completed in {duration:.2f} seconds", "SUCCESS")
                print_agent_response(response.get("output", "No output received"))
                    
            except Exception as e:
                print_status_bar(f"Execution error: {str(e)}", "ERROR")
                if args.verbose:
                    traceback.print_exc()
                print_colored("💡 The agent encountered an error but the browser will remain open.", Colors.BRIGHT_YELLOW)
                print_colored("   You can continue with a new instruction.", Colors.BRIGHT_YELLOW)
                
        except Exception as unexpected_error:
            print_status_bar(f"Unexpected error in interactive loop: {str(unexpected_error)}", "ERROR")
            if args.verbose:
                traceback.print_exc()
            print("💡 An unexpected error occurred. You can try again or exit.")
    
    # Enhanced cleanup with options
    print_section_header("Cleanup")
    if 'playwright' in locals() and 'browser' in locals():
        close_input = input("Disconnect from Chrome? (y/N): ")
            
        if close_input.lower() in ['y', 'yes']:
            print_status_bar("Disconnecting...", "PROGRESS")
            try:
                close_browser(playwright, browser)
                print_status_bar("Disconnected - Chrome remains open", "SUCCESS")
            except Exception as e:
                print_status_bar(f"Disconnect warning: {str(e)}", "WARNING")
        else:
            print_status_bar("Connection maintained - Chrome stays open", "INFO")
    
    return True

def print_interactive_help():
    """Print help for interactive mode with colors."""
    print(f"""
{Colors.BRIGHT_CYAN}🔧 INTERACTIVE COMMANDS:{Colors.RESET}
  {Colors.BRIGHT_GREEN}help{Colors.RESET}     Show this help message
  {Colors.BRIGHT_GREEN}status{Colors.RESET}   Show system status
  {Colors.BRIGHT_GREEN}clear{Colors.RESET}    Clear the screen
  {Colors.BRIGHT_RED}exit{Colors.RESET}     Exit the Browser Agent
  {Colors.BRIGHT_RED}quit{Colors.RESET}     Exit the Browser Agent
  {Colors.BRIGHT_RED}q{Colors.RESET}        Exit the Browser Agent

{Colors.BRIGHT_YELLOW}💡 TIPS:{Colors.RESET}
  - Be specific about what you want the browser to do
  - Use natural language: {Colors.BRIGHT_WHITE}"Go to Google and search for Python"{Colors.RESET}
  - The agent can handle complex multi-step tasks
  - Use {Colors.BRIGHT_MAGENTA}Ctrl+C{Colors.RESET} to interrupt long-running tasks
    """)

def print_system_status():
    """Print current system status with colors."""
    from ..utils import get_system_info
    
    print_section_header("System Status")
    info = get_system_info()
    
    print_colored(f"🔧 Version: {info['version']}", Colors.BRIGHT_GREEN)
    print_colored(f"🐍 Python: {info['python_version']}", Colors.BRIGHT_BLUE)
    print_colored(f"🖥️  Platform: {info['platform']}", Colors.BRIGHT_CYAN)
    print_colored(f"🌐 Chrome Processes: {info['chrome_processes']}", Colors.BRIGHT_YELLOW)
    
    api_status = "✅ Configured" if info['api_key_configured'] else "❌ Missing"
    api_color = Colors.BRIGHT_GREEN if info['api_key_configured'] else Colors.BRIGHT_RED
    print_colored(f"🔑 API Key: {api_status}", api_color)
    
    print_colored(f"📁 Debug Profiles: {len(info['debug_profiles'])}", Colors.BRIGHT_MAGENTA)
    print_colored(f"🗂️  Temp Profiles: {len(info['temp_profiles'])}", Colors.BRIGHT_CYAN)
    
    if info['chrome_processes'] > 0:
        print_colored("✅ Chrome is running", Colors.BRIGHT_GREEN)
    else:
        print_colored("⚠️  Chrome is not running", Colors.BRIGHT_YELLOW)

def print_keyboard_shortcuts():
    """Print available keyboard shortcuts for text editing."""
    print_section_header("Keyboard Shortcuts")
    print(f"""
{Colors.BRIGHT_CYAN}⌨️  TEXT NAVIGATION:{Colors.RESET}
  {Colors.BRIGHT_GREEN}Option + →{Colors.RESET}     Move cursor forward by word
  {Colors.BRIGHT_GREEN}Option + ←{Colors.RESET}     Move cursor backward by word  
  {Colors.BRIGHT_GREEN}Cmd + →{Colors.RESET}       Move cursor to end of line
  {Colors.BRIGHT_GREEN}Cmd + ←{Colors.RESET}       Move cursor to beginning of line
  {Colors.BRIGHT_GREEN}Ctrl + A{Colors.RESET}      Move cursor to beginning of line
  {Colors.BRIGHT_GREEN}Ctrl + E{Colors.RESET}      Move cursor to end of line

{Colors.BRIGHT_CYAN}🗑️  TEXT DELETION:{Colors.RESET}
  {Colors.BRIGHT_RED}Cmd + Delete{Colors.RESET}       Delete from cursor to end of line
  {Colors.BRIGHT_RED}Option + Delete{Colors.RESET}    Delete word forward
  {Colors.BRIGHT_RED}Option + Backspace{Colors.RESET} Delete word backward
  {Colors.BRIGHT_RED}Ctrl + K{Colors.RESET}           Delete from cursor to end of line
  {Colors.BRIGHT_RED}Ctrl + U{Colors.RESET}           Delete entire line
  {Colors.BRIGHT_RED}Ctrl + W{Colors.RESET}           Delete word backward

{Colors.BRIGHT_CYAN}📚 HISTORY:{Colors.RESET}
  {Colors.BRIGHT_YELLOW}↑ / ↓{Colors.RESET}         Navigate command history
  {Colors.BRIGHT_YELLOW}Ctrl + R{Colors.RESET}      Reverse search through history
  {Colors.BRIGHT_YELLOW}Ctrl + S{Colors.RESET}      Forward search through history  
  {Colors.BRIGHT_YELLOW}Ctrl + P/N{Colors.RESET}    Previous/Next history (alternative)
  {Colors.BRIGHT_YELLOW}Tab{Colors.RESET}           Auto-completion (where available)

{Colors.BRIGHT_CYAN}🔧 CONTROL:{Colors.RESET}
  {Colors.BRIGHT_MAGENTA}Ctrl + C{Colors.RESET}      Interrupt current operation
  {Colors.BRIGHT_MAGENTA}Ctrl + D{Colors.RESET}      Exit (EOF)

{Colors.BRIGHT_YELLOW}💡 TIP:{Colors.RESET} These shortcuts work in all text input fields in the CLI!
    """)
