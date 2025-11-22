"""
Page analyzer for examining web page content and structure.
"""

import time
from agent.tools import tool

# Global variables
page = None
page_elements = []

def initialize(browser_page):
    """Initialize the page analyzer."""
    global page
    page = browser_page

@tool
def analyze_page():
    """
    Analyzes the current page and returns all visible content and interactive elements.
    
    Extracts buttons, links, inputs, text content with unique IDs for each element.
    Use this tool to see what's on the page before interacting with it.
    
    Returns: Formatted list of page elements with:
    - Element IDs (for precise targeting)
    - Element types (button, link, input, etc.)
    - Visible text and descriptions
    - Position information
    
    Run after navigation or page changes to refresh element information.
    """
    global page_elements
    try:
            # Initialize page elements array to store detailed information
            page_elements = []

            print("Analyzing page content...")
            
            # Use JavaScript to directly analyze the DOM - optimized version
            page_content = page.evaluate("""
            () => {
                // Fast visibility check - combines viewport and visibility checks
                function isVisibleInViewport(el) {
                    const rect = el.getBoundingClientRect();
                    
                    // Quick dimension check
                    if (rect.width <= 0 || rect.height <= 0) return false;
                    
                    // Quick viewport check
                    if (rect.bottom <= 0 || rect.top >= window.innerHeight || 
                        rect.right <= 0 || rect.left >= window.innerWidth) return false;
                    
                    // Only check computed style if element passed basic checks
                    const style = window.getComputedStyle(el);
                    return style.display !== 'none' && 
                           style.visibility !== 'hidden' && 
                           parseFloat(style.opacity) > 0.1;
                }
                
                // Fast element type detection - enhanced version
                function getElementType(el) {
                    const tag = el.tagName.toLowerCase();
                    const type = el.type?.toLowerCase();
                    const role = el.getAttribute('role')?.toLowerCase();
                    
                    // Quick lookups for common elements
                    if (tag === 'a') return 'link';
                    if (tag === 'button') return 'button';
                    if (tag === 'select') return 'dropdown';
                    if (tag === 'textarea') return 'textarea';
                    
                    if (tag === 'input') {
                        if (type === 'submit' || type === 'button' || type === 'reset') return 'button';
                        if (type === 'checkbox') return 'checkbox';
                        if (type === 'radio') return 'radio';
                        if (type === 'text' || type === 'email' || type === 'password' || type === 'search') return 'input';
                        return 'input'; // Default for other input types
                    }
                    
                    // Check ARIA roles
                    if (role === 'button') return 'button';
                    if (role === 'link') return 'link';
                    if (role === 'checkbox') return 'checkbox';
                    if (role === 'radio') return 'radio';
                    if (role === 'textbox' || role === 'searchbox') return 'input';
                    if (role === 'combobox' || role === 'listbox') return 'dropdown';
                    if (role === 'tab') return 'tab';
                    
                    // Check for clickable elements with enhanced detection
                    const style = window.getComputedStyle(el);
                    const hasClickHandler = el.onclick || el.getAttribute('onclick');
                    const isPointer = style.cursor === 'pointer';
                    
                    if ((tag === 'div' || tag === 'span') && (hasClickHandler || isPointer)) {
                        if (el.getAttribute('aria-haspopup') === 'true') return 'dropdown';
                        if (el.classList.contains('btn') || el.classList.contains('button')) return 'button';
                        return 'button';
                    }
                    
                    if (tag === 'label') return 'label';
                    if (tag === 'img' && (isPointer || hasClickHandler)) return 'image';
                    if (['h1','h2','h3','h4','h5','h6'].includes(tag) && (isPointer || hasClickHandler)) return 'header';
                    
                    // Check for general interactivity
                    if (hasClickHandler || el.getAttribute('tabindex') === '0' || isPointer) return 'interactive';
                    
                    return null;
                }
                
                // Get all attributes of an element
                function getElementAttributes(el) {
                    const result = {};
                    for (const attr of el.attributes) {
                        result[attr.name] = attr.value;
                    }
                    return result;
                }
                
                // Generate CSS selector for element - enhanced version
                function generateSelector(el) {
                    if (!el) return '';
                    
                    // Priority 1: Use ID if available and unique
                    if (el.id && el.id.trim()) {
                        const escapedId = CSS.escape(el.id);
                        if (document.querySelectorAll('#' + escapedId).length === 1) {
                            return '#' + escapedId;
                        }
                    }
                    
                    // Priority 2: Use specific attributes that are likely unique
                    const uniqueAttrs = ['data-testid', 'data-cy', 'data-test', 'name'];
                    for (const attr of uniqueAttrs) {
                        const value = el.getAttribute(attr);
                        if (value && value.trim()) {
                            const selector = `[${attr}="${CSS.escape(value)}"]`;
                            if (document.querySelectorAll(selector).length === 1) {
                                return selector;
                            }
                        }
                    }
                    
                    // Priority 3: Build a path-based selector
                    let selector = el.tagName.toLowerCase();
                    
                    // Add type for inputs
                    if (el.tagName.toLowerCase() === 'input' && el.type) {
                        selector += `[type="${el.type}"]`;
                    }
                    
                    // Add classes (limit to 2 most specific ones)
                    if (el.classList && el.classList.length > 0) {
                        const classes = Array.from(el.classList)
                            .filter(cls => cls.length > 0 && !cls.match(/^(ng-|_|css-)/)) // Skip framework classes
                            .slice(0, 2);
                        if (classes.length > 0) {
                            selector += '.' + classes.map(cls => CSS.escape(cls)).join('.');
                        }
                    }
                    
                    // Add nth-child if needed for uniqueness
                    if (document.querySelectorAll(selector).length > 1) {
                        const parent = el.parentElement;
                        if (parent) {
                            const siblings = Array.from(parent.children).filter(child => 
                                child.tagName === el.tagName && 
                                (el.className === child.className || (!el.className && !child.className))
                            );
                            if (siblings.length > 1) {
                                const index = siblings.indexOf(el) + 1;
                                selector += `:nth-child(${index})`;
                            }
                        }
                    }
                    
                    // Final fallback: add parent context if still not unique
                    if (document.querySelectorAll(selector).length > 1 && el.parentElement) {
                        const parentTag = el.parentElement.tagName.toLowerCase();
                        const parentClass = el.parentElement.classList.length > 0 ? 
                            '.' + Array.from(el.parentElement.classList)[0] : '';
                        selector = parentTag + parentClass + ' > ' + selector;
                    }
                    
                    return selector;
                }
                
                // Get parent info for context
                function getParentInfo(el) {
                    if (!el || !el.parentElement) return null;
                    
                    const parent = el.parentElement;
                    return {
                        tagName: parent.tagName.toLowerCase(),
                        id: parent.id || '',
                        className: parent.className || '',
                        text: cleanText(parent.innerText || parent.textContent || '').substring(0, 50)
                    };
                }
                
                // Find all modal/dialog/popup elements that are visible in viewport
                function findPopups() {
                    // Expanded selectors for modals/dialogs/popups
                    const selectors = [
                        // ARIA roles and attributes
                        '[role=dialog]', '[role=alertdialog]', '[role=drawer]', '[role=tooltip]', '[role=menu]',
                        '[aria-modal="true"]', '[aria-haspopup="dialog"]', '[aria-haspopup="menu"]',
                        
                        // Data attributes
                        '[data-modal="true"]', '[data-popup="true"]', '[data-dialog="true"]', '[data-overlay="true"]',
                        
                        // Common class patterns
                        '.modal', '.dialog', '.popup', '.overlay', '.pop-up', '.popover', '.tooltip', '.drawer',
                        '.toast', '.notification', '.alert-box',
                        
                        // Framework-specific selectors
                        '.ant-modal', '.ant-drawer', '.ant-popover', // Ant Design
                        '.MuiDialog-root', '.MuiDrawer-root', '.MuiPopover-root', // Material UI
                        '.ReactModal__Content', // React Modal
                        '.modal-dialog', '.modal-content', '.popover', // Bootstrap
                        '.chakra-modal', '.chakra-dialog', // Chakra UI
                        '.ui.modal', '.ui.popup', // Semantic UI
                        '.v-dialog', '.v-menu', // Vuetify
                        
                        // Generic patterns
                        '[class*="modal"]', '[class*="dialog"]', '[class*="popup"]', '[class*="overlay"]',
                        '[class*="drawer"]', '[class*="toast"]', '[class*="tooltip"]', '[class*="popover"]'
                    ];
                    
                    // Find all visible popups in viewport
                    const popups = [];
                    
                    // Check for elements matching our selectors
                    for (const sel of selectors) {
                        for (const el of document.querySelectorAll(sel)) {
                            if (isVisibleInViewport(el)) popups.push(el);
                        }
                    }
                    
                    // Check for fixed/absolute positioned elements with high z-index
                    document.querySelectorAll('div, section, aside').forEach(el => {
                        if (!popups.includes(el) && isVisibleInViewport(el)) {
                            const style = window.getComputedStyle(el);
                            const position = style.position;
                            const zIndex = parseInt(style.zIndex) || 0;
                            
                            // Fixed/absolute with high z-index are often modals/popups
                            if ((position === 'fixed' || position === 'absolute') && zIndex > 10) {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 50 && rect.height > 50) { // Reasonable size check
                                    popups.push(el);
                                }
                            }
                        }
                    });
                    
                    // Check for elements near known backdrops (often indicates a modal)
                    const backdrops = document.querySelectorAll('.modal-backdrop, .overlay, .backdrop, .dimmer, [class*="backdrop"], [class*="overlay"]');
                    for (const backdrop of backdrops) {
                        if (isVisibleInViewport(backdrop)) {
                            const backdropRect = backdrop.getBoundingClientRect();
                            const viewportCenter = {
                                x: window.innerWidth / 2,
                                y: window.innerHeight / 2
                            };
                            
                            // Look for visible centered elements - often these are modals related to backdrops
                            document.querySelectorAll('div, section, aside').forEach(el => {
                                if (!popups.includes(el) && isVisibleInViewport(el)) {
                                    const rect = el.getBoundingClientRect();
                                    const elementCenter = {
                                        x: rect.left + rect.width / 2,
                                        y: rect.top + rect.height / 2
                                    };
                                    
                                    // Is it centered, reasonable size, and contained within backdrop?
                                    const isCentered = Math.abs(elementCenter.x - viewportCenter.x) < viewportCenter.x / 3 &&
                                                      Math.abs(elementCenter.y - viewportCenter.y) < viewportCenter.y / 3;
                                    
                                    if (isCentered && rect.width > 50 && rect.height > 50) {
                                        popups.push(el);
                                    }
                                }
                            });
                        }
                    }
                    
                    // Remove duplicates
                    return Array.from(new Set(popups));
                }

                // Fast text cleaning
                function cleanText(text) {
                    return text ? text.replace(/\\s+/g, ' ').trim() : '';
                }
                
                // Simple popup detection - enhanced but efficient
                function findVisiblePopups() {
                    const popups = [];
                    const modalSelectors = [
                        '[role="dialog"]', '[role="alertdialog"]', '[aria-modal="true"]',
                        '.modal', '.dialog', '.popup', '.overlay', '.pop-up', '.popover',
                        '.ant-modal', '.MuiDialog-root', '.ReactModal__Content', '.modal-dialog',
                        '[class*="modal"]', '[class*="dialog"]', '[class*="popup"]'
                    ];
                    
                    for (const selector of modalSelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const el of elements) {
                            if (isVisibleInViewport(el) && !popups.includes(el)) {
                                popups.push(el);
                            }
                        }
                    }
                    
                    // Quick check for high z-index fixed/absolute elements
                    const candidates = document.querySelectorAll('div[style*="position"], section[style*="position"]');
                    for (const el of candidates) {
                        if (isVisibleInViewport(el) && !popups.includes(el)) {
                            const style = window.getComputedStyle(el);
                            if ((style.position === 'fixed' || style.position === 'absolute') && 
                                parseInt(style.zIndex) > 10) {
                                const rect = el.getBoundingClientRect();
                                if (rect.width > 100 && rect.height > 100) {
                                    popups.push(el);
                                }
                            }
                        }
                    }
                    
                    return popups;
                }
                
                // Extract content efficiently - enhanced functionality
                function extractContent() {
                    const content = [];
                    const elements = [];
                    let elementId = 0;
                    
                    // Get all potentially interactive elements in one query - expanded
                    const interactiveSelectors = 'a, button, input, select, textarea, [onclick], [role="button"], [role="link"], [tabindex="0"], label, img[onclick], div[onclick], span[onclick]';
                    const allElements = document.querySelectorAll(interactiveSelectors);
                    
                    for (const el of allElements) {
                        if (!isVisibleInViewport(el)) continue;
                        
                        const type = getElementType(el);
                        if (!type) continue;
                        
                        // Enhanced text extraction
                        let text = cleanText(el.textContent || el.value || el.placeholder || 
                                           el.getAttribute('aria-label') || el.getAttribute('title') || 
                                           el.alt || type);
                        
                        // For input fields without text, use name or type
                        if ((type === 'input' || type === 'textarea') && !text) {
                            text = el.getAttribute('name') || el.getAttribute('placeholder') || type;
                        }
                        
                        if (text.length > 100) text = text.substring(0, 100) + '...';
                        
                        // Skip if type matches text exactly
                        if (text === type) continue;
                        
                        // Generate CSS selector for this element
                        const cssSelector = generateSelector(el);
                        
                        content.push(`[${elementId}][${type}][${cssSelector}]${text}`);
                        
                        // Store enhanced element info
                        const rect = el.getBoundingClientRect();
                        elements.push({
                            id: elementId,
                            tagName: el.tagName,
                            type: type,
                            text: text,
                            cssSelector: cssSelector,
                            x: rect.left + window.pageXOffset,
                            y: rect.top + window.pageYOffset,
                            width: rect.width,
                            height: rect.height,
                            center_x: rect.left + rect.width/2 + window.pageXOffset,
                            center_y: rect.top + rect.height/2 + window.pageYOffset,
                            isDisabled: el.disabled || el.hasAttribute('disabled'),
                            attributes: {
                                id: el.id || '',
                                class: el.className || '',
                                href: el.href || '',
                                value: el.value || '',
                                placeholder: el.placeholder || ''
                            }
                        });
                        
                        elementId++;
                    }
                    
                    // Add visible text content (non-interactive) - improved
                    const textElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, span, div, li, td, th');
                    for (const el of textElements) {
                        if (!isVisibleInViewport(el)) continue;
                        
                        // Only get direct text content (not from children)
                        let ownText = '';
                        for (const child of el.childNodes) {
                            if (child.nodeType === Node.TEXT_NODE) {
                                ownText += child.textContent;
                            }
                        }
                        ownText = cleanText(ownText);
                        
                        // Better filtering for meaningful text
                        if (ownText && ownText.length > 1 && ownText.length < 200 && 
                            !ownText.match(/^\\s*[\\d\\W]*\\s*$/)) { // Skip pure numbers/symbols
                            content.push(ownText);
                        }
                    }
                    
                    // Check for visible popups - enhanced processing
                    const popups = findVisiblePopups();
                    if (popups.length > 0) {
                        content.push('--- Modal/Popup Detected ---');
                        // Process popup content with same detail level
                        for (const popup of popups.slice(0, 2)) { // Process up to 2 popups
                            const popupElements = popup.querySelectorAll(interactiveSelectors);
                            for (const el of popupElements) {
                                if (!isVisibleInViewport(el)) continue;
                                const type = getElementType(el);
                                if (!type) continue;
                                let text = cleanText(el.textContent || el.value || el.placeholder || 
                                                   el.getAttribute('aria-label') || type);
                                if (text !== type && text.length > 0) {
                                    const cssSelector = generateSelector(el);
                                    content.push(`[${elementId}][${type}][${cssSelector}]${text}`);
                                    
                                    // Store popup element info too
                                    const rect = el.getBoundingClientRect();
                                    elements.push({
                                        id: elementId,
                                        tagName: el.tagName,
                                        type: type,
                                        text: text,
                                        cssSelector: cssSelector,
                                        x: rect.left + window.pageXOffset,
                                        y: rect.top + window.pageYOffset,
                                        center_x: rect.left + rect.width/2 + window.pageXOffset,
                                        center_y: rect.top + rect.height/2 + window.pageYOffset,
                                        isPopup: true
                                    });
                                    
                                    elementId++;
                                }
                            }
                        }
                        content.push('--- End of Popup ---');
                    }
                    
                    return { content, elements };
                }
                
                return extractContent();
            }
            """)
            
            # Store elements and process content with original formatting
            page_elements = page_content['elements']
            
            # Post-process the content - clean up formatting and structure
            result = []
            current_line = ""
            
            # Add each item, grouping related content on the same line
            for item in page_content['content']:
                # Skip elements where type matches display text exactly
                if item.startswith('['):
                    parts = item.split(']', 3)  # Changed to 3 to handle [ID][type][selector]Text
                    if len(parts) >= 4:  # Now we have ID, type, selector, and text
                        element_type = parts[1][1:]
                        display_text = parts[3]  # Text is now the 4th part
                        if display_text.strip() == element_type:
                            continue
                
                # Start a new line for interactive elements or if current line is empty
                if item.startswith('[') or not current_line:
                    if current_line:
                        result.append(current_line)
                    current_line = item
                # Keep short content items together if they're related
                elif len(item) < 30 and len(current_line) + len(item) + 1 < 80:
                    current_line += " " + item
                # Otherwise start a new line
                else:
                    result.append(current_line)
                    current_line = item
            
            # Don't forget the last line
            if current_line:
                result.append(current_line)
            
            # Format the result
            formatted_result = "\\n".join(result).strip()
            return formatted_result
            
    except Exception as e:
        return f"Error analyzing page: {str(e)}"