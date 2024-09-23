import concurrent.futures
from Backend.Booking import Booking
from Backend.MakeMyTrip import MakeMyTrip
from pymongo import MongoClient

# Define tasks for Booking
def booking_task(place, adult_num, room_num):
    with Booking() as Bot:
        Bot.land_first_page()
        Bot.search_booking(place=place, adult_num=adult_num, room_num=room_num)

# Define tasks for MakeMyTrip
def makemytrip_task(place, adult_number, room_number):
    with MakeMyTrip() as Bot:
        Bot.land_first_page()
        Bot.search_hotels(place=place, adult_number=adult_number, room_number=room_number)

# List of locations
locations = [
    "Cox's Bazar", "Dhaka", "Chittagong", "Inani", "Sreemangal",
    "Sylhet", "Narayanganj", "Bandarban", "Himchori", "Kuakata",
    "Gazipur", "Comilla", "Kolkata", "Darjeeling", "Kathmandu",
    "Bangkok", "Kuala Lumpur", "Singapore", "Male City", "Dubai", "Paris"
]

# List of tasks to run for all locations
tasks = []
for location in locations:
    tasks.append((booking_task, location, 1, 1))
    tasks.append((booking_task, location, 2, 1))
    tasks.append((booking_task, location, 2, 2))
    tasks.append((booking_task, location, 3, 2))
    tasks.append((booking_task, location, 4, 2))
    tasks.append((makemytrip_task, location, 1, 1))
    tasks.append((makemytrip_task, location, 2, 1))
    tasks.append((makemytrip_task, location, 2, 2))
    tasks.append((makemytrip_task, location, 3, 2))
    tasks.append((makemytrip_task, location, 1, 2))

# Function to execute tasks in batches of 10
def run_in_batches(tasks, batch_size=10):
    with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            futures = [executor.submit(task[0], task[1], task[2], task[3]) for task in batch]
            concurrent.futures.wait(futures)

# Run the tasks in batches
run_in_batches(tasks, batch_size=10)

# MongoDB connection and moving data between collections
client = MongoClient('mongodb+srv://tmuhebbullah:Abcd1234..@cluster0.vxrd9.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')  # Replace with your MongoDB URI if needed
db = client['hotel_database']  # Replace with your database name
collection1 = db['hotels_temp']

# Collection 2 - final data after processing
collection2 = db['hotels']
collection2.delete_many({})  # Remove all existing data from the second collection

# Step 2: Move data from the first collection to the second collection
all_data = list(collection1.find({}))  # Fetch all data from collection1
print(all_data)
if len(all_data) > 0:
    # Insert into the second collection
    collection2.insert_many(all_data)  # Insert all data into collection2
    print(f"Moved {len(all_data)} records to the second collection.")

    # Step 3: Optionally delete data from the first collection (if needed)
else:
    print("No data to move from collection1 to collection2.")

# with Agoda() as Bot:
#     Bot.land_first_page()
#     Bot.search_hotel(place="Cox's Bazar",adult_number=1,room_number=1)
# with Agoda() as Bot:
#     Bot.land_first_page()
#     Bot.search_hotel(place="Cox's Bazar",adult_number=2,room_number=1)
# with Agoda() as Bot:
#     Bot.land_first_page()
#     Bot.search_hotel(place="Cox's Bazar",adult_number=2,room_number=2)
# with Agoda() as Bot:
#     Bot.land_first_page()
#     Bot.search_hotel(place="Cox's Bazar",adult_number=3,room_number=2)
# with Agoda() as Bot:
#     Bot.land_first_page()
#     Bot.search_hotel(place="Cox's Bazar",adult_number=4,room_number=2)

