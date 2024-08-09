import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


def get_driver(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--remote-debugging-port=9222") 
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")


    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(url)

    return driver

def is_flight_schedule_available(url):
    driver = get_driver(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.scheduleList > div.tblbody > div.scrollArea'))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        scroll_area_div = soup.select_one('div.scheduleList > div.tblbody > div.scrollArea')
        if scroll_area_div:
            return True
        
    except Exception as e:
        print(e)
        return False

    finally:
        driver.quit()

def get_flight_schedules(url):
    driver = get_driver(url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.scheduleList > div.tblbody > div.scrollArea'))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        scroll_area_div = soup.select_one('div.scheduleList > div.tblbody > div.scrollArea')
        if scroll_area_div:
            flight_info_list = []
            items = scroll_area_div.select('li.itemBlock')
            
            for item in items:
                airline_name_element = item.select_one('span.airlineName > span.name')
                flight_time_element = item.select('div.airlineTime .time')
                fee_element = item.select_one('span.fee')

                airline_name = airline_name_element.text.strip() if airline_name_element else None
                departure_time = flight_time_element[0].text.strip() if flight_time_element else None
                arrival_time = flight_time_element[1].text.strip() if flight_time_element else None
                fee = fee_element.text.strip() if fee_element else None
                
                flight_info = {
                    "airline_name": airline_name,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "fee": fee
                }

                flight_info_list.append(flight_info)
            
            return flight_info_list
        
    except Exception as e:
        raise e

    finally:
        driver.quit()