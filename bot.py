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


import pytesseract
from PIL import Image


def tesseract(image_name):
    # Path to the image file
    image_path = image_name

    # Path to Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)

    # Use pytesseract to do OCR on the image
    text = pytesseract.image_to_string(image)

    return text





def fuel_data(file_name):
    try:
        # Read the Excel file
        df = pd.read_excel(file_name)
        
        # Filter rows where specific column contains float values
        amt_column = df.iloc[:, 15]  # Assuming 'Unnamed: 15' is the 16th column
        float_values = amt_column.apply(lambda x: isinstance(x, (float, int)))
        filtered_df = df[float_values].copy()  # Create a copy to avoid the warning
        
        # Filter out rows where 'Unnamed: 4' column contains float values
        filtered_df = filtered_df[~filtered_df['Unnamed: 4'].apply(lambda x: isinstance(x, (float, int)))]
        
        # Rename columns to 'Unnamed: 15' and 'Unnamed: 1'
        filtered_df.columns = ['Unnamed: 15' if col == 'Column_15' else 'Unnamed: 1' if col == 'Column_1' else col for col in filtered_df.columns]
        
        # Remove quotation marks using .loc[]
        filtered_df.loc[:, 'Unnamed: 15'] = filtered_df['Unnamed: 15'].astype(str).str.replace('"', '')
        
        # Convert 'Unnamed: 15' column to numeric using .loc[] to avoid the warning
        filtered_df.loc[:, 'Unnamed: 15'] = pd.to_numeric(filtered_df['Unnamed: 15'], errors='coerce')
        
        # Drop rows with NaN values in the 'Unnamed: 15' column
        filtered_df = filtered_df.dropna(subset=['Unnamed: 15'])
        
        # Group by 'Unnamed: 1' (Driver Name) and calculate the total fuel consumed and number of days worked
        grouped_df = filtered_df.groupby('Unnamed: 1').agg({'Unnamed: 15': 'sum', 'Unnamed: 4': 'nunique'}).reset_index()
        grouped_df.columns = ['Driver Name', 'Total Fuel', 'Total Days Worked']
        
        # Convert dataframe to a list of tuples
        fuel_data_list = list(grouped_df.itertuples(index=False, name=None))
        
        return fuel_data_list
        
    except FileNotFoundError:
        print(f"File '{file_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")




@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def screenshot(message: types.Message):
    photo = message.photo[-1]
    # Download the photo by file ID
    file_path = await photo.download()
    file_path = str(file_path)
    test_path = file_path.split("=")[1].replace("'", "").replace(">", "")
    print(f"File Path:{test_path}")
    text = tesseract(test_path)
    

    print(text)




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


import fitz

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with fitz.open(pdf_path) as pdf:
        # Get the second page
        page = pdf[1]  # Index starts from 0, so 1 represents the second page
        
        # Extract text from the page
        text = page.get_text()
        # print(text.split("\n"))
        
        return text



def find_next_line_after_week(text_content):
    # Split the text by lines
    lines = text_content.split('\n')
    
    # Search for the line containing "Week"
    for i, line in enumerate(lines):
        if line == "Week":
            # Check if the next line exists
            if i + 1 < len(lines):
                return lines[i + 1]
            else:
                return "Next line after 'Week' not found"
    
    return "'Week' not found"

