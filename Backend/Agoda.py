import time

import Backend.URLS as URLS
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import requests

url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"

response = requests.get(url)

data = response.json()

currency = data['usd']['bdt']
class Agoda(webdriver.Chrome):
    def __init__(self, teardown=False):
        self.teardown = teardown
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Ensure headless option is set correctly
        # options.add_argument("--no-sandbox")
        # options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ['enable-logging'])
        super(Agoda, self).__init__(options=options)
        self.implicitly_wait(30)  # Adjust implicit wait time as needed
        self.main_list = []
        self.store = []
        print("Initialized WebDriver with headless mode")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()

    def land_first_page(self):
        self.get(URLS.Agoda_dot_com)

    def scrolling(self):
        last_height = self.execute_script("return document.body.scrollHeight")
        time.sleep(5)
        while True:
            # Scroll down to the bottom
            self.execute_script("window.scrollBy(0, 400);")
            time.sleep(5)
            self.execute_script("window.scrollBy(0, 600);")
            time.sleep(5)
            self.execute_script("window.scrollBy(0, 800);")
            time.sleep(5)
            self.execute_script("window.scrollBy(0, 1000);")
            time.sleep(5)
            self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(10)
            self.execute_script("window.scrollBy(0, -500);")
            # Wait to load the page
            time.sleep(10)  # adjust the sleep time as needed

            # Calculate new scroll height and compare with the last scroll height
            new_height = self.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    def cancel_cross(self):
        try:
            cross = self.find_element(By.ID,'closeNotificationTapZone')
            cross.click()
        except Exception:
            pass
    def search_hotel(self,place,adult_number,room_number):

        self.cancel_cross()
        place_name = self.find_element(By.ID,'textInput')
        place_name.clear()
        place_name.send_keys(place)
        select_place = self.find_element(By.CSS_SELECTOR,'span[class="Suggestion__geoHierarchyName"]')
        select_place.click()
        today = datetime.today()

        # Calculate tomorrow's date
        tomorrow = today + timedelta(days=1)

        # Calculate the day after tomorrow's date
        day_after_tomorrow = today + timedelta(days=2)
        check_in_date = tomorrow.strftime('%Y-%m-%d')
        check_in = self.find_element(By.CSS_SELECTOR,f'span[data-selenium-date="{check_in_date}"]')
        check_in.click()
        check_out_date = day_after_tomorrow.strftime('%Y-%m-%d')
        check_out = self.find_element(By.CSS_SELECTOR,f'span[data-selenium-date="{check_out_date}"]')
        check_out.click()
        rooms_element = self.find_element(By.CSS_SELECTOR,'div[data-selenium="occupancyRooms"]')
        rooms_increase = rooms_element.find_element(By.CSS_SELECTOR,'button[aria-label="Add"]')
        for i in range(room_number-1):
            rooms_increase.click()
        adult_element = self.find_element(By.CSS_SELECTOR,'div[data-selenium="occupancyAdults"]')
        adult_decrease = adult_element.find_element(By.CSS_SELECTOR,'button[aria-label="Subtract"]')
        for i in range(1):
            adult_decrease.click()
        adult_increase = adult_element.find_element(By.CSS_SELECTOR,'button[aria-label="Add"]')
        for i in range(adult_number-1):
            adult_increase.click()
        try:
            done_click = self.find_element(By.CSS_SELECTOR,'button[aria-label="Done"]')
            done_click.click()
        except Exception:
            pass
        search_click = self.find_element(By.CSS_SELECTOR,'button[data-selenium="searchButton"]')
        search_click.click()
        self.scrolling()
        hotels_list = self.find_elements(By.CSS_SELECTOR,'div[data-element-name="PropertyCardBaseJacket"]')
        print(len(hotels_list))
        ht = []
        for i in range(len(hotels_list)):
            x = {}
            try:
                hotel_name = hotels_list[i].find_element(By.CSS_SELECTOR, 'h3[data-selenium="hotel-name"]').get_attribute('innerHTML').strip()
                redirect_link = hotels_list[i].find_element(By.TAG_NAME, 'a').get_attribute('href')
                image_link = hotels_list[i].find_element(By.TAG_NAME, 'img').get_attribute('src')
                price = hotels_list[i].find_element(By.CLASS_NAME, 'PropertyCardPrice__Value').get_attribute('innerHTML').strip()
                print(hotel_name)
                print(redirect_link)
                print(image_link)
                print(float(price)*currency)
                x['Place'] = place
                x['Adult_Person'] = adult_number
                x['Room_Count'] = room_number
                x['Hotel_name'] = hotel_name
                x['Redirect_link'] = redirect_link
                x['Image_link'] = image_link
                x['Price'] = float(price)*currency
                ht.append(x)
            except Exception as e:
                print(e)
        for i in ht:
            print(i)

