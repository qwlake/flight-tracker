import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

def is_flight_schedule_available():
    flight_schedule_date = os.getenv('FLIGHT_SCHEDULE_DATE')
    url = f'https://sky.interpark.com/schedules/domestic/CJU-GMP-{flight_schedule_date}?adt=2&chd=0&inf=0&seat=DOMESTIC_BASE&pickAirLine=&pickMainFltNo=&pickSDate='

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222") 

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.scheduleList > div.tblbody > div.scrollArea'))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        scroll_area_div = soup.select_one('div.scheduleList > div.tblbody > div.scrollArea')
        if scroll_area_div:
            return True
        
    except:
        return False

    finally:
        driver.quit()
