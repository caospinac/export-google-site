import os
import json
import argparse
import tempfile
from pathlib import Path
from slugify import slugify
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

OUTPUT_DIR = "google_site_export"
COOKIES_FILE = "cookies.json"

def sanitize_filename(text):
    return slugify(text, separator="_")

def extract_path_from_url(url, base_url):
    """Extract the relevant path from URL for filename"""
    try:
        # Parse both URLs
        parsed_url = urlparse(url)
        parsed_base = urlparse(base_url)
        
        # Get the path after the base site path
        full_path = parsed_url.path
        base_path = parsed_base.path
        
        # Remove the base path to get the relative path
        if full_path.startswith(base_path):
            relative_path = full_path[len(base_path):].strip('/')
        else:
            relative_path = full_path.strip('/')
        
        # If no relative path, use the last segment of the full path
        if not relative_path:
            path_segments = full_path.strip('/').split('/')
            relative_path = path_segments[-1] if path_segments else 'home'
        
        # Replace slashes with underscores and sanitize
        filename_base = relative_path.replace('/', '_')
        return sanitize_filename(filename_base) if filename_base else 'page'
        
    except Exception as e:
        return 'unknown_page'

def create_output_dir():
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def load_cookies(context):
    """Load cookies from JSON file"""
    if not os.path.exists(COOKIES_FILE):
        print(f" File {COOKIES_FILE} not found")
        print(" Export cookies from Chrome using an extension like 'Get cookies.txt'")
        return False
    
    try:
        with open(COOKIES_FILE, 'r') as f:
            cookies_data = json.load(f)
        
        # Convert cookies format if needed
        cookies = []
        for cookie in cookies_data:
            cookie_dict = {
                'name': cookie.get('name'),
                'value': cookie.get('value'), 
                'domain': cookie.get('domain'),
                'path': cookie.get('path', '/'),
                'secure': cookie.get('secure', False),
                'httpOnly': cookie.get('httpOnly', False)
            }
            
            # Handle expiration
            if 'expirationDate' in cookie:
                cookie_dict['expires'] = int(cookie['expirationDate'])
            
            cookies.append(cookie_dict)
        
        context.add_cookies(cookies)
        print(f" {len(cookies)} cookies loaded")
        return True
        
    except Exception as e:
        print(f" Error loading cookies: {e}")
        return False

def export_google_site(base_url):
    create_output_dir()

    with sync_playwright() as p:
        print(" Starting browser...")
        
        # Create temp directory for session
        temp_dir = tempfile.mkdtemp(prefix="chrome-export-")
        
        # Launch Chrome in headless mode (more lightweight)
        context = p.chromium.launch_persistent_context(
            user_data_dir=temp_dir,
            headless=True,  # No browser window
            channel="chrome",  # Use Chrome instead of Chromium
            args=[
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor",
                "--no-sandbox",
                "--disable-dev-shm-usage"  # Reduce memory usage
            ]
        )
        
        # Load cookies before navigation
        cookies_loaded = load_cookies(context)
        
        if not cookies_loaded:
            print(" Could not load cookies. Script terminated.")
            print(" Make sure you have a valid cookies.json file")
            context.close()
            return
        
        page = context.new_page()
        
        print(" Navigating to site...")
        page.goto(base_url)
        page.wait_for_load_state("networkidle")
        
        # Check if authentication worked
        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            print(" Cookies didn't work - authentication required")
            print(" Verify that cookies haven't expired")
            print(" Re-export cookies from your browser")
            context.close()
            return
        
        print(" Authentication successful with cookies")

        # Find menu items
        selectors = [
            "nav ul li a",
            "[role='navigation'] a",
            ".navigation a", 
            "aside a",
            ".sidebar a",
            "a[href*='sites.google.com']"
        ]
        
        menu_items = None
        working_selector = None
        for selector in selectors:
            try:
                items = page.locator(selector)
                if items.count() > 0:
                    menu_items = items
                    working_selector = selector
                    print(f" Menu found: {selector}")
                    break
            except:
                continue
        
        if not menu_items or menu_items.count() == 0:
            print(" No menu elements found")
            context.close()
            return

        count = menu_items.count()
        print(f" Found {count} sections to export")
        print()  # Empty line for better formatting

        processed = 0
        skipped = 0

        # Get all URLs first
        urls_to_process = []
        for i in range(count):
            try:
                item = menu_items.nth(i)
                label = item.inner_text().strip()
                href = item.get_attribute('href')
                if label and href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = f"https://sites.google.com{href}"
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = f"{base_url.rstrip('/')}/{href}"
                    
                    urls_to_process.append({
                        'index': i + 1,
                        'label': label,
                        'url': full_url
                    })
            except:
                continue

        # Process each URL by direct navigation
        for info in urls_to_process:
            try:
                label = info['label']
                url = info['url']
                index = info['index']
                
                # Extract filename from URL path
                filename_base = extract_path_from_url(url, base_url)
                filename = filename_base + ".pdf"
                pdf_path = os.path.join(OUTPUT_DIR, filename)
                
                # Check if file already exists
                if os.path.exists(pdf_path):
                    print(f"[{index}/{count}] {label} - SKIPPED (already exists)")
                    skipped += 1
                    continue
                
                # Simple progress indicator
                print(f"[{index}/{count}] {label}")
                
                # Navigate directly to the URL
                page.goto(url)
                page.wait_for_load_state("networkidle", timeout=20000)
                
                # Generate PDF
                page.pdf(
                    path=pdf_path,
                    format="A4",
                    print_background=True,
                    margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
                )
                processed += 1
                
            except Exception as e:
                print(f" Error in element {index}: {str(e)[:50]}...")
                continue

        print(f" Export completed - {processed} files processed, {skipped} files skipped, saved to '{OUTPUT_DIR}/'")
        context.close()

def main():
    parser = argparse.ArgumentParser(description="Google Sites exporter with cookies")
    parser.add_argument("--url", required=True, help="URL of the Google Sites")
    
    args = parser.parse_args()
    export_google_site(args.url)

if __name__ == "__main__":
    main()
