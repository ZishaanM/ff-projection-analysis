import os
import sys
import time

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

LEAGUE_ID = os.environ.get("ESPN_LEAGUE_ID")
if not LEAGUE_ID:
    sys.exit("Set ESPN_LEAGUE_ID (see .env.example).")

link = f"https://fantasy.espn.com/football/players/projections?leagueId={LEAGUE_ID}"

def scrape_espn_with_selenium():
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("Loading ESPN page...")
        driver.get(link)
        
        # Wait for page to load
        time.sleep(5)
        
        # Try to find tables using different methods
        print("Looking for tables...")
        
        # Method 1: Try pandas on the page source
        try:
            page_source = driver.page_source
            tables = pd.read_html(page_source)
            if tables:
                print(f"Found {len(tables)} tables using pandas!")
                return tables[0]  # Return first table
        except:
            print("Pandas couldn't find tables in page source")
        
        # Method 2: Look for specific ESPN table elements
        try:
            # Wait for player data to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Table"))
            )
            
            # Get the table element
            table_element = driver.find_element(By.CLASS_NAME, "Table")
            table_html = table_element.get_attribute('outerHTML')
            
            # Parse with pandas
            tables = pd.read_html(table_html)
            if tables:
                print("Found table using selenium element selection!")
                return tables[0]
                
        except Exception as e:
            print(f"Selenium table method failed: {e}")
        
        # Method 3: Extract data manually from elements
        try:
            print("Trying manual data extraction...")
            # Look for player rows
            player_rows = driver.find_elements(By.CSS_SELECTOR, "tr")
            print(f"Found {len(player_rows)} table rows")
            
            if len(player_rows) > 0:
                # Print first few rows to see structure
                for i, row in enumerate(player_rows[:5]):
                    print(f"Row {i}: {row.text[:100]}...")
                
                return "Manual extraction needed - see row data above"
            
        except Exception as e:
            print(f"Manual extraction failed: {e}")
        
        return "No data found"
        
    except Exception as e:
        print(f"Error accessing ESPN: {e}")
        return None
        
    finally:
        driver.quit()

def try_simple_requests():
    """Try simple requests approach first"""
    print("Trying simple requests approach...")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(link, headers=headers)
        
        if response.status_code == 200:
            tables = pd.read_html(response.text)
            if tables:
                print("Success with simple requests!")
                return tables[0]
        
        print(f"Requests returned status code: {response.status_code}")
        return None
        
    except Exception as e:
        print(f"Simple requests failed: {e}")
        return None

# Try different approaches
print("=== ESPN Fantasy Data Scraper ===\n")

# First try simple requests
result = try_simple_requests()

if result is None:
    print("\n=== Trying Selenium approach ===")
    result = scrape_espn_with_selenium()

if result is not None and hasattr(result, 'head'):
    print("\n=== SUCCESS! Here's your data: ===")
    print(result.head())
    
    # Save to CSV
    result.to_csv("espn_projections.csv", index=False)
    print("\nData saved to espn_projections.csv")
else:
    print(f"\n=== Result: ===")
    print(result)