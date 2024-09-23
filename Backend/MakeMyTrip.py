import time
import Backend.URLS as URLS
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import threading
import requests
from pymongo import MongoClient

url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/inr.json"

response = requests.get(url)

data = response.json()

currency_bdt = data['inr']['bdt']
currency_usd = data['inr']['usd']
client = MongoClient('mongodb+srv://tmuhebbullah:Abcd1234..@cluster0.vxrd9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')  # Replace with your MongoDB URI if needed
db = client['hotel_database']  # Replace with your database name
collection1 = db['hotels_temp']

# Collection 2 - final data after processing
collection2 = db['hotels']

class MakeMyTrip(webdriver.Chrome):
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
        super(MakeMyTrip, self).__init__(options=options)
        self.implicitly_wait(30)  # Adjust implicit wait time as needed
        self.main_list = []
        self.store = []
        print("Initialized WebDriver with headless mode")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            self.quit()
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
    def land_first_page(self):
        self.get(URLS.Make_my_trip)
        # time.sleep(30)
        self.cancel_cross()

    def cancel_cross(self):
        cross = self.find_element(By.CLASS_NAME,'commonModal__close')
        cross.click()
    def search_hotels(self,place,adult_number,room_number):
        click_hotel = self.find_element(By.ID,'city')
        click_hotel.click()
        hotel_name_select = self.find_element(By.CLASS_NAME,'hw__searchInputWrapper')
        hotel_name_select.click()
        # time.sleep(30)
        hotel_name = self.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[1]/div[1]/div/div/div/div[1]/input')
        hotel_name.clear()
        hotel_name.send_keys(place)
        time.sleep(5)
        find_res = self.find_element(By.ID,'react-autowhatever-1-section-0-item-0')
        find_res.click()
        time.sleep(5)
        action = ActionChains(self)
        action.move_by_offset(1800, 900).click().perform()

        r_g = self.find_element(By.CSS_SELECTOR,'div[data-cy="HotelSearchWidget_319"]')
        r_g.click()
        room_guest_option = self.find_element(By.ID,'guest')
        room_guest_option.click()
        rooms_select = self.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[4]/div[1]/div[1]/div[1]/div[2]/div')
        rooms_select.click()
        rooms_select_num = self.find_element(By.XPATH,f"/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[4]/div[1]/div[1]/div[1]/div[2]/ul/li[{room_number}]")
        rooms_select_num.click()
        adult_select = self.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[4]/div[1]/div[1]/div[2]/div[2]/div')
        adult_select.click()
        adult_select_num = self.find_element(By.XPATH,f"/html/body/div[1]/div/div[2]/div/div[1]/div[2]/div/div[1]/div[4]/div[1]/div[1]/div[2]/div[2]/ul/li[{adult_number}]")
        adult_select_num.click()

        apply_button = self.find_element(By.CSS_SELECTOR,'button[data-cy="RoomsGuestsNew_327"]')
        apply_button.click()
        search_click = self.find_element(By.ID, 'hsw_search_button')
        search_click.click()
        time.sleep(10)
        ht = []
        self.scrolling()
        time.sleep(10)
        i = 0
        while True:
            try:
                x = {}
                hotel_list = self.find_element(By.ID, f'Listing_hotel_{i}')
                ht_name = hotel_list.find_element(By.CSS_SELECTOR,'span[class="wordBreak appendRight10"]').get_attribute('innerHTML').strip()
                # print(ht_name)
                redirect_link = hotel_list.find_element(By.TAG_NAME, 'a').get_attribute('href')
                image_link = hotel_list.find_element(By.TAG_NAME, 'img').get_attribute('src')
                price = hotel_list.find_element(By.ID,'hlistpg_hotel_shown_price').get_attribute('innerHTML').strip().split('₹<!-- --> <!-- -->')
                print(price)
                if len(price) == 2:
                    final_price = price[1].replace(',','')
                else:
                    temp = price[0].replace('₹ ','')
                    final_price = temp.replace(',','')

                # print(f"Anchor href: {redirect_link}")
                # print(f"Image src: {image_link}")
                print(f"Price: {final_price}")
                x['OTA']= 'MakeMyTrip.com'
                x['Place'] = place
                if room_number >= 2:
                    x['Adult_Person'] = adult_number+1
                else:
                    x['Adult_Person'] = adult_number
                x['Room_Count'] = room_number
                x['Hotel_Name'] = ht_name.lower()
                x['Redirect_Link'] = redirect_link
                x['Image_Link'] = image_link
                x['BDT_Price'] = float(final_price)*currency_bdt
                x['USD_Price'] = float(final_price)*currency_usd
                # print(f"Added: {x}")
                ht.append(x)
                collection1.insert_one(x)  # Inserting each hotel record into the MongoDB database
                print(f"Added to DB: {x}")
                i+=1
            except Exception as e:
                break


        # for i in range(10):
        #     x = self.find_element(By.ID,f'Listing_hotel_{i}')
        #     print(f"Added: {x}")
        #     ht.append(x)
        print(ht)
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