@dp.message_handler(commands=['new_order'])
async def mute_user_command(message: types.Message):
    print("NewOreder")
    # Check if the sender of the message is an admin
    await message.delete()
    
    replied_to_message = message.reply_to_message
    if replied_to_message and replied_to_message.text:
                message_text = replied_to_message.text

            # Use regular expressions to extract information
           
                
                unit = message_text.split("Load:")[1].split(" ")[2].split('\n')[0]
                driver_name = message_text.split("👤")[1].split(" ")[2].split("\n")[0]
                dh = message_text.split("DH")[1].split(" ")[1].split("\n")[0]
                customer_name = message_text.split("📦")[1].split(" ")[2]
                thre = message_text.split("————————————————")[2].split("\n")[3].split("   ")[0]
                four = message_text.split("————————————————")[2].split("\n")[4].split('   ')[0]
                bosh = f"{thre} - {four}"
                
                thre_del = message_text.split("————————————————")[3].split("\n")[3].split("   ")[0]
                four_del = message_text.split("————————————————")[3].split("\n")[4].split('   ')[0]
                oxr = f"{thre_del} {four_del}"
                lane = f"{bosh} - {oxr}"
                pu_data = message_text.split("PU:")[1].split("\n")[0]
                
                manager = message_text.split("👨🏻‍💻: ")[1].split("\n")[0]

                rate = message_text.split("Rate: ")[1].split("\n")[0]

                miles = message_text.split("Miles: ")[1].split("\n")[0]

                gross = message_text.split("Gross: ")[1].split("\n")[0]
                
                p_m = int(miles) / int(gross.split("$")[0]) 

                factoring = 0.01 * int(gross.split("$")[0])

                dispach = 0.03 * int(gross.split("$")[0])
                


                all_miles = int(dh)+ int(miles)

                # Generate or retrieve the unique jobID
                jobID = generate_job_id()  # Assuming you have a function to generate a unique job ID

                # Insert data into the database
                db.insert_all(jobID, customer_name, unit, driver_name, lane, pu_data, rate, dh, miles, manager, "In Progress")

                db.insert_all_to_monthly(jobID, customer_name, unit, driver_name, lane, pu_data, "In Progress", rate, dh, miles, manager)
                # Call the catch_driver function with the appropriate parameters
                catch_driver(unit, driver_name, customer_name)

                db.insert_driver_name(jobID, unit, driver_name, gross, p_m, all_miles, all_miles, factoring, dispach)


                await message.answer("Order added to Database!")    




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
            fuel_text = "Total fuel values per driver:\n"
            fuel_text += "{:<20} {:<10} {:<15}\n".format("Driver Name", "Total Fuel", "Total Days Worked")
            fuel_text += "-" * 50 + "\n"
            for driver, fuel, days_worked in data:
                db.update_fuel(driver, fuel, days_worked)
                fuel_text += "{:<20} {:<10} {:<15}\n".format(driver, fuel, days_worked)
            
            # Print the fuel data
            print(fuel_text)

        await message.delete()


    elif message.document.mime_type == 'application/pdf':
        print("PDF")




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
            buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', 'Remove manager', "Monthly Board"]
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
    
    # Create an inline keyboard with buttons for each driver
    keyboard = types.InlineKeyboardMarkup(row_width=3)  # Adjust the row_width value as needed
    n = 0
    for driver_name in all_drivers:
        print(type(driver_name[0]))
        keyboard.add(types.InlineKeyboardButton(text=str(n + 1), callback_data=f"driver_{driver_name[0]}"))
        n += 1  # Increase n for the next iteration

    # Send the message with all driver names and the total count along with the inline keyboard
    await message.answer(f"Total number of drivers: {total_count}", reply_markup=keyboard)

data_l_d = {}

@dp.message_handler(commands=['layover'])
async def layover(message: types.Message):
    await message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[0], callback_data=f"driver-name_{driver[0]}")
        keyboard.add(button)
    await message.answer("Please select driver", reply_markup=keyboard)
    data_l_d['money'] = message.text.split(" ")[1]





@dp.callback_query_handler(lambda query: query.data.startswith("driver-name"))
async def lay(query: types.CallbackQuery):
    driver_name = query.data.split("_")[1]

    await query.message.answer("Ok layover added")

    layover = str(data_l_d["money"])
 
    db.insert_layover(driver_name, layover)

@dp.message_handler(commands=['detention'])
async def layover(message: types.Message):
    await message.delete()
    driver_names = db.catch_all_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
        button = types.InlineKeyboardButton(text=driver[0], callback_data=f"driver-detention_{driver[0]}")
        keyboard.add(button)
        await message.answer("Please select driver", reply_markup=keyboard)
    data_l_d['detention'] = message.text.split(" ")[1]


