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
import uuid
import string

import csv

# Set up logging
logging.basicConfig(level=logging.INFO)
tokens = {}
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







@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.get_args():

        token = message.text.split("=")[0].split(' ')[1]
   
        if tokens["token"] == token:
            await message.answer(f"Welcome new manager\n\nYour key: {token}")
            db.add_manager(message.from_user.id, token)
            tokens.clear()
        else:
            await message.answer("Expired")

data = {}

chat = "@helsihx"

def catch_driver(unit, name, truck_number):
    driver_name = db.catch_driver(unit)
    if driver_name:
        print(driver_name[0][0])
    else:
        print("Driver Not found")
  
def generate_job_id():
    # Generate a UUID (Universally Unique Identifier) for the job ID
    job_id = uuid.uuid4().hex
    return job_id

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
   

    

    # all_data = [customer_name, unit, driver_name, lane, pu_data, rate, dh, miles, manager]
    # Generate or retrieve the unique jobID
    jobID = generate_job_id()  # Assuming you have a function to generate a unique job ID

    # Insert data into the database
    db.insert_all(jobID, customer_name, unit, driver_name, lane, pu_data, rate, dh, miles, manager, "In Progress")

    # Call the catch_driver function with the appropriate parameters
    catch_driver(unit, driver_name, customer_name)










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
    # db.add_admin()

    if " " in message.text:

        manager_key = message.text.split(" ")[1]
       


        manager_idx = db.admin_check()
        manager_exsist_key = db.catch_key(message.from_user.id)
        admin_status = db.catch_admin_status(message.from_user.id)

        if manager_key == manager_exsist_key[0]:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_super_admin = ['Drivers', 'Works', 'Statistic', 'Managers', 'Add new manager', 'Remove manager']
            buttons_for_manager = ["Drivers", 'Works']
            for manager_id in manager_idx:

                if manager_id[0] == message.from_user.id:
                    if admin_status[0] == "Super":
                        keyboard.add(*buttons_for_super_admin)
                        await message.answer(f"Welcome {message.from_user.first_name}", reply_markup=keyboard) 
                    else:
                        year = datetime.now().year
                        month = datetime.now().month
                        day = datetime.now().day

                        hour = datetime.now().hour
                        minute = datetime.now().minute

                        time = f"{year}-{month}-{day} {hour}:{minute}"


                        db.last_entry(time,message.from_user.id)
                        keyboard.add(*buttons_for_manager)
                        await message.answer(f"Welcome {message.from_user.first_name}", reply_markup=keyboard) 
                else:
                    await message.answer("You are not an admin!")
        else:
            await message.answer("I think you forgot your password👨🏻‍💻")
    else:
            await message.answer("Mr/Mrs please send this command like that /manager: your_key")



@dp.message_handler(lambda message: message.text == "Drivers")
async def drivers(message: types.Message):
    all_drivers, total_count = db.catch_all_drivers()
    
    # Concatenate all driver names into one string
    drivers_message = f"Drivers:\n{'-' * 30}\n" + "\n".join(driver[0] for driver in all_drivers)
    
    # Send the message with all driver names and the total count
    await message.answer(f"Total number of drivers: {total_count}\n{drivers_message}")








@dp.message_handler(lambda message: message.text == "Works")
async def works(message: types.Message):
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count = db.catch_works()
    in_prog = len(catch_in_progress)
    # Limit the number of works to 10 for catch_finished
    catch_finished = catch_finished[:10]

    # Create a list to store the finished works
    Finished_Works = []
    if catch_finished:
        # Add each finished work to the Finished_Works list
        for idx, row in enumerate(catch_finished, start=1):
            Finished_Works.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for finished works
        finished_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(catch_finished[:10], start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"finished_{row[0]}")
            finished_keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 finished works
        if len(catch_finished) > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_finished")
            finished_keyboard_markup.add(next_page_button)

        # Send the list of finished works with inline keyboard
        await message.answer("Finished Works:", reply_markup=finished_keyboard_markup)

    # Limit the number of works to 10 for catch_in_progress
    catch_in_progress = catch_in_progress[:10]

    # Create a list to store the in-progress works
    In_Progress_Works = []
    if catch_in_progress:
        # Add each in-progress work to the In_Progress_Works list
        for idx, row in enumerate(catch_in_progress, start=1):
            In_Progress_Works.append(f"{idx}. Customer: {row[1]}\n{'-'*50}\n")

        # Create inline keyboard markup with buttons labeled 1 to 10 for in-progress works
        in_progress_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(catch_in_progress, start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"progress_{row[0]}")
            in_progress_keyboard_markup.add(button)

        if in_prog > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_progress")
            in_progress_keyboard_markup.add(next_page_button)

        # Send the list of in-progress works with inline keyboard
        await message.answer(
            f"Page 1\n\nWorks In Progress:\n\n{''.join(In_Progress_Works)} ",  # Include the page number in the message text
            reply_markup=in_progress_keyboard_markup
        )
    else:
        await message.answer("No works in progress at the moment.")








