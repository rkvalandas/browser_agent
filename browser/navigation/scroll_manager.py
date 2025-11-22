"""
Scroll manager for browser page scrolling and position management.
"""

import time
import random
from agent.tools import tool

# Global variable to store the page
page = None

def initialize(browser_page):
    """Initialize the scroll manager."""
    global page
    page = browser_page

@tool
def scroll(direction="down") -> str:
    """
    Scrolls the web page in the specified direction.
    
    Input (direction) - Scroll direction:
    - "down": Scroll down one viewport height (default)
    - "up": Scroll up one viewport height
    - "top": Jump to page beginning
    - "bottom": Jump to page end
    
    Returns: Status message with scroll position and whether boundary reached.
    """
    try:
        # Clean input and handle quoted strings
        print(f"Scroll direction received: {direction}")
        if isinstance(direction, str):
            direction = direction.lower().strip("'\"").strip()
        
        # Get current scroll position and page dimensions
        scroll_info = page.evaluate("""
            () => {
                return {
                    currentY: window.pageYOffset || document.documentElement.scrollTop,
                    maxY: Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    ) - window.innerHeight,
                    viewportHeight: window.innerHeight,
                    documentHeight: Math.max(
                        document.body.scrollHeight,
                        document.body.offsetHeight,
                        document.documentElement.clientHeight,
                        document.documentElement.scrollHeight,
                        document.documentElement.offsetHeight
                    )
                };
            }
        """)
        
        current_y = scroll_info['currentY']
        max_y = scroll_info['maxY']
        viewport_height = scroll_info['viewportHeight']
        
        # Handle different scroll directions with position checking
        if direction == "down":
            # Check if already at bottom (within 10px tolerance for floating point precision)
            if current_y >= max_y - 10:
                return "Already at the bottom of the page - cannot scroll down further"
            
            # Calculate how much we can actually scroll down
            remaining_scroll = max_y - current_y
            scroll_amount = min(viewport_height, remaining_scroll)
            
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            
            # Check if we reached the bottom after scrolling
            new_position = page.evaluate("window.pageYOffset || document.documentElement.scrollTop")
            if new_position >= max_y - 10:
                return "Scrolled down and reached the bottom of the page"
            else:
                return f"Scrolled down {scroll_amount}px - showing new content"
                
        elif direction == "up":
            # Check if already at top
            if current_y <= 10:
                return "Already at the top of the page - cannot scroll up further"
            
            # Calculate how much we can actually scroll up
            scroll_amount = min(viewport_height, current_y)
            
            page.evaluate(f"window.scrollBy(0, -{scroll_amount})")
            
            # Check if we reached the top after scrolling
            new_position = page.evaluate("window.pageYOffset || document.documentElement.scrollTop")
            if new_position <= 10:
                return "Scrolled up and reached the top of the page"
            else:
                return f"Scrolled up {scroll_amount}px - showing previous content"
                
        elif direction == "top":
            # Check if already at top
            if current_y <= 10:
                return "Already at the top of the page"
            
            page.evaluate("window.scrollTo(0, 0)")
            return "Scrolled to top of the page"
            
        elif direction == "bottom":
            # Check if already at bottom
            if current_y >= max_y - 10:
                return "Already at the bottom of the page"
            
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            return "Scrolled to bottom of the page"
            
        else:
            # Invalid direction - default to down with same checks
            if current_y >= max_y - 10:
                return f"Invalid direction '{direction}' - already at bottom, cannot scroll down"
            
            remaining_scroll = max_y - current_y
            scroll_amount = min(viewport_height, remaining_scroll)
            page.evaluate(f"window.scrollBy(0, {scroll_amount})")
            return f"Invalid direction '{direction}', defaulted to scrolling down {scroll_amount}px"
    except Exception as e:
        # Add more detailed error information for debugging
        print(f"Scroll error details: {e}")
        
        # Fallback to basic scroll operations without position checking
        try:
            if direction == 'top':
                page.evaluate("window.scrollTo(0, 0)")
                return "Scrolled to top (fallback method)"
            elif direction == 'bottom':
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return "Scrolled to bottom (fallback method)"
            elif direction == 'up':
                page.evaluate("window.scrollBy(0, -window.innerHeight)")
                return "Scrolled up one viewport (fallback method)"
            else:  # down or invalid
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                return f"Scrolled down one viewport (fallback method) for direction: {direction}"
        except Exception as fallback_error:
            # Ultimate fallback to JavaScript
            try:
                page.evaluate(f"""
                    () => {{
                        if ('{direction}' === 'top') window.scrollTo(0, 0);
                        else if ('{direction}' === 'bottom') window.scrollTo(0, document.body.scrollHeight);
                        else if ('{direction}' === 'up') window.scrollBy(0, -window.innerHeight);
                        else window.scrollBy(0, window.innerHeight);
                    }}
                """)
                return f"JavaScript fallback scroll used for direction: {direction}"
            except Exception as js_error:
                return f"Error scrolling: {str(e)} - All fallbacks failed: Basic({str(fallback_error)}), JS({str(js_error)})"