@dp.callback_query_handler(lambda query: query.data.startswith("driver-detention"))
async def lay(query: types.CallbackQuery):
    driver_name = query.data.split("_")[0]

    await query.message.answer("Ok detention added")

    detention = data_l_d["detention"]

    db.insert_detention(driver_name, detention)



@dp.callback_query_handler(lambda query: query.data.startswith("driver_"))
async def driver_info(callback: types.CallbackQuery):
    print(callback.data)
    global status
    driver_name = callback.data.split("_")[1]

    data = db.count_work_by_name(driver_name)
    keybard = InlineKeyboardMarkup(row_width=5)

    back = InlineKeyboardButton(text="Back", callback_data='back')
    keybard.add(back)
    info_driver_status = db.get_status_payment(driver_name)
    print(info_driver_status)
    status = info_driver_status[0][2]
    if status == "PAID":
        for info in data:
            template = f"Driver name: {info[1]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[2]}"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "WAIT":
        for info in data:
            template = f"Driver name: {info[1]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[2]}\n\nThere is unpaid work"
        unpaid_keyboard = types.InlineKeyboardButton(text="PAID", callback_data=f"paid_{info_driver_status[0][0]}")
        keybard.add(unpaid_keyboard)        
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
                
    else:
        for info in data:
            template = f"Driver name: {info[1]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[2]}"
            
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)


@dp.callback_query_handler(lambda query: query.data.startswith("paid_"))
async def paid(query: types.CallbackQuery):
    id = query.data.split("_")[1]

    db.update_status(id)

    await query.message.answer("Ok Payment Status changed")


import sqlite3
import pandas as pd

def export_table_to_excel(db_file, table_name, excel_file):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_file)
    
    # Read data from the database table into a pandas DataFrame
    query = f"SELECT * FROM {table_name};"
    df = pd.read_sql_query(query, conn)
    
    # Remove the first column (assuming it's the primary key or an auto-increment ID)
    df = df.iloc[:, 1:]
    
    # Export DataFrame to Excel
    df.to_excel(excel_file, index=False)
    
    # Close the database connection
    conn.close()
    print(f"Data from table '{table_name}' exported to '{excel_file}' successfully.")

# Example usage





def monthly_board():
    db_file = "database.db"  # Replace with your SQLite database file path
    table_name = "mothly"  # Replace with the name of your table
    excel_file = "Monthly_Board.xlsx"  # Replace with the desired Excel file name/path
    export_table_to_excel(db_file, table_name, excel_file)




# Assuming bot is your aiogram.Bot instance
@dp.message_handler(lambda message: message.text == "Monthly Board")
async def exel(message: types.Message):
    # Call your function to export data to Excel
    monthly_board()
    # Send the Excel document to the user
    await bot.send_document(chat_id=message.from_user.id, document=open("Monthly_Board.xlsx", "rb"))





@dp.callback_query_handler(lambda query: query.data == "back")
async def back_to(callback: types.CallbackQuery):
    all_drivers, total_count = db.catch_all_drivers()
    
    # Create an iline keyboard with buttons fnor each driver
    keyboard = types.InlineKeyboardMarkup(row_width=3)  # Adjust the row_width value as needed
    n = 0
    for driver_name in all_drivers:
        print(type(driver_name[0]))
        keyboard.add(types.InlineKeyboardButton(text=str(n + 1), callback_data=f"driver_{driver_name[0]}"))
        n += 1  # Increase n for the next iteration
    
    # Send the message with all driver names and the total count along with the inline keyboard
    await bot.edit_message_text(chat_id=callback.from_user.id,message_id=callback.message.message_id,text=f"Total number of drivers: {total_count}", reply_markup=keyboard)





from aiogram import types

