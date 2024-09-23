import time

import Backend.URLS as URLS
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime, timedelta
from pymongo import MongoClient
import requests
client = MongoClient('mongodb+srv://tmuhebbullah:Abcd1234..@cluster0.vxrd9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')  # Replace with your MongoDB URI if needed
db = client['hotel_database']  # Replace with your database name

# Collection 1 - where initial data is stored
collection1 = db['hotels_temp']

# Collection 2 - final data after processing
collection2 = db['hotels']
url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/bdt.json"
response = requests.get(url)
data = response.json()
currency_usd = data['bdt']['usd']

class Booking(webdriver.Chrome):
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
        super(Booking, self).__init__(options=options)
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
        self.get(URLS.Booking_dot_com)
        self.cancel_cross()
    def cancel_cross(self):
        try:
            select_cross = self.find_element(By.CSS_SELECTOR,'button[aria-label="Dismiss sign-in info."]')
            select_cross.click()
        except Exception as e:
            pass


    def scrolling(self):
        last_height = self.execute_script("return document.body.scrollHeight")
        time.sleep(5)
        while True:
            # Scroll down to the bottom
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

    def search_booking(self,place,adult_num, room_num):
        self.cancel_cross()
        # Searching a place
        search = self.find_element(By.NAME, 'ss')  #ada65db9b5
        search.clear()
        search.send_keys(place)
        find_res = self.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/form/div[1]/div[1]/div/div/div[2]/div/div/ul/li[1]')
        find_res.click()
        today = datetime.today()

        # Calculate tomorrow's date
        tomorrow = today + timedelta(days=1)

        # Calculate the day after tomorrow's date
        day_after_tomorrow = today + timedelta(days=2)

        # Finding check-in and check-out date
        check_in = tomorrow.strftime('%Y-%m-%d')
        checkin_ele = self.find_element(By.CSS_SELECTOR,f'span[data-date="{check_in}"]')
        checkin_ele.click()
        check_out = day_after_tomorrow.strftime('%Y-%m-%d')
        checkout_ele = self.find_element(By.CSS_SELECTOR, f'span[data-date="{check_out}"]')
        checkout_ele.click()

        # Select person and room count

        room_box = self.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/form/div[1]/div[3]/div/button')
        room_box.click()
        while True:
            dec_adult = self.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/form/div[1]/div[3]/div/div/div/div/div[1]/div[2]/button[1]')
            dec_adult.click()
            adults_value_ele = self.find_element(By.ID, 'group_adults')
            adults_value = adults_value_ele.get_attribute('value')  # Should give back adults count

            if int(adults_value) == 1:
                break
        for _ in range(adult_num-1):
            inc_adult = self.find_element(By.XPATH,
                                          '/html/body/div[3]/div[2]/div/form/div[1]/div[3]/div/div/div/div/div[1]/div[2]/button[2]')
            inc_adult.click()

        for _ in range(room_num-1):
            inc_room = self.find_element(By.XPATH,'/html/body/div[3]/div[2]/div/form/div[1]/div[3]/div/div/div/div/div[3]/div[2]/button[2]')
            inc_room.click()


        adult_increase = self.find_element(By.CSS_SELECTOR,'button[data-testid="occupancy-config"]')
        adult_increase.click()
        search_button = self.find_element(By.CSS_SELECTOR,'button[type="submit"]')
        search_button.click()
        self.cancel_cross()
        self.scrolling()
        # hotels_select = self.find_element(By.CLASS_NAME, 'f9958fb57b')
        hotels_name = self.find_elements(By.CSS_SELECTOR, '[data-testid="property-card"]')
        print(len(hotels_name))
        i = 1
        ht = []
        for hotel in hotels_name:
            x = {}
            Image_link = ''
            Redirect_Link = ''
            try:
                hotel_name = hotel.find_element(By.CSS_SELECTOR, '[data-testid="title"]').get_attribute(
                    'innerHTML').strip()
                # print(f'{i}. {hotel_name}')
                # room_type = hotel.find_element(By.CSS_SELECTOR, 'h4[role="link"]').get_attribute('innerHTML').strip()
                # print(f'Room Type = {room_type}')
                i += 1
                # for image and redirect link

                anchor_tags = hotel.find_elements(By.CSS_SELECTOR,
                                                  'a[data-testid="property-card-desktop-single-image"]')
                for anchor in anchor_tags:
                    Redirect_Link = anchor.get_attribute('href')
                    img = anchor.find_element(By.TAG_NAME, 'img')
                    Image_link = img.get_attribute('src')

                price = hotel.find_element(By.CSS_SELECTOR,
                                           'span[data-testid="price-and-discounted-price"]').get_attribute(
                    'innerHTML').strip()
                price = price.split(';')
                x['OTA'] = "Booking.com"
                x['Place'] = place.lower()
                x['Adult_Person'] = adult_num
                x['Room_Count'] = room_num
                x['Hotel_Name'] = hotel_name
                x['BDT_Price'] = float(price[1].replace(',',''))
                x['USD_Price'] = float(price[1].replace(',',''))*currency_usd
                x['Image_Link'] = Image_link
                x['Redirect_Link'] = Redirect_Link
                collection1.insert_one(x)  # Inserting each hotel record into the MongoDB database
                print(f"Added to DB: {x}")
                ht.append(x)

            except Exception as e:
                pass
        for i in ht:
            print(i)
        # collection2.delete_many({})  # Remove all existing data from the second collection
        #
        # # Step 2: Move data from the first collection to the second collection
        # all_data = list(collection1.find({}))  # Fetch all data from collection1
        # print(all_data)
        # if len(all_data) > 0:
        #     # Insert into the second collection
        #     collection2.insert_many(all_data)  # Insert all data into collection2
        #     print(f"Moved {len(all_data)} records to the second collection.")
        #
        #     # Step 3: Optionally delete data from the first collection (if needed)
        # else:
        #     print("No data to move from collection1 to collection2.")
        time.sleep(5)
