import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import os
import sys
import time
import getpass

LEAGUE_ID = os.environ.get("ESPN_LEAGUE_ID")
if not LEAGUE_ID:
    sys.exit("Set ESPN_LEAGUE_ID (see .env.example).")

def debug_espn_login():
    """
    Debug version that shows you what's happening step by step
    """
    print("=== ESPN Debug Scraper ===")
    
    # Get credentials
    username = os.environ.get("ESPN_USERNAME") or input("Enter your ESPN username/email: ")
    password = os.environ.get("ESPN_PASSWORD") or getpass.getpass("Enter your ESPN password (hidden): ")
    
    # Set up Chrome options (visible browser for debugging)
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Set up the driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print("\n🌐 Step 1: Going to ESPN login page...")
        driver.get("https://www.espn.com/login")
        time.sleep(3)
        
        print(f"Current URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Look for different possible login form selectors
        login_selectors = [
            "input[name='username']",
            "input[name='email']", 
            "input[type='email']",
            "#username",
            "#email",
            "input[placeholder*='email']",
            "input[placeholder*='username']"
        ]
        
        password_selectors = [
            "input[name='password']",
            "input[type='password']",
            "#password"
        ]
        
        print("\n🔍 Step 2: Looking for login form...")
        
        username_field = None
        password_field = None
        
        # Try to find username field
        for selector in login_selectors:
            try:
                username_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found username field with selector: {selector}")
                break
            except:
                continue
        
        # Try to find password field
        for selector in password_selectors:
            try:
                password_field = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"✅ Found password field with selector: {selector}")
                break
            except:
                continue
        
        if not username_field or not password_field:
            print("❌ Could not find login fields. Let's inspect the page...")
            
            # Get all input elements
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input elements:")
            for i, inp in enumerate(inputs):
                print(f"  {i}: type='{inp.get_attribute('type')}', name='{inp.get_attribute('name')}', id='{inp.get_attribute('id')}', placeholder='{inp.get_attribute('placeholder')}'")
            
            # Look for buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            print(f"Found {len(buttons)} buttons:")
            for i, btn in enumerate(buttons):
                print(f"  {i}: text='{btn.text}', type='{btn.get_attribute('type')}', class='{btn.get_attribute('class')}'")
            
            print("\n🔧 Manual login required:")
            print("1. Log in manually in the browser window")
            print("2. Navigate to your league page")
            print("3. Come back here and press Enter")
            input("Press Enter when you're logged in and on your league page...")
            
        else:
            print("\n📝 Step 3: Entering credentials...")
            username_field.clear()
            username_field.send_keys(username)
            time.sleep(1)
            
            password_field.clear()
            password_field.send_keys(password)
            time.sleep(1)
            
            # Look for submit button
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                "button:contains('Log In')",
                "button:contains('Sign In')",
                ".btn-submit",
                "#submit-btn"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = driver.find_element(By.CSS_SELECTOR, selector)
                    print(f"✅ Found submit button with selector: {selector}")
                    break
                except:
                    continue
            
            if submit_button:
                print("🔑 Step 4: Clicking login button...")
                submit_button.click()
            else:
                print("⚠️ No submit button found, trying Enter key...")
                password_field.send_keys(Keys.RETURN)
            
            # Wait for login
            print("⏳ Step 5: Waiting for login to complete...")
            time.sleep(5)
            
            print(f"Post-login URL: {driver.current_url}")
            
            # Navigate to league page
            print("🏈 Step 6: Going to your league page...")
            driver.get(f"https://fantasy.espn.com/football/players/projections?leagueId={LEAGUE_ID}")
            time.sleep(8)
        
        print(f"\n📊 Step 7: Analyzing league page...")
        print(f"Final URL: {driver.current_url}")
        print(f"Page title: {driver.title}")
        
        # Look for any tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"Found {len(tables)} table elements")
        
        if tables:
            for i, table in enumerate(tables):
                try:
                    table_html = table.get_attribute('outerHTML')
                    df = pd.read_html(table_html)[0]
                    
                    if len(df) > 3:  # Substantial table
                        print(f"\n✅ Table {i} looks promising ({len(df)} rows, {len(df.columns)} columns):")
                        print(df.head())
                        
                        # Save this table
                        filename = f"espn_table_{i}.csv"
                        df.to_csv(filename, index=False)
                        print(f"💾 Saved to {filename}")
                        
                        return df
                        
                except Exception as e:
                    print(f"Table {i} processing failed: {e}")
        
        # If no tables, look for structured data
        print("\n🔍 Looking for other data structures...")
        
        # Get page source and look for JSON data
        page_source = driver.page_source
        if '"players"' in page_source or '"projections"' in page_source:
            print("🎯 Found potential JSON data in page source!")
            print("You may need to extract JSON data instead of HTML tables")
        
        # Look for specific ESPN fantasy elements
        espn_selectors = [
            "[data-testid*='player']",
            ".player-column",
            ".jsx-player",
            ".Table__TR",
            ".player-name"
        ]
        
        for selector in espn_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                for i, elem in enumerate(elements[:5]):
                    print(f"  {i}: {elem.text[:100]}")
        
        return None
        
    except Exception as e:
        print(f"❌ Major error: {e}")
        return None
        
    finally:
        print("\n⏰ Browser will close in 30 seconds...")
        print("Press Ctrl+C to close immediately")
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            pass
        driver.quit()

if __name__ == "__main__":
    debug_espn_login()