@dp.message_handler(lambda message: message.text == "Works")
async def works(message: types.Message):
    keyboard_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    finished_button = types.KeyboardButton("Finished works")
    in_progress_button = types.KeyboardButton("In progress works")
    rejected_button = types.KeyboardButton("Rejected works")
    canceled_button = types.KeyboardButton("Canceled works")
    keyboard_markup.add(finished_button, in_progress_button, rejected_button, canceled_button)
    await message.answer("Please select an option:", reply_markup=keyboard_markup)

from aiogram import types

@dp.message_handler(lambda message: message.text == "Finished works")
async def finished_works(message: types.Message):
    # Get data for finished works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()

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
    else:
        await message.answer("No finished works at the moment.")

@dp.message_handler(lambda message: message.text == "In progress works")
async def in_progress_works(message: types.Message):
    # Get data for in-progress works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()

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

        if in_progress_count > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_progress")
            in_progress_keyboard_markup.add(next_page_button)

        # Send the list of in-progress works with inline keyboard
        await message.answer(
            f"Page 1\n\nWorks In Progress:\n\n{''.join(In_Progress_Works)} ",  # Include the page number in the message text
            reply_markup=in_progress_keyboard_markup
        )
    else:
        await message.answer("No works in progress at the moment.")

@dp.message_handler(lambda message: message.text == "Rejected works")
async def rejected_works(message: types.Message):
    # Get data for rejected works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()
    works_title = "Rejected"
    # Limit the number of works to 10 for catch_rejected
    works = catch_rejected[:10]
    count = rejected_count

    # Create a list to store the rejected works
    Works_List = []
    if works:
        # Add each work to the Works_List
        for idx, row in enumerate(works, start=1):
            Works_List.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for works
        keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(works, start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"{works_title.lower()}_{row[0]}")
            keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 works
        if count > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data=f"next_page_{works_title.lower()}")
            keyboard_markup.add(next_page_button)

        # Send the list of works with inline keyboard
        await message.answer(f"{works_title.capitalize()} Works:", reply_markup=keyboard_markup)
    else:
        await message.answer(f"No {works_title.lower()} works at the moment.")


@dp.callback_query_handler(lambda query: query.data.startswith("rejected_"))
async def rejected_callback(query: types.CallbackQuery):
    # Extract the jobID from the callback data
    job_id = query.data.split("_")[1]

    # Fetch the details of the rejected work using the jobID
    rejected_work_details = db.get_work_details_by_id(job_id)

    if rejected_work_details is None:
        await query.message.answer("Work details not found.")
        return

    # Prepare the message text
    message_text = f"Details of Rejected Work (Job ID: {job_id}):\n\n"
    for key, value in rejected_work_details.items():
        message_text += f"{key.capitalize()}: {value}\n"

    # Create inline keyboard markup with "Back" button
    back_button = types.InlineKeyboardButton("Back", callback_data="back_to_rejected")
    keyboard_markup = types.InlineKeyboardMarkup().add(back_button)

    # Send the message with the details of the rejected work and the "Back" button
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard_markup)

@dp.callback_query_handler(lambda query: query.data == "back_to_rejected")
async def back_to_rejected_callback(query: types.CallbackQuery):
    # Get data for rejected works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()
    works_title = "Rejected"

    # Limit the number of works to 10 for catch_rejected
    works = catch_rejected[:10]
    count = rejected_count

    # Create a list to store the rejected works
    Works_List = []
    if works:
        # Add each work to the Works_List
        for idx, row in enumerate(works, start=1):
            Works_List.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for works
        keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(works, start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"{works_title.lower()}_{row[0]}")
            keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 works
        if count > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data=f"next_page_{works_title.lower()}")
            keyboard_markup.add(next_page_button)

        # Send the list of works with inline keyboard
        await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=f"{works_title.capitalize()} Works:",
            reply_markup=keyboard_markup
        )
    else:
        await query.message.answer(f"No {works_title.lower()} works at the moment.")




