import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import getpass

# ESPN League URL
link = "https://fantasy.espn.com/football/players/projections?leagueId=1555307944"

def scrape_espn_with_login():
    """
    ESPN Fantasy requires login for private leagues.
    This version opens a browser window for manual login.
    """
    print("=== ESPN Fantasy Scraper with Manual Login ===")
    print("This will open a browser window for you to log in manually.")
    print("After logging in, the script will attempt to scrape the data.")
    
    input("Press Enter when ready to open browser...")
    
    # Set up Chrome options (remove headless for manual login)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Opening ESPN login page...")
        # Go to ESPN login first
        driver.get("https://www.espn.com/login")
        
        print("\n=== MANUAL LOGIN REQUIRED ===")
        print("1. Log into your ESPN account in the browser window")
        print("2. After logging in successfully, come back here")
        print("3. Press Enter to continue with data scraping")
        
        input("Press Enter after you've logged in...")
        
        # Now navigate to your league page
        print("Navigating to your league page...")
        driver.get(link)
        
        # Wait for page to load
        time.sleep(10)
        
        print("Looking for player projection data...")
        
        # Try different selectors for ESPN fantasy data
        selectors_to_try = [
            "table",
            ".Table",
            "[data-testid='player-table']",
            ".player-column",
            ".jsx-player-table",
            ".Table__TR",
            "tr"
        ]
        
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    
                    if selector == "table":
                        # Try to extract table directly
                        for i, table in enumerate(elements):
                            table_html = table.get_attribute('outerHTML')
                            try:
                                df = pd.read_html(table_html)[0]
                                print(f"Successfully extracted table {i}!")
                                print("Sample data:")
                                print(df.head())
                                return df
                            except:
                                continue
                    
                    elif selector == "tr":
                        # Extract row data manually
                        rows_data = []
                        headers = []
                        
                        for i, row in enumerate(elements[:20]):  # Check first 20 rows
                            row_text = row.text.strip()
                            if row_text and len(row_text) > 10:  # Skip empty/short rows
                                cells = row.find_elements(By.TAG_NAME, "td")
                                if not cells:
                                    cells = row.find_elements(By.TAG_NAME, "th")
                                
                                if cells:
                                    cell_texts = [cell.text.strip() for cell in cells]
                                    if i == 0 or not headers:
                                        headers = cell_texts
                                    else:
                                        rows_data.append(cell_texts)
                                
                                print(f"Row {i}: {row_text[:100]}...")
                        
                        if rows_data and headers:
                            print(f"Creating DataFrame with {len(rows_data)} rows and {len(headers)} columns")
                            # Ensure all rows have same length as headers
                            cleaned_rows = []
                            for row in rows_data:
                                if len(row) == len(headers):
                                    cleaned_rows.append(row)
                                elif len(row) > 0:
                                    # Pad or trim row to match headers
                                    while len(row) < len(headers):
                                        row.append("")
                                    cleaned_rows.append(row[:len(headers)])
                            
                            if cleaned_rows:
                                df = pd.DataFrame(cleaned_rows, columns=headers)
                                print("Successfully created DataFrame!")
                                print("Sample data:")
                                print(df.head())
                                return df
                        
            except Exception as e:
                print(f"Selector {selector} failed: {e}")
                continue
        
        # If no structured data found, show page info
        print("\n=== PAGE ANALYSIS ===")
        print(f"Page title: {driver.title}")
        print(f"Current URL: {driver.current_url}")
        
        # Get page text to see what's there
        page_text = driver.find_element(By.TAG_NAME, "body").text
        print(f"Page contains {len(page_text)} characters")
        print("First 500 characters of page:")
        print(page_text[:500])
        
        return None
        
    except Exception as e:
        print(f"Error during scraping: {e}")
        return None
        
    finally:
        print("\nClosing browser in 10 seconds...")
        print("Press Ctrl+C to close immediately")
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            pass
        driver.quit()

def try_espn_api_approach():
    """
    Try to access ESPN's API endpoints directly
    """
    print("=== Trying ESPN API Approach ===")
    
    # Extract league ID from URL
    league_id = "1555307944"
    
    # Common ESPN API endpoints
    api_urls = [
        f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leagues/{league_id}",
        f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leagues/{league_id}/teams",
        f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    for url in api_urls:
        try:
            print(f"Trying: {url}")
            response = requests.get(url, headers=headers)
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("API Success! Data structure:")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                return data
            else:
                print(f"Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"API call failed: {e}")
    
    return None

if __name__ == "__main__":
    print("=== ESPN Fantasy Football Data Scraper ===\n")
    
    print("Choose your approach:")
    print("1. Try API endpoints (faster, may not work for private leagues)")
    print("2. Use browser with manual login (more reliable for private leagues)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        result = try_espn_api_approach()
        if result:
            print("API data retrieved successfully!")
            # You would need to parse the JSON structure here
        else:
            print("API approach failed. Try option 2.")
    
    elif choice == "2":
        result = scrape_espn_with_login()
        
        if result is not None and hasattr(result, 'head'):
            print("\n=== SUCCESS! Saving data ===")
            result.to_csv("espn_projections.csv", index=False)
            print("Data saved to espn_projections.csv")
        else:
            print("No data was successfully extracted.")
    
    else:
        print("Invalid choice. Please run again and choose 1 or 2.")