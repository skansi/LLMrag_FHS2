from playwright.sync_api import sync_playwright
import time
import os
import re

def scrape_single_html_absolute_links(url, output_file="index.html", wait_time=7):
    """
    Saves a single HTML file, converting all relative asset links 
    (href, src) to absolute URLs.
    
    This fixes issues with root-relative paths and viewport-based 
    styling by simulating a large screen.
    """
    try:
        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            
        print(f"Initializing browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            
            # --- FIX: Set viewport in new_context() ---
            print("Setting viewport to 1920x1080 for the browser context...")
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Page creation is now clean
            page = context.new_page()
            # ------------------------------------------
            
            print(f"Fetching content from: {url}")
            page.goto(url, wait_until="networkidle")
            
            print(f"Waiting {wait_time} seconds for dynamic/jQuery content...")
            time.sleep(wait_time)
            
            # Convert all links to absolute
            print("Converting all relative links (href, src) to absolute...")
            js_converter_script = """
            () => {
                // Select all elements that can have external links
                const selectors = 'link[href], script[src], img[src], a[href], source[src]';
                document.querySelectorAll(selectors).forEach(el => {
                    // Check if it's 'href' or 'src'
                    const attr = el.hasAttribute('href') ? 'href' : 'src';
                    const url = el.getAttribute(attr);
                    
                    if (url) {
                        // Use the browser's URL constructor to resolve the link
                        const absoluteUrl = new URL(url, document.baseURI).href;
                        el.setAttribute(attr, absoluteUrl);
                    }
                });
            }
            """
            page.evaluate(js_converter_script)
            print("Link conversion complete.")

            # Get the final HTML content
            print("Grabbing final HTML content...")
            html_content = page.content()
            
            # Save the modified HTML
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            browser.close()
            print(f"\nSuccessfully saved to: {output_file}")
            print("Run this file with VS Code's 'Live Server'.")
            
    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
if __name__ == "__main__":
    url = "https://www.fhs.unizg.hr/"
    
    # Create a specific directory for this
    output_dir = "fhs_live_html_absolute"
    output_path = os.path.join(output_dir, "index.html")
    
    # Using a slightly longer wait time for this older site
    scrape_single_html_absolute_links(url, output_path, wait_time=1)