@dp.message_handler(lambda message: message.text == "Canceled works")
async def canceled_works(message: types.Message):
    # Get data for canceled works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()
    works_title = "Canceled"
    # Limit the number of works to 10 for catch_canceled
    works = catch_canceled[:10]
    count = canceled_count

    # Create a list to store the canceled works
    Works_List = []
    if works:
        # Add each work to the Works_List
        for idx, row in enumerate(works, start=1):
            Works_List.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for works
        keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(works, start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"canceled_{row[0]}")
            keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 works
        if count > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data=f"next_page_{works_title.lower()}")
            keyboard_markup.add(next_page_button)

        # Send the list of works with inline keyboard
        await message.answer(f"{works_title.capitalize()} Works:", reply_markup=keyboard_markup)
    else:
        await message.answer(f"No {works_title.lower()} works at the moment.")


@dp.callback_query_handler(lambda query: query.data.startswith("canceled_"))
async def canceled_callback(query: types.CallbackQuery):
    # Extract the jobID from the callback data
    job_id = query.data.split("_")[1]

    # Fetch the details of the canceled work using the jobID
    canceled_work_details = db.get_work_details_by_id(job_id)

    print(canceled_work_details)
    # Prepare the message text
    message_text = f"Details of Canceled Work (Job ID: {job_id}):\n\n"
    for key, value in canceled_work_details.items():
        message_text += f"{key.capitalize()}: {value}\n"

    # Create inline keyboard markup with "Back" button
    back_button = types.InlineKeyboardButton("Back", callback_data="back_to_canceled")
    keyboard_markup = types.InlineKeyboardMarkup().add(back_button)

    # Send the message with the details of the canceled work and the "Back" button
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard_markup)


@dp.callback_query_handler(lambda query: query.data == "back_to_canceled")
async def back_to_canceled_callback(query: types.CallbackQuery):
    # Get data for canceled works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()
    works_title = "Canceled"

    # Limit the number of works to 10 for catch_canceled
    works = catch_canceled[:10]
    count = canceled_count

    # Create a list to store the canceled works
    Works_List = []
    if works:
        # Add each work to the Works_List
        for idx, row in enumerate(works, start=1):
            Works_List.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for works
        keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(works, start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"{works_title.lower()}_{row[0]}")
            keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 works
        if count > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data=f"next_page_{works_title.lower()}")
            keyboard_markup.add(next_page_button)

        # Send the list of works with inline keyboard
        await bot.edit_message_text(
            chat_id=query.from_user.id,
            message_id=query.message.message_id,
            text=f"{works_title.capitalize()} Works:",
            reply_markup=keyboard_markup
        )
    else:
        await query.message.answer(f"No {works_title.lower()} works at the moment.")



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

info = {}

@dp.callback_query_handler(lambda query: query.data.startswith("progress_"))
async def progress_id(query: types.CallbackQuery):
    id = query.data.split("_")[1]
    info.clear()
    info["ID"] = id
    job_data = db.catch_job_by_id(id)
    keyboard = InlineKeyboardMarkup(row_width=3)
    back = InlineKeyboardButton("Back", callback_data="Back_progress")
    finish = InlineKeyboardButton(text="Finished", callback_data="Finish")
    reject = InlineKeyboardButton(text="Reject", callback_data=f"reject_{id}")
    cancle = InlineKeyboardButton(text="Cancelled", callback_data=f"cancelled_{id}")
    keyboard.add(finish, reject, cancle, back)
    for data in job_data:
        template = f"Customer: {data[0]}\n\n{'-' * 50}\n\nDriver Name: {data[1]}\n\n{'-' * 50}\n\nLane: {data[3]}\n\n{'-' * 50}\n\nRate: {data[4]}"

        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("reject"))
async def reject(query: types.CallbackQuery):
    job_id = query.data.split("_")[1]
 
 
    await query.message.answer("The work is rejected")

    db.reject(job_id)