@dp.callback_query_handler(lambda query: query.data == "next_page_progress")
async def next_page_progress(callback_query: types.CallbackQuery):
    # Get the current message
    message = callback_query.message

    # Get the current state of works in progress
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count = db.catch_works()

    # Extract the page number from the message text
    current_page = int(message.text.split("Page ")[1].split('\n')[0])  # Assuming the page number is stored as "Page {number}"

    # Calculate the start index for the next page
    start_index = current_page * 10

    # Get the works for the next page
    next_page_works = catch_in_progress[start_index:start_index + 10]

    # Create a list to store the works for the next page
    In_Progress_Works = []
    for idx, row in enumerate(next_page_works, start=start_index + 1):
        In_Progress_Works.append(f"{idx}. Customer: {row[1]}\n{'-' * 50}\n")

    # Create inline keyboard markup with buttons labeled based on the next page
    in_progress_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
    for idx, row in enumerate(next_page_works, start=start_index + 1):
        button = types.InlineKeyboardButton(str(idx), callback_data=f"progress_{row[0]}")
        in_progress_keyboard_markup.add(button)

    # Add "Previous Page" button
    prev_page_button = types.InlineKeyboardButton("Previous Page", callback_data="prev_page_progress")
    in_progress_keyboard_markup.add(prev_page_button)

    # Send the list of works for the next page with inline keyboard
    await message.edit_text(
        f"Page {current_page + 1}\n\nWorks In Progress:\n\n{''.join(In_Progress_Works)} ",  # Update the page number
        reply_markup=in_progress_keyboard_markup
    )


@dp.callback_query_handler(lambda query: query.data == "prev_page_progress")
async def prev_page_progress(callback_query: types.CallbackQuery):
    # Get the current message
    message = callback_query.message

    # Get the current state of works in progress
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count = db.catch_works()

    # Extract the page number from the message text
    current_page = int(message.text.split("Page ")[1].split('\n')[0])  # Assuming the page number is stored as "Page {number}"

    # Calculate the start index for the previous page
    start_index = (current_page - 2) * 10  # Subtracting 2 to go to the previous page and then multiplying by 10

    # Get the works for the previous page
    prev_page_works = catch_in_progress[start_index:start_index + 10]

    # Create a list to store the works for the previous page
    Prev_In_Progress_Works = []
    for idx, row in enumerate(prev_page_works, start=start_index + 1):
        Prev_In_Progress_Works.append(f"{idx}. Customer: {row[1]}\n{'-'*50}\n")

    # Create inline keyboard markup with buttons labeled based on the previous page
    prev_page_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
    for idx, row in enumerate(prev_page_works, start=start_index + 1):
        button = types.InlineKeyboardButton(str(idx), callback_data=f"progress_{row[0]}")
        prev_page_keyboard_markup.add(button)

    # Add "Next Page" button
    next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_progress")
    prev_page_keyboard_markup.add(next_page_button)

    # Send the list of works for the previous page with inline keyboard
    await message.edit_text(
        f"Page {current_page - 1}\n\nWorks In Progress:\n\n{''.join(Prev_In_Progress_Works)}",  # Update the page number
        reply_markup=prev_page_keyboard_markup
    )

@dp.callback_query_handler(lambda query: query.data.startswith("finished_"))
async def progress_id(query: types.CallbackQuery):
    id = query.data.split("_")[1]
 
    job_data = db.catch_job_by_id(id)
    keyboard = InlineKeyboardMarkup(row_width=5)
    back = InlineKeyboardButton("Back", callback_data="Back_finshed")
    keyboard.add(back)
    for data in job_data:
        template = f"Customer: {data[0]}\n\n{'-' * 50}\n\nDriver Name: {data[1]}\n\n{'-' * 50}\n\nLane: {data[3]}\n\n{'-' * 50}\n\nRate: {data[4]}"

        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith("progress_"))
