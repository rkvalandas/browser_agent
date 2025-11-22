from playwright.sync_api import sync_playwright

def inject_cursor_script():
    return """
    // Create a custom cursor element
    const cursor = document.createElement('div');
    cursor.id = 'ai-agent-cursor';
    cursor.style.position = 'absolute';
    cursor.style.width = '20px';
    cursor.style.height = '20px';
    cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
    cursor.style.border = '2px solid red';
    cursor.style.borderRadius = '50%';
    cursor.style.transform = 'translate(-50%, -50%)';
    cursor.style.pointerEvents = 'none';
    cursor.style.zIndex = '999999';
    cursor.style.transition = 'left 0.05s, top 0.05s';
    
    // Add cursor to the page
    document.addEventListener('DOMContentLoaded', function() {
        document.body.appendChild(cursor);
    });
    
    // If page already loaded, add cursor now
    if (document.body) {
        document.body.appendChild(cursor);
    }
    
    // Function to update cursor position
    window.updateAICursor = function(x, y) {
        if (cursor && document.body && document.body.contains(cursor)) {
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        } else if (document.body) {
            document.body.appendChild(cursor);
            cursor.style.left = x + 'px';
            cursor.style.top = y + 'px';
        }
    };
    """

def initialize_browser(options, connection_options=None):
    """Fast Chrome connection - connects to existing Chrome or launches it automatically.
    
    Tries to connect to existing Chrome, if fails, launches Chrome with debugging.
    """
    playwright = sync_playwright().start()
    
    # Default: connect to existing Chrome on port 9222
    cdp_endpoint = "http://localhost:9222"
    if connection_options and "cdp_endpoint" in connection_options:
        cdp_endpoint = connection_options["cdp_endpoint"]
    
    # Try to connect to existing Chrome
    browser = None
    try:
        print(f"🔗 Connecting to Chrome at {cdp_endpoint}...")
        browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
        print("✅ Connected to existing Chrome")
    except Exception as e:
        # Connection failed - launch Chrome automatically
        print(f"⚠️  Chrome not running, launching automatically...")
        
        # Launch Chrome with debugging enabled
        import subprocess
        import platform
        import time
        
        port = cdp_endpoint.split(":")[-1]
        system = platform.system()
        
        # Determine Chrome executable path
        if system == "Darwin":  # macOS
            chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        elif system == "Linux":
            chrome_path = "google-chrome"
        elif system == "Windows":
            chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        else:
            chrome_path = "google-chrome"
        
        # Build Chrome launch arguments
        chrome_args = [
            chrome_path,
            f"--remote-debugging-port={port}",
            "--user-data-dir=/tmp/chrome-debug-agent",
            "--no-first-run",
            "--no-default-browser-check"
        ]
        
        # Add headless flag if configured
        if options.get("headless", False):
            chrome_args.append("--headless=new")  # Use new headless mode
            print("🔇 Launching Chrome in headless mode")
        
        # Launch Chrome with remote debugging
        try:
            subprocess.Popen(chrome_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for Chrome to start (max 5 seconds)
            print("⏳ Waiting for Chrome to start...")
            for i in range(10):
                time.sleep(0.5)
                try:
                    browser = playwright.chromium.connect_over_cdp(cdp_endpoint)
                    print("✅ Chrome launched and connected")
                    break
                except:
                    continue
            
            if browser is None:
                raise Exception("Chrome launched but connection failed")
                
        except Exception as launch_error:
            raise Exception(f"Failed to launch Chrome: {launch_error}")
    
    # Use existing context or create new one
    if len(browser.contexts) > 0:
        context = browser.contexts[0]
    else:
        context = browser.new_context(viewport=None)
    
    # Get active page or create new one
    page = context.new_page()
    
    # Inject cursor visualization CSS and JavaScript
    page.add_init_script(inject_cursor_script())
    
    # Add script to prevent new tabs from opening
    page.add_init_script("""
        window.open = function(url, name, features) {
            console.log('Intercepted window.open call for URL:', url);
            if (url) {
                window.location.href = url;
            }
            return window;
        };
        
        // Override link behavior to prevent target="_blank"
        document.addEventListener('click', function(e) {
            const link = e.target.closest('a');
            if (link && link.target === '_blank') {
                e.preventDefault();
                console.log('Intercepted _blank link click for URL:', link.href);
                window.location.href = link.href;
            }
        }, true);
    """)
    
    # Navigate to a blank page first to ensure script loading
    page.goto('about:blank')
    
    # Ensure cursor is created and function is available
    page.evaluate("""
        () => {
            if (!document.getElementById('ai-agent-cursor')) {
                const cursor = document.createElement('div');
                cursor.id = 'ai-agent-cursor';
                cursor.style.position = 'absolute';
                cursor.style.width = '20px';
                cursor.style.height = '20px';
                cursor.style.backgroundColor = 'rgba(255, 0, 0, 0.3)';
                cursor.style.border = '2px solid red';
                cursor.style.borderRadius = '50%';
                cursor.style.transform = 'translate(-50%, -50%)';
                cursor.style.pointerEvents = 'none';
                cursor.style.zIndex = '999999';
                cursor.style.transition = 'left 0.05s, top 0.05s';
                document.body.appendChild(cursor);
            }
            
            if (typeof window.updateAICursor !== 'function') {
                window.updateAICursor = function(x, y) {
                    const cursor = document.getElementById('ai-agent-cursor');
                    if (cursor) {
                        cursor.style.left = x + 'px';
                        cursor.style.top = y + 'px';
                    } else {
                        console.error('Cursor element not found');
                    }
                };
            }
        }
    """)
    
    user_agent = page.evaluate('() => navigator.userAgent')
    print(f"Browser setup successful. User agent: {user_agent}")
    
    return playwright, browser, page

def close_browser(playwright, browser):
    """Disconnect from Chrome without closing it."""
    try:
        print("🔌 Disconnecting from Chrome (browser stays open)")
        playwright.stop()
        return "Disconnected successfully"
    except Exception as e:
        return f"Error disconnecting: {str(e)}"