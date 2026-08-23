from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

print("Checking Chrome...")

try:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    print("Installing/checking ChromeDriver...")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    print("Opening URL...")
    driver.get("https://batchetl.streamlit.app")
    
    print("Page title:", driver.title)
    print("Page length:", len(driver.page_source))
    
    driver.quit()
    print("✅ Selenium works!")
except Exception as e:
    print(f"❌ Error: {e}")