async def progress_id(query: types.CallbackQuery):
    id = query.data.split("_")[1]
 
    job_data = db.catch_job_by_id(id)
    keyboard = InlineKeyboardMarkup(row_width=5)
    back = InlineKeyboardButton("Back", callback_data="Back_progress")
    keyboard.add(back)
    for data in job_data:
        template = f"Customer: {data[0]}\n\n{'-' * 50}\n\nDriver Name: {data[1]}\n\n{'-' * 50}\n\nLane: {data[3]}\n\n{'-' * 50}\n\nRate: {data[4]}"

        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)





@dp.callback_query_handler(lambda query: query.data.startswith("Back_"))
async def back(query: types.CallbackQuery):
    # Extract the action from the callback data
    action = query.data.split("_")[1]

    # Retrieve the necessary data
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count = db.catch_works()

    # Check the action
    if action == "progress":
        catch_in_progress = catch_in_progress[:10]

        # Create a list to store the in-progress works
        In_Progress_Works = []
        if catch_in_progress:
            # Create inline keyboard markup with buttons labeled 1 to 10 for in-progress works
            in_progress_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)

            for idx, row in enumerate(catch_in_progress, start=1):
                button = types.InlineKeyboardButton(str(idx), callback_data=f"progress_{row[0]}")
                in_progress_keyboard_markup.add(button)
        
                # Add each in-progress work to the In_Progress_Works list
                In_Progress_Works.append(f"{idx}. Customer: {row[1]}\n{'-'*50}\n")

            # Add "Next Page" button if there are more than 10 works in progress
            if in_progress_count > 10:
                next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_progress")
                in_progress_keyboard_markup.add(next_page_button)

            # Send the list of in-progress works with inline keyboard
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=f"Page 1\n\nWorks In Progress:\n\n{''.join(In_Progress_Works)}\n", reply_markup=in_progress_keyboard_markup)

    elif action == "finished":
        catch_finished = catch_finished[:10]

        # Create a list to store the finished works
        Finished_Works = []
        if catch_finished:
            # Create inline keyboard markup with buttons labeled 1 to 10 for finished works
            finished_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)

            for idx, row in enumerate(catch_finished[:10], start=1):
                button = types.InlineKeyboardButton(str(idx), callback_data=f"finished_{row[0]}")
                finished_keyboard_markup.add(button)

            # Add "Next Page" button if there are more than 10 finished works
            if finished_count > 10:
                next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_finished")
                finished_keyboard_markup.add(next_page_button)

            # Send the list of finished works with inline keyboard
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=f"Page 1\n\nFinished Works:\n\n{row[1]}", reply_markup=finished_keyboard_markup)






@dp.message_handler(lambda message: message.text == "Managers")
async def managers(message: types.Message):
    print('manager')
    adminNames = db.catch_managers()
    
    for names in adminNames:



        template = f"Name: {names[0]}\n{'-'*45}\nLast entry: {names[1]}"

        await message.answer(template)



@dp.message_handler(lambda message: message.text == "Add new manager")
async def new_manager(message: types.Message):
    admin_status = db.catch_admin_status(message.from_user.id)

    if admin_status[0] == "Super":
        token = generate_random_token()
        url = generate_bot_url(token)
        tokens['token'] = token


        await message.answer(f"Link for add new manager\n\n{url}")

    else:
        await message.answer("You have not a permission for this command")


def generate_random_token(length=8):
    numbers = string.digits
    return ''.join(random.choice(numbers) for _ in range(length))

def generate_bot_url(token):
    return f"https://t.me/TaskTrackrBot?start={token}"




@dp.message_handler(lambda message: message.text == "Remove manager")
async def remove_manager(message: types.Message):
    adminNames = db.catch_managers()
    keyboard = InlineKeyboardMarkup()

    text = 0
    for names in adminNames:
        button = InlineKeyboardButton(text=f"{text + 1}", callback_data=f"remove_{names[0]}")
        keyboard.add(button)

        await message.answer(f"Please select manager\n\n{text + 1}. {names[0]}", reply_markup=keyboard)
    



@dp.callback_query_handler(lambda query: query.data.startswith("remove_"))
async def call(query: types.CallbackQuery):
    admin_name = query.data.split("_")[1]
    db.remove_manager(admin_name)

    await query.message.answer("Succesfuly removed")











if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
