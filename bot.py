import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from states.states import States
from data.database_works import UserDatabase
from data.config import API_TOKEN
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import random
import pandas as pd
import os

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

db = UserDatabase("database.db")






def fuel_data(file_name):
    # Replace 'your_file.xlsx' with the path to your Excel file
    file_path = file_name

    # Read the Excel file
    try:
        df = pd.read_excel(file_path)
        
        # Filter rows where 'Unnamed: 15' column contains float values
        amt_column = df['Unnamed: 15']  # Adjust the column index based on your actual file
        float_values = amt_column.apply(lambda x: isinstance(x, float) or isinstance(x, int))
        filtered_df = df[float_values]
        
        # Remove quotation marks from 'Unnamed: 15' column using .loc[]
        filtered_df.loc[:, 'Unnamed: 15'] = filtered_df['Unnamed: 15'].astype(str).str.replace('"', '')
        
        # Convert 'Unnamed: 15' column to numeric and remove NaN values using .loc[]
        filtered_df.loc[:, 'Unnamed: 15'] = pd.to_numeric(filtered_df['Unnamed: 15'], errors='coerce')
        filtered_df = filtered_df.dropna(subset=['Unnamed: 15'])
        
        # Group by 'Unnamed: 1' (Driver Name) and sum 'Unnamed: 15' values
        grouped_df = filtered_df.groupby('Unnamed: 1')['Unnamed: 15'].sum().reset_index()

        # Initialize an empty list to store results
        results = []

        for index, row in grouped_df.iterrows():
            driver_name = row['Unnamed: 1']
            total_fuel = row['Unnamed: 15']
            results.append((driver_name, total_fuel))

        return results
        
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")










data = {}

chat = "@helsihx"

def catch_driver(unit, name, truck_number):
    driver_name = db.catch_driver(unit)
    if driver_name:
        print(driver_name[0][0])
    else:
        print("Driver Not found")
        db.insert_driver(name, truck_number)

import csv

@dp.message_handler(lambda message: "Load" in message.text)
async def receive_new_job(message: types.Message):
    unit = message.text.split("Load:")[1].split(" ")[2].split('\n')[0]
    driver_name = message.text.split("👤")[1].split(" ")[2].split("\n")[0]
    dh = message.text.split("DH")[1].split(" ")[1].split("\n")[0]
    customer_name = message.text.split("📦")[1].split(" ")[2]
    thre = message.text.split("————————————————")[2].split("\n")[3].split("   ")[0]
    four = message.text.split("————————————————")[2].split("\n")[4].split('   ')[0]
    bosh = f"{thre} - {four}"
    
    thre_del = message.text.split("————————————————")[3].split("\n")[3].split("   ")[0]
    four_del = message.text.split("————————————————")[3].split("\n")[4].split('   ')[0]
    oxr = f"{thre_del} {four_del}"
    lane = f"{bosh} - {oxr}"
    pu_data = message.text.split("PU:")[1].split("\n")[0]
    
    manager = message.text.split("👨🏻‍💻: ")[1].split("\n")[0]

    rate = message.text.split("Rate: ")[1].split("\n")[0]

    miles = message.text.split("Miles: ")[1].split("\n")[0]
   

    

    all_data = [customer_name, unit, driver_name,lane, pu_data, rate, dh, miles, manager]
    print(all_data)
    
    catch_driver(unit, driver_name, unit)
    
    # Write to CSV file
    with open('data.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(all_data)






@dp.message_handler(content_types=['document'])
async def handle_document(message: types.Message):
    if message.document.mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' and message.caption == '/data':
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        # Download the file
        downloaded_file = await bot.download_file(file_path)
        
        # Save the file locally
        file_name = f"downloaded_{file_id}.xlsx"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())

        # Process the downloaded Excel file
        data = fuel_data(file_name)
        
        # Remove the downloaded file after processing
        os.remove(file_name)

        # Format and print the data
        if data:
            print("Total fuel values per driver:")
            print("{:<20} {:<10}".format("Driver Name", "Total Fuel"))
            print("-" * 30)
            for driver, fuel in data:
                print("{:<20} {:<10}".format(driver, fuel))

        await message.delete()





@dp.message_handler(commands='manager')
async def admin_handler(message: types.Message):
    manager_idx = db.admin_check(message.from_user.id)
    for manager_id in manager_idx:

        if manager_id[0] == message.from_user.id:
            await message.answer("Hello manager")

        else:
            await message.answer("You are not an admin!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
