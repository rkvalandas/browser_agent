"""
Navigator module for browser page navigation.
"""

import time
from agent.tools import tool

# Global variable to store the page
page = None

def initialize(browser_page):
    """Initialize the browser navigator."""
    global page
    page = browser_page

@tool
def navigate(url) -> str:
    """
    Navigates browser to a specified URL.
    
    Input (url):
    - Full URL: "https://www.example.com"
    - Domain only: "example.com" (https:// added automatically)
    
    Returns: Status message with the final URL reached.
    """
    try:
        # Clean the URL - remove backticks and other formatting characters
        url = url.replace('`', '').strip()
        
        # Handle cases with duplicate protocol prefixes
        if (url.count('http') > 1):
            # Find the last occurrence of http:// or https://
            last_http_index = max(url.rfind('http://'), url.rfind('https://'))
            if (last_http_index >= 0):
                url = url[last_http_index:]
        
        # Ensure URL has a protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        print(f"Attempting to navigate to: {url}")
        
        # STEP 1: Direct navigation attempt
        try:
            print(f"Trying direct navigation to {url}")
            page.goto(url, timeout=50000)
            current_url = page.url
            
            # Check if navigation was successful
            if not (current_url.startswith("http") and not "about:blank" in current_url):
                raise Exception("Direct navigation not successful")
            time.sleep(1.5)  # Allow time for page to load
            
            print(f"Direct navigation successful, now at: {current_url}")
            return f"Navigated to {url} - Current page: {current_url}"
            
        except Exception as direct_nav_error:
            print(f"Direct navigation failed: {direct_nav_error}")
    
    except Exception as e:
        print(f"Critical navigation error: {e}")
        return f"Error navigating to {url}: {str(e)}"

@tool
def go_back() -> str:
    """
    Navigates back to the previous page in browser history.
    
    Simulates clicking the browser back button. Use when you need to return
    to a previously visited page.
    
    Returns: Status message indicating success or if history is unavailable.
    """
    try:
        # Store current URL to verify navigation
        current_url = page.url
        
        # Check if we can go back
        can_go_back = page.evaluate("() => window.history.length > 1")
        
        if not can_go_back:
            return "Cannot go back - no previous page in history"
        
        print("Navigating back to previous page...")
        
        # Try using browser back button first (most reliable)
        page.go_back(wait_until="domcontentloaded", timeout=10000)
        
        # Wait for navigation to complete
        time.sleep(1.5)
        
        # Verify we actually navigated to a different page
        new_url = page.url
        if (new_url == current_url):
            # If URL didn't change, try alternative method
            print("Back navigation didn't change URL, trying alternative method...")
            page.evaluate("() => window.history.back()")
            time.sleep(1.5)
            new_url = page.url
        
        # Final verification
        if (new_url != current_url):
            print(f"Successfully navigated back to: {new_url}")
            return f"Navigated back to previous page: {new_url}"
        else:
            return "Back navigation attempted but URL remains unchanged"
            
    except Exception as e:
        print(f"Error navigating back: {str(e)}")
        return f"Error navigating back: {str(e)}"