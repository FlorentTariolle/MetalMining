#!/usr/bin/env python3
"""
Script to scrape genres from Metal Archives for the top bands.
Gets the list of top bands from extract_top_bands.py and scrapes their genres.
Uses Selenium with a real browser to bypass anti-bot protection.
"""

import json
import time
import argparse
import urllib.parse
from pathlib import Path
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        WEBDRIVER_MANAGER_AVAILABLE = True
    except ImportError:
        WEBDRIVER_MANAGER_AVAILABLE = False
except ImportError:
    print("Error: Missing required packages. Install with:")
    print("pip install selenium webdriver-manager")
    sys.exit(1)

# Import functions from extract_top_bands.py
from extract_top_bands import load_music_data, get_top_bands

BASE_URL = "https://www.metal-archives.com/bands/"
DEFAULT_OUTPUT = "data/bands_genres.json"
DEFAULT_TOP_N = 100
DELAY = 1  # Delay between requests in seconds


def format_band_url(band_name: str) -> str:
    """
    Format band name for Metal Archives URL.
    Metal Archives replaces spaces with underscores in URLs.
    Example: "Judas Priest" -> "Judas_Priest"
    """
    # Replace spaces with underscores as Metal Archives does
    formatted_name = band_name.replace(' ', '_')
    # URL encode special characters but keep underscores
    encoded = urllib.parse.quote(formatted_name, safe='_')
    return f"{BASE_URL}{encoded}/"


def scrape_band_genre(band_name: str, driver: webdriver.Chrome, retries: int = 2) -> str:
    """
    Scrape the genre for a band from Metal Archives using Selenium.
    Returns the genre string, or None if not found.
    """
    url = format_band_url(band_name)
    
    for attempt in range(retries):
        try:
            driver.get(url)
            
            # Wait for the page to load and check for the band_stats element
            try:
                wait = WebDriverWait(driver, 15)
                band_stats = wait.until(EC.presence_of_element_located((By.ID, "band_stats")))
                # Wait a bit more for dynamic content to load
                time.sleep(0.5)
            except TimeoutException:
                # Page might not have loaded - check if it's actually a 403 error
                current_url = driver.current_url
                page_title = driver.title.lower()
                
                # Only check for 403 if we can't find band_stats AND the URL/title suggests an error
                if ("403" in current_url or "forbidden" in page_title or 
                    "error" in page_title or "access denied" in page_title):
                    print(f"403 Forbidden/Blocked")
                    return None
                
                # If band_stats not found but no clear error, might just be slow loading
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return None
            
            # Find the genre by looking for dt with "Genre:" and getting the next dd
            # Based on the HTML structure: <dl class="float_right"><dt>Genre:</dt><dd>Heavy Metal</dd>
            try:
                # Wait for the genre dt element to be present
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#band_stats dl.float_right dt")))
                
                # Find the dt element with "Genre:" text
                genre_dt = driver.find_element(By.XPATH, "//div[@id='band_stats']//dl[@class='float_right']//dt[text()='Genre:']")
                
                # Get the immediately following dd sibling
                genre_dd = genre_dt.find_element(By.XPATH, "./following-sibling::dd[1]")
                genre = genre_dd.text.strip()
                
                if genre:
                    return genre
                
            except NoSuchElementException:
                # Try alternative method: find all dts and dds, match by position
                try:
                    dts = driver.find_elements(By.CSS_SELECTOR, "#band_stats dl.float_right dt")
                    dds = driver.find_elements(By.CSS_SELECTOR, "#band_stats dl.float_right dd")
                    
                    for i, dt in enumerate(dts):
                        if dt.text.strip() == "Genre:":
                            if i < len(dds):
                                genre = dds[i].text.strip()
                                if genre:
                                    return genre
                            break
                except Exception:
                    pass
            except Exception as e:
                # Last resort: try to get first dd in float_right (assuming Genre is first)
                try:
                    genre_dd = driver.find_element(By.CSS_SELECTOR, "#band_stats dl.float_right dd:first-of-type")
                    genre = genre_dd.text.strip()
                    if genre:
                        return genre
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            if attempt < retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"(Error: {e}, retrying in {wait_time}s)...", end=' ', flush=True)
                time.sleep(wait_time)
                continue
            else:
                print(f"Error fetching {band_name}: {e}")
                return None
    
    return None