@dp.callback_query_handler(lambda query: query.data.startswith("Back_"))
async def back(query: types.CallbackQuery):
    # Extract the action from the callback data
    action = query.data.split("_")[1]
    print(action)
    # Retrieve the necessary data
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count = db.catch_works()

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

    elif action == "finshed":
        print("Finihs")
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

    elif action == "rejected":
        catch_rejected = catch_rejected[:10]
    
        # Create a list to store the rejected works
        Rejected_Works = []
        if catch_rejected:
            # Create inline keyboard markup with buttons labeled 1 to 10 for rejected works
            rejected_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)

            for idx, row in enumerate(catch_rejected[:10], start=1):
                button = types.InlineKeyboardButton(str(idx), callback_data=f"rejected_{row[0]}")
                rejected_keyboard_markup.add(button)

            # Add "Next Page" button if there are more than 10 rejected works
            if rejected_count > 10:
                next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_rejected")
                rejected_keyboard_markup.add(next_page_button)

            # Send the list of rejected works with inline keyboard
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=f"Page 1\n\nRejected Works:\n\n{row[1]}", reply_markup=rejected_keyboard_markup)

    elif action == "canceled":
        catch_canceled = catch_canceled[:10]
    
        # Create a list to store the canceled works
        Canceled_Works = []
        if catch_canceled:
            # Create inline keyboard markup with buttons labeled 1 to 10 for canceled works
            canceled_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)

            for idx, row in enumerate(catch_canceled[:10], start=1):
                button = types.InlineKeyboardButton(str(idx), callback_data=f"canceled_{row[0]}")
                canceled_keyboard_markup.add(button)

            # Add "Next Page" button if there are more than 10 canceled works
            if canceled_count > 10:
                next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_canceled")
                canceled_keyboard_markup.add(next_page_button)

            # Send the list of canceled works with inline keyboard
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=f"Page 1\n\nCanceled Works:\n\n{row[1]}", reply_markup=canceled_keyboard_markup)

    

@dp.callback_query_handler(lambda query: query.data == "Finish")
async def finish_work(callback: types.CallbackQuery, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Yes", "No Wait"]
    keyboard.add(*buttons)
    await callback.message.answer("Has the driver been paid?", reply_markup=keyboard)

    await state.set_state(States.paid_status)



@dp.message_handler(state=States.paid_status)
async def paid_status(message: types.Message, state: FSMContext):
    if message.text == "Yes":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Yes", "No Wait"]
        info['paid'] = "PAID"
        keyboard.add(*buttons)
        await message.answer("Has the AMZ payment been paid?", reply_markup=keyboard)
        await state.set_state(States.note)

    if message.text == "No Wait":
        id = info["ID"]
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons_for_super_admin = ['Drivers', 'Works', 'Statistic', 'Managers', 'Add new manager', 'Remove manager']
        keyboard.add(*buttons_for_super_admin)
        db.update_payment_status_to_wait(id)
        await message.answer("After payment, you can change the information from within Drivers", reply_markup=keyboard)
        await state.finish()






@dp.message_handler(state=States.note)
async def note(message: types.Message, state: FSMContext):
    if message.text == "Yes":
        keyboard = types.ReplyKeyboardRemove()
        await message.answer("Please enter Note", reply_markup=keyboard)
        await state.set_state(States.no_note)
    if message.text == "No":
        job_id = info["ID"]
        payment_status = info["paid"]
        amz_status = info["amz"]
        await message.answer("The work is completed")
        db.update_monthly_without_note(payment_status, amz_status, job_id)
        await message.answer("Job is finished")

        await state.finish()


@dp.message_handler(state=States.no_note)
async def update_data(message: types.Message):
    job_id = info["ID"]
    payment_status = info["paid"]
    amz_status = info["amz"]
    note = message.text

    if note:
        db.update_monthly(payment_status, amz_status, note, job_id)

        await message.answer("Job is finished")


@dp.message_handler(lambda message: message.text == "Managers")
async def managers(message: types.Message):
    print('manager')
    adminNames = db.catch_managers()
    
    for names in adminNames:



        template = f"Name: {names[0]}\n{'-'*45}\nLast entry: {names[1]}"

        await message.answer(template)



@dp.message_handler(lambda message: message.text == "All Data")
async def exel_all(message: types.Message):
    await message.answer("Wait a minute data's are collecting....")

    

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