def scrape_genres_for_bands(band_list: list, output_file: str = DEFAULT_OUTPUT, delay: float = DELAY, headless: bool = False) -> dict:
    """
    Scrape genres for a list of bands and save to JSON using Selenium.
    Returns a dictionary mapping band names to genres.
    """
    results = {}
    
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    print("Initializing Chrome browser...")
    driver = None
    try:
        if WEBDRIVER_MANAGER_AVAILABLE:
            print("Using webdriver-manager to automatically handle ChromeDriver...")
            print("(This may take 30-60 seconds on first run to download ChromeDriver)")
            print("Please wait...")
            try:
                driver_path = ChromeDriverManager().install()
                print(f"ChromeDriver ready!")
                service = Service(driver_path)
                print("Starting Chrome browser...")
                driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e:
                print(f"Error with webdriver-manager: {e}")
                print("Falling back to system ChromeDriver...")
                driver = webdriver.Chrome(options=chrome_options)
        else:
            print("Attempting to use system ChromeDriver...")
            print("(If this hangs, install webdriver-manager: pip install webdriver-manager)")
            driver = webdriver.Chrome(options=chrome_options)
        
        if driver is None:
            raise Exception("Failed to initialize Chrome driver")
        
        # Set a page load timeout to prevent hanging
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)
        
        # Execute comprehensive anti-detection scripts
        stealth_script = """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        window.chrome = {runtime: {}};
        """
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': stealth_script})
        driver.execute_script(stealth_script)
        print("Chrome browser initialized successfully!")
    except Exception as e:
        print(f"\nError initializing Chrome driver: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure Google Chrome is installed on your system")
        print("2. Install webdriver-manager: pip install webdriver-manager")
        print("3. Or manually download ChromeDriver from: https://chromedriver.chromium.org/")
        print("4. Make sure ChromeDriver is in your PATH")
        if driver:
            try:
                driver.quit()
            except:
                pass
        return {}
    
    try:
        # First, visit the homepage to establish a session
        print("Establishing session with Metal Archives...")
        driver.get('https://www.metal-archives.com/')
        time.sleep(2)  # Wait for page to load
        print("Session established successfully.")
        
        total = len(band_list)
        print(f"Scraping genres for {total} bands from Metal Archives...")
        print("=" * 60)
        
        for i, band_name in enumerate(band_list, 1):
            print(f"[{i}/{total}] Fetching genre for: {band_name}...", end=' ', flush=True)
            
            genre = scrape_band_genre(band_name, driver)
            
            if genre:
                results[band_name] = genre
                print(f"✓ {genre}")
            else:
                results[band_name] = None
                print("✗ Not found or error")
            
            # Delay between requests
            if i < total:
                time.sleep(delay)
    
    finally:
        # Always close the browser
        print("\nClosing browser...")
        driver.quit()
    
    # Save results to JSON
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"Results saved to {output_file}")
    print(f"Successfully scraped: {sum(1 for v in results.values() if v is not None)}/{total}")
    
    return results


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Scrape genres from Metal Archives for top bands"
    )
    parser.add_argument(
        "-f", "--filepath",
        default="data/dataset.json",
        help="Path to dataset JSON file (default: data/dataset.json)"
    )
    parser.add_argument(
        "-n", "--top",
        type=int,
        default=DEFAULT_TOP_N,
        help=f"Number of top bands to scrape (default: {DEFAULT_TOP_N})"
    )
    parser.add_argument(
        "-o", "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file (default: {DEFAULT_OUTPUT})"
    )
    parser.add_argument(
        "-d", "--delay",
        type=float,
        default=DELAY,
        help=f"Delay between requests in seconds (default: {DELAY})"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode (no GUI)"
    )
    args = parser.parse_args()
    
    # Get top bands using extract_top_bands functions
    print(f"Loading dataset from {args.filepath}...")
    df = load_music_data(args.filepath)
    
    print(f"Getting top {args.top} bands...")
    top_bands = get_top_bands(df, args.top)
    
    print(f"\nFound {len(top_bands)} bands to scrape")
    print("=" * 60)
    
    # Scrape genres
    results = scrape_genres_for_bands(top_bands, args.output, args.delay, args.headless)
    
    return results


if __name__ == "__main__":
    main()
