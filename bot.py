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
import numpy as np
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

chat = "@qwerty181898"

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



def find_next_line_after_week(text_content, line_):
    # Split the text by lines
    lines = text_content.split('\n')
    
    # Search for the line containing "Week"
    for i, line in enumerate(lines):
        if line == line_:
            # Check if the next line exists
            if i + 1 < len(lines):
                return lines[i + 1]
            else:
                return "Next line after 'Week' not found"
    
    return "'Week' not found"

@dp.message_handler(commands=['new_order'])
async def mute_user_command(message: types.Message):
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

                db.insert_all_to_monthly(jobID, customer_name, unit, driver_name, lane, pu_data, "In Progress", rate, dh, miles, manager, "In Progress")
                # Call the catch_driver function with the appropriate parameters
                al = catch_driver(unit, driver_name, customer_name)
           
                db.insert_driver_name(jobID, unit, driver_name, gross, p_m, all_miles, all_miles, factoring, dispach)


                await message.answer("Order added to Database!")    

def process_toll_details(file_path):
    df = pd.read_csv(file_path)
    
    # Replace non-finite values with NaN
    df['EquipID'] = df['EquipID'].replace([np.inf, -np.inf], np.nan)
    
    # Convert EquipID to integers, ignoring NaN values
    df['EquipID'] = df['EquipID'].astype('Int64')
    
    # Drop rows where EquipID is NaN
    df = df.dropna(subset=['EquipID'])
    
    # Create a dictionary to store EquipID and corresponding InvoiceDate and Toll_Amount
    equipid_invoice_toll = dict(zip(zip(df['EquipID'], df['InvoiceDate']), df['Toll_Amount']))
    
    # Prepare the data to return
    data_to_return = []
    for (equip_id, invoice_date), toll_amount in equipid_invoice_toll.items():
        data_to_return.append((equip_id, invoice_date, toll_amount))
    
    return data_to_return


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


    elif message.document.mime_type == 'application/pdf'  and message.caption == '/pdf':
        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        # Download the file
        downloaded_file = await bot.download_file(file_path)
        
        # Save the file locally
        file_name = f"downloaded_{file_id}.pdf"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())
        test = extract_text_from_pdf(file_name)
        rate = find_next_line_after_week(test, "Week")
        unit = find_next_line_after_week(test, "Charge")
        unit_num = unit.split(":")[1]
        
        db.update_truck_payment(unit_num, rate)

    elif message.document.mime_type == 'text/csv'  and message.caption == '/csv':

        file_id = message.document.file_id
        file_info = await bot.get_file(file_id)
        file_path = file_info.file_path

        # Download the file
        downloaded_file = await bot.download_file(file_path)
        
        # Save the file locally
        file_name = f"downloaded_{file_id}.csv"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file.getvalue())


        toll = process_toll_details(file_name)
        print(toll)
        for t in toll:
            time_ = t[1].replace("'", "")
            print(t[0])
    
            db.update_tools(t[0], t[2], time_)

        os.remove(file_name)
            # os.remove(file_name)
    


  
        

@dp.message_handler(commands='manager')
async def admin_handler(message: types.Message):
    # db.add_admin(message.from_user.id)

    if " " in message.text:

        manager_key = message.text.split(" ")[1]
       


        manager_idx = db.admin_check()
        print(manager_idx)
        manager_exsist_key = db.catch_key(message.from_user.id)
        print(manager_exsist_key)
        admin_status = db.catch_admin_status(message.from_user.id)
        print(admin_status)
        if manager_exsist_key:
            if manager_key == manager_exsist_key[0]:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
                
                for manager_id in manager_idx:
                    print(manager_id)
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
                            keyboard.add(*buttons_for_super_admin)
                            await message.answer(f"Welcome {message.from_user.first_name}", reply_markup=keyboard) 
            else:
                        await message.answer("I think you forgot your password👨🏻‍💻")
        else:
                        await message.answer("You are not an admin!")
        
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
        keyboard.add(types.InlineKeyboardButton(text=f"{driver_name[0]}", callback_data=f"driver_{driver_name[0]}"))
        n += 1  # Increase n for the next iteration

    # Send the message with all driver names and the total count along with the inline keyboard
    await message.answer(f"Total number of drivers: {total_count}", reply_markup=keyboard)

data_l_d = {}


@dp.message_handler(commands=['pdINS'])
async def layover(message: types.Message):
    await message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[1], callback_data=f"driver-pdins_{driver[0]}")
        keyboard.add(button)
    await message.answer("Please select Load ID", reply_markup=keyboard)
    data_l_d['pdINs'] = message.text.split(" ")[1]






@dp.callback_query_handler(lambda query: query.data.startswith("driver-pdins_"))
async def lay(query: types.CallbackQuery):
        id = query.data.split("_")[1]
        # print(id)

        
        keyboard = InlineKeyboardMarkup()

        test, gross = db.get_jobs_by_driver(id)
        # print(test)
        n = 0
        text = ""
        for i in test:
            customer = i[1].replace('👤:', "")  
            # print(i)
            text = f"{n + 1}. Customer: {customer}\n\nDriver Name: {i[2]}\n\nPU: {i[3]}"
            
            button = InlineKeyboardButton(text=f"{n + 1}", callback_data=f"pdInss_{i[0]}")  # Changed "oter_" to "Other_"
        keyboard.add(button)
            
        back = InlineKeyboardButton(text="Back", callback_data="baks_tt_pdINS")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("pdInss_"))
async def update_layover(query: types.CallbackQuery):
    driver_name = query.data.split("_")[1]

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Ok layover added")

    layover = str(data_l_d["money"])
 
    db.pdINS(driver_name, layover)


@dp.callback_query_handler(lambda query: query.data == "baks_tt_pdINS")
async def back_to_lay(query: types.CallbackQuery):
  
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[1], callback_data=f"driver-pdins_{driver[0]}")
        keyboard.add(button)
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please select Load ID", reply_markup=keyboard)
    


@dp.message_handler(commands=['layover'])
async def layover(message: types.Message):
    await message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[1], callback_data=f"driver-name_{driver[0]}")
        keyboard.add(button)
    await message.answer("Please select Load ID", reply_markup=keyboard)
    data_l_d['money'] = message.text.split(" ")[1]






@dp.callback_query_handler(lambda query: query.data.startswith("driver-name"))
async def lay(query: types.CallbackQuery):
        id = query.data.split("_")[1]
        # print(id)

        
        keyboard = InlineKeyboardMarkup()

        test, gross = db.get_jobs_by_driver(id)
        # print(test)
        n = 0
        text = ""
        for i in test:
            customer = i[1].replace('👤:', "")  
            # print(i)
            text = f"{n + 1}. Customer: {customer}\n\nDriver Name: {i[2]}\n\nPU: {i[3]}"
            
            button = InlineKeyboardButton(text=f"{n + 1}", callback_data=f"layoverss_{i[0]}")  # Changed "oter_" to "Other_"
        keyboard.add(button)
            
        back = InlineKeyboardButton(text="Back", callback_data="baks_tt_lay")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data == "baks_tt_lay")
async def back_to_lay(query: types.CallbackQuery):
  
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[1], callback_data=f"driver-name_{driver[0]}")
        keyboard.add(button)
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please select Load ID", reply_markup=keyboard)
    




@dp.callback_query_handler(lambda query: query.data.startswith("layoverss_"))
async def update_layover(query: types.CallbackQuery):
    driver_name = query.data.split("_")[1]

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Ok layover added")

    layover = str(data_l_d["money"])
 
    db.insert_layover(driver_name, layover)
    



@dp.message_handler(commands=['detention'])
async def layover(message: types.Message):
    await message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[0], callback_data=f"driver-det_{driver[0]}")
        keyboard.add(button)
    await message.answer("Please select Load ID", reply_markup=keyboard)
    data_l_d['detention'] = message.text.split(" ")[1]



@dp.callback_query_handler(lambda query: query.data.startswith("driver-det"))
async def lay(query: types.CallbackQuery):
        id = query.data.split("_")[1]
        # print(id)

        
        keyboard = InlineKeyboardMarkup()

        test, gross = db.get_jobs_by_driver(id)
        # print(test)
        n = 0
        text = ""
        for i in test:
            customer = i[1].replace('👤:', "")  
            # print(i)
            text = f"{n + 1}. Customer: {customer}\n\nDriver Name: {i[2]}\n\nPU: {i[3]}"
            
            button = InlineKeyboardButton(text=f"{n + 1}", callback_data=f"detentionss_{i[0]}")  # Changed "oter_" to "Other_"
        keyboard.add(button)
            
        back = InlineKeyboardButton(text="Back", callback_data="baks_tt_det")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=text, reply_markup=keyboard)
@dp.callback_query_handler(lambda query: query.data == "baks_tt_det")
async def back_to_det(query: types.CallbackQuery):
    await query.message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[1], callback_data=f"driver-det_{driver[0]}")
        keyboard.add(button)
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please select Load ID", reply_markup=keyboard)
    

@dp.callback_query_handler(lambda query: query.data.startswith("detentionss_"))
async def update_layover(query: types.CallbackQuery):
    driver_name = query.data.split("_")[1]

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Ok detention added")

    layover = str(data_l_d["money"])
 
    db.insert_detention(driver_name, layover)
    

@dp.callback_query_handler(lambda query: query.data.startswith("driver_"))
async def driver_info(callback: types.CallbackQuery):
    print(callback.data)
    global status
    driver_name = callback.data.split("_")[1]

    
    keybard = InlineKeyboardMarkup(row_width=5)

    back = InlineKeyboardButton(text="Back", callback_data='back')
    keybard.add(back)
    info_driver_status = db.get_status_payment(driver_name)
 
    status = info_driver_status[0][2]
    data = db.count_work_by_name(driver_name, status)
    print(status)
    if status == "Finished":
        
        
        for info in data:
            print(info)
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "WAIT":
        
        for info in data:

            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            print(info)
            
            template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}\n\nThere is unpaid work"
        unpaid_keyboard = types.InlineKeyboardButton(text="PAID", callback_data=f"paid_{info_driver_status[0][0]}")
        keybard.add(unpaid_keyboard, work_button)        
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "Rejected":
        for info in data:
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "Cancled":
        for info in data:
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
                
    elif status == "In Progress":
        for info in data:
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)


@dp.message_handler(lambda message: message.text == "Change Data")
async def change_start(message: types.Message):
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data in ["next_page", "back_page"])
async def pagination_handler(query: types.CallbackQuery):
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup()
    page_size = 10
    current_page = int(query.message.text.split()[1]) if query.message.text else 1
    
    if query.data == "next_page":
        current_page += 1
    elif query.data == "back_page":
        current_page -= 1

    datas = datas[(current_page - 1) * page_size:current_page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)
    # Add "Back Page" button
    if current_page > 1:
        back_button = InlineKeyboardButton(text="Back Page", callback_data="back_page")
        keyboard.add(back_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await query.message.edit_text(text=f"Page {current_page}\n\n{template}", reply_markup=keyboard)
    await query.answer()  # Acknowledge the callback query


change_new = {}


@dp.callback_query_handler(lambda query: query.data.startswith("cchange_"))
async def change_main(queey: types.CallbackQuery):
    job_id = queey.data.split("_")[1] 
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton(text="Change Driver Name", callback_data=f"change_driver_name_{job_id}"),
        types.InlineKeyboardButton(text="Change Driver Payment", callback_data=f"change_driver_payment_{job_id}"),
        types.InlineKeyboardButton(text="Change Escrow", callback_data=f"change_escrow_{job_id}"),
        types.InlineKeyboardButton(text="Change Layover", callback_data=f"change_layover_{job_id}"),
        types.InlineKeyboardButton(text="Change Detention", callback_data=f"change_detention_{job_id}"),
        types.InlineKeyboardButton(text="Change Customer", callback_data=f"change_customer_{job_id}"),
        types.InlineKeyboardButton(text="Change Rate", callback_data=f"change_rate_{job_id}"),
        types.InlineKeyboardButton(text="Change Miles", callback_data=f"change_miles_{job_id}"),
        types.InlineKeyboardButton(text="Back", callback_data=f"back_for_change")
    ]
    keyboard.add(*buttons)

    await bot.edit_message_text(chat_id=queey.from_user.id, message_id = queey.message.message_id, text="Please select and option: ", reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data == "back_for_change")
async def change_name(query: types.CallbackQuery, state: FSMContext):
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=query.message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("change_driver_name_"))
async def change_name(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[3]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Driver Name")
    await state.set_state(States.change_name)

@dp.message_handler(state=States.change_name)
async def do_change_name(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    print()
    
    db.update_name_by_jobss(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)








@dp.callback_query_handler(lambda query: query.data.startswith("change_customer_"))
async def change_customer(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[2]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Customer")
    await state.set_state(States.change_customer)

@dp.message_handler(state=States.change_customer)
async def do_change_customer(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_customer_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)




@dp.callback_query_handler(lambda query: query.data.startswith("change_detention_"))
async def change_detention(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[2]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Detention")
    await state.set_state(States.change_detention)

@dp.message_handler(state=States.change_detention)
async def do_change_detention(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_detention_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("change_layover_"))
async def change_layover(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[2]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Layover")
    await state.set_state(States.change_detention)

@dp.message_handler(state=States.change_detention)
async def do_change_layover(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_detention_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)







@dp.callback_query_handler(lambda query: query.data.startswith("change_escrow_"))
async def change_Escrow(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[2]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Escrow")
    await state.set_state(States.change_detention)

@dp.message_handler(state=States.change_detention)
async def do_change_escrow(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_escrow_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith("change_escrow_"))
async def change_Escrow(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[2]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Escrow")
    await state.set_state(States.change_detention)

@dp.message_handler(state=States.change_detention)
async def do_change_escrow(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_escrow_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)





@dp.callback_query_handler(lambda query: query.data.startswith("change_driver_payment_"))
async def change_driver_payment(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[3]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter Driver Payment")
    await state.set_state(States.change_driver_payment)



@dp.message_handler(state=States.change_driver_payment)
async def do_driver_payment(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_driver_payment_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)



# @dp.callback_query_handler(lambda query: query.data.startswith("change_amz_payment_"))
# async def change_amz_payment(query: types.CallbackQuery, state: FSMContext):
#     job_id = query.data.split("_")[3]
#     change_new["job_id"] = job_id
#     await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter Driver Payment")
#     await state.set_state(States.change_amz_payment)



# @dp.message_handler(state=States.change_amz_payment)
# async def do_change_amz_payment(message: types.Message, state: FSMContext):
#     await message.delete()
#     await message.answer("Ok Changed!")
    
#     db.update_driver_payment_by_job(message.text, change_new["job_id"])
#     await state.finish()
#     datas = db.catch_for_change()
#     keyboard = InlineKeyboardMarkup(row_width=4)
#     page_size = 10
#     page = 1

#     if len(datas) > page_size:
#         datas = datas[(page - 1) * page_size:page * page_size]

#     buttons = []
#     for index, data in enumerate(datas, start=1):
#         button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"change_{data[0]}")
#         buttons.append(button)

#     # Distribute buttons into rows of 4
#     while buttons:
#         keyboard.row(*buttons[:4])
#         buttons = buttons[4:]

#     # Add "Next Page" button
#     if len(datas) == page_size:
#         next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
#         keyboard.add(next_button)

#     template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
#     await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("change_miles_"))
async def change_miles(query: types.CallbackQuery, state: FSMContext):
    job_id = query.data.split("_")[3]
    change_new["job_id"] = job_id
    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please enter new Mile")
    await state.set_state(States.change_driver_payment)



@dp.message_handler(state=States.change_driver_payment)
async def do_change_mile(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer("Ok Changed!")
    
    db.update_driver_payment_by_job(message.text, change_new["job_id"])
    await state.finish()
    datas = db.catch_for_change()
    keyboard = InlineKeyboardMarkup(row_width=4)
    page_size = 10
    page = 1

    if len(datas) > page_size:
        datas = datas[(page - 1) * page_size:page * page_size]

    buttons = []
    for index, data in enumerate(datas, start=1):
        button = InlineKeyboardButton(text=f"{index}. Customer: {data[2]}", callback_data=f"cchange_{data[0]}")
        buttons.append(button)

    # Distribute buttons into rows of 4
    while buttons:
        keyboard.row(*buttons[:4])
        buttons = buttons[4:]

    # Add "Next Page" button
    if len(datas) == page_size:
        next_button = InlineKeyboardButton(text="Next Page", callback_data="next_page")
        keyboard.add(next_button)

    template = "\n\n".join([f"Customer: {data[2]}\nDriver Name: {data[1]}\nUnit: {data[3]}\nPU: {data[4]}\n{'-' * 50}" for data in datas])
    await bot.send_message(chat_id=message.from_user.id, text=f"Page {page}\n\n{template}", reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith("work_user_"))
async def work_user_callback(callback: types.CallbackQuery):
    driver_name = callback.data.split("_")[2]  # Extracting the driver name from the callback data

    # Fetching the list of jobs for the specified driver name
    jobs_list, gross = db.get_jobs_by_driver(driver_name)

    if jobs_list:
        # Initialize the message text to an empty string
        message_text = ""
        print(gross)
        # Initialize a list to store inline keyboard buttons
        keyboard_buttons = []

        # Iterate over the jobs list to create buttons and concatenate job information
        for idx, job, in enumerate(jobs_list, start=1):
            # Remove parentheses, "👤:", and newline characters from each job entry
            cleaned_job = [item.strip("()👤:").replace("\n", "") for item in job]
          
            # Format cleaned job for display    
            formatted_job = f"{', '.join(cleaned_job)}"
            print(cleaned_job)
            
          
            # Add the formatted job to the message text
            message_text += f"{idx}. Customer: {cleaned_job[1]}\n{'-'*50}\n\nDriver Name: {cleaned_job[2]}\n{'-'*50}\n\nPU date: {cleaned_job[3]}\n{'-'*50}\n"

            # Create an inline keyboard button for each job
            button_text = str(idx)
            keyboard_button = types.InlineKeyboardButton(button_text, callback_data=f"job_{cleaned_job[0]}")
            keyboard_buttons.append(keyboard_button)
        
        # Create an inline keyboard with the buttons
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        back = types.InlineKeyboardButton("Back", callback_data=f"back_to_driver_cop_{driver_name}")
        keyboard.add(*keyboard_buttons, back)
        
        # Sending the concatenated message along with the inline keyboard
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,text=message_text, reply_markup=keyboard)
    else:
        # If there are no jobs for the specified driver, display a message indicating so
        message_text = f"No jobs found for {driver_name}"
        await bot.send_message(callback.from_user.id, message_text)



@dp.callback_query_handler(lambda query: query.data.startswith("back_to_driver_cop"))
async def back_tomenu(callback: types.CallbackQuery):
    global status
    driver_name = callback.data.split("_")[4]
    
    
    keybard = InlineKeyboardMarkup(row_width=5)

    back = InlineKeyboardButton(text="Back", callback_data='back')
    keybard.add(back)
    info_driver_status = db.get_status_payment(driver_name)
 
    status = info_driver_status[0][2]
    data = db.count_work_by_name(driver_name, status)
    print(status)
    if status == "Finished":
        
        
        for info in data:
            print(info)
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "WAIT":
        
        for info in data:

            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            print(info)
            
            template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}\n\nThere is unpaid work"
        unpaid_keyboard = types.InlineKeyboardButton(text="PAID", callback_data=f"paid_{info_driver_status[0][0]}")
        keybard.add(unpaid_keyboard, work_button)        
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "Rejected":
        for info in data:
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
    elif status == "Cancled":
        for info in data:
            work_button = InlineKeyboardButton(text="View Jobs", callback_data=f"work_user_{driver_name}")
            keybard.add(work_button)
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
                
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)
        
                
    elif status == "In Progress":
        for info in data:
            if info[3]:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nCurrent order from: {info[3]}"
            else:
                template = f"Driver name: {info[2]}\n\nThe total number of jobs done: {info[0]}\n\nThere is no current order"
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keybard)




@dp.callback_query_handler(lambda query: query.data.startswith("job_"))
async def back_to_mmmm(callback: types.CallbackQuery):
    job_id = callback.data.split("_")[1]

    test, gross = db.catch_job_by_jobid(job_id)
    keyboard = InlineKeyboardMarkup(row_width=5)
    print(test)
    template = ""
    for i in test:
        print(i)
        print(gross[0][0])

        # for index, item in enumerate(i):
        #     print(f"Index {index}: {type(item)}")
        #     # Optionally, you can perform further actions based on the type of the item

        template += ("Customer: " + i[0].replace('\n', '').replace('👤', '') + "\n\n" + '-' * 40 + "\n\n" + \
             "Unit: " + str(i[2]) + "\n" + '-' * 40 + "\n\n" + "Status: " + i[5] + "\n" + '-' * 40 + "\n\n" +
             "Lane: " + i[3] + "\n" + '-' * 40 + "\n\n" + "PU: " + i[6].replace('      ', '') + "\n" + '-' * 40 + "\n\n" + "Gross: " + gross[0][0] + "\n" + '-' * 40 + "\n\n" + "Miles: " + i[7]) 

    back_button = InlineKeyboardButton(text="Back", callback_data=f"bback_to_Agin_{test[0][1]}")
      # Printing just for testing
    keyboard.add(back_button)
    await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=template, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("bback_to_Agin_"))
async def back_too(callback: types.CallbackQuery):
    driver_name = callback.data.split("_")[3]  # Extracting the driver name from the callback data

    # Fetching the list of jobs for the specified driver name
    jobs_list, gross = db.get_jobs_by_driver(driver_name)

    if jobs_list:
        # Initialize the message text to an empty string
        message_text = ""
        print(gross)
        # Initialize a list to store inline keyboard buttons
        keyboard_buttons = []

        # Iterate over the jobs list to create buttons and concatenate job information
        for idx, job, in enumerate(jobs_list, start=1):
            # Remove parentheses, "👤:", and newline characters from each job entry
            cleaned_job = [item.strip("()👤:").replace("\n", "") for item in job]
          
            # Format cleaned job for display    
            formatted_job = f"{', '.join(cleaned_job)}"
            print(cleaned_job)
            
          
            # Add the formatted job to the message text
            message_text += f"{idx}. Customer: {cleaned_job[1]}\n{'-'*50}\n\nDriver Name: {cleaned_job[2]}\n{'-'*50}\n\nPU date: {cleaned_job[3]}\n{'-'*50}\n"

            # Create an inline keyboard button for each job
            button_text = str(idx)
            keyboard_button = types.InlineKeyboardButton(button_text, callback_data=f"job_{cleaned_job[0]}")
            keyboard_buttons.append(keyboard_button)
        
        # Create an inline keyboard with the buttons
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        back = types.InlineKeyboardButton("Back", callback_data=f"back_to_driver_cop_{driver_name}")
        keyboard.add(*keyboard_buttons, back)
        
        # Sending the concatenated message along with the inline keyboard
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id,text=message_text, reply_markup=keyboard)
    else:
        # If there are no jobs for the specified driver, display a message indicating so
        message_text = f"No jobs found for {driver_name}"
        await bot.send_message(callback.from_user.id, message_text)


other_things = {}


@dp.message_handler(commands=['other'])
async def other(message: types.Message):
        money = message.text.split(" ")[1]
        note = message.text.split(" ")[2]

        other_things['money'] = money
        other_things['note'] = note

        driver_names = db.catch_a_drivers()
        keyboard = types.InlineKeyboardMarkup(row_width=5)
        for driver in driver_names:
    
            button = types.InlineKeyboardButton(text=driver[0], callback_data=f"Other_{driver[0]}")
            keyboard.add(button)
        await message.answer("Please select driver", reply_markup=keyboard)
        
@dp.callback_query_handler(lambda query: query.data.startswith("Other_"))
async def do_other_change(callback: types.CallbackQuery):
        id = callback.data.split("_")[1]

        
        keyboard = InlineKeyboardMarkup()

        test = db.get_jobs_by_driver(id)
        n = 0
        text = ""
        for i in test:
            text = f"{n + 1}. Customer: {i[0]}\n\nDriver Name: {i[1]}\n\nPU: {i[2]}"
            
            button = InlineKeyboardButton(text=f"{i[0]}", callback_data=f"otherss_{i[3]}")  # Changed "oter_" to "Other_"
            keyboard.add(button)
            
        back = InlineKeyboardButton(text="Back", callback_data="baks_tt")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda query: query.data.startswith("otherss_"))
async def jbsdxfb(callback: types.CallbackQuery):
    job_id = callback.data.split("_")[1]

    money = other_things['money']
    note = other_things['note']

    if note:
        db.update_other_for_note_and_money(job_id, money, note)
    else:
        db.update_other_for_money(job_id, money)

    await callback.message.answer("Succes!")


        


@dp.callback_query_handler(lambda query: query.data == "back_to_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
      
    all_drivers, total_count = db.catch_all_drivers()
    
    # Create an inline keyboard with buttons for each driver
    keyboard = types.InlineKeyboardMarkup(row_width=3)  # Adjust the row_width value as needed
    n = 0
    for driver_name in all_drivers:
        print(type(driver_name[0]))
        keyboard.add(types.InlineKeyboardButton(text=f"{driver_name[0]}", callback_data=f"driver_{driver_name[0]}"))
        n += 1  # Increase n for the next iteration

    # Send the message with all driver names and the total count along with the inline keyboard
    await bot.edit_message_text(chat_id=callback.from_user.id, message_id=callback.message.message_id, text =f"Total number of drivers: {total_count}", reply_markup=keyboard)




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
    
    # Define column widths and row heights in centimeters
    column_widths_cm = [50] * len(df.columns)
    column_widths = [width / 2.54 for width in column_widths_cm]  # Convert cm to inches
    row_height_cm = 50
    row_height = row_height_cm / 2.54  # Convert cm to inches
    
    # Define the dark fire color
    fire_color = '#FF5733'
    
    # Export DataFrame to Excel with customized column widths and row heights
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        workbook = writer.book
        worksheet = writer.sheets['Sheet1']
        
        # Apply the dark fire color to all column headers and enlarge font size slightly
        header_format = workbook.add_format({'bg_color': fire_color, 'font_size': 15})
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # Set column widths and row heights
        for i, width in enumerate(column_widths):
            worksheet.set_column(i, i, width)
        worksheet.set_default_row(height=row_height)
    
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
        keyboard.add(types.InlineKeyboardButton(text=str(f"{driver_name[0]}"), callback_data=f"driver_{driver_name[0]}"))
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
    unpiad_button = types.KeyboardButton("Unpaid Works")
    back_to_main = types.KeyboardButton("Back to Main")
    keyboard_markup.add(finished_button, in_progress_button, rejected_button, canceled_button, unpiad_button, back_to_main)
    await message.answer("Please select an option:", reply_markup=keyboard_markup)


@dp.message_handler(lambda message: message.text == "Back to Main")
async def back_to_main(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
    keyboard.add(*buttons_for_super_admin)            
    await message.answer("You are in Main", reply_markup=keyboard)





@dp.message_handler(lambda message: message.text == "Unpaid Works")
async def unpaid_works(message: types.Message):
    # Get data for unpaid works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()
  
    

    # Create a list to store the unpaid works
    Unpaid_Works = []
    if catch_unpaid:
        
        catch_unpaid = count_unpaid[:10]
        # Add each unpaid work to the Unpaid_Works list
        for idx, row in enumerate(catch_unpaid, start=1):
            Unpaid_Works.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for unpaid works
        unpaid_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(catch_unpaid[:10], start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"unpaid_{row[0]}")
            unpaid_keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 unpaid works
        if len(catch_unpaid) > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_unpaid")
            unpaid_keyboard_markup.add(next_page_button)

        # Send the list of unpaid works with inline keyboard
        await message.answer("Unpaid Works:", reply_markup=unpaid_keyboard_markup)
    else:
        await message.answer("No unpaid works at the moment.")



@dp.message_handler(lambda message: message.text == "Finished works")
async def finished_works(message: types.Message):
    # Get data for finished works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()

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
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()

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
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()
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



@dp.callback_query_handler(lambda query: query.data.startswith("unpaid_"))
async def unpaid_callback(query: types.CallbackQuery):
    # Extract the jobID from the callback data
    job_id = query.data.split("_")[1]

    # Fetch the details of the unpaid work using the jobID
    unpaid_work_details = db.get_work_details_by_id(job_id)
    payment_statuses = db.get_payment_statuses(job_id)
    print(payment_statuses)
    if unpaid_work_details is None:
        await query.message.answer("Work details not found.")
        return


    for statuses in payment_statuses:
        if statuses[0] == "WAIT" and statuses[1] == "WAIT" and statuses[2] == "WAIT":
            if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
                 db.update_status(job_id)


            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            finish = InlineKeyboardButton(text="Driver Payment Paid", callback_data=f"for_diriver_payment_{job_id}")
            reject = InlineKeyboardButton(text="AMZ Payment Paid", callback_data=f"for_amz_{job_id}")
            cancle = InlineKeyboardButton(text="Factoring Payment Paid", callback_data=f"for_factoring_{job_id}")
            
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(finish, reject, cancle, back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)

        if statuses[0] == "PAID" and statuses[1] == "WAIT" and statuses[2] == "WAIT":
            if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
                 db.update_status(job_id)


            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            finish = InlineKeyboardButton(text="Driver Payment Paid", callback_data=f"for_diriver_payment_{job_id}")
         
            cancle = InlineKeyboardButton(text="Factoring Payment Paid", callback_data=f"for_factoring_{job_id}")
            
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(finish, cancle, back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)
        if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "WAIT":
            if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
                 db.update_status(job_id)


            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            finish = InlineKeyboardButton(text="Driver Payment Paid", callback_data=f"for_diriver_payment_{job_id}")
           
            
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(finish,  back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)

        if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
           

            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            db.update_status(job_id)
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)

        if statuses[0] == "WAIT" and statuses[1] == "PAID" and statuses[2] == "WAIT":
            if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
                 db.update_status(job_id)

            
            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            finish = InlineKeyboardButton(text="Driver Payment Paid", callback_data=f"for_diriver_payment_{job_id}")
            reject = InlineKeyboardButton(text="AMZ Payment Paid", callback_data=f"for_amz_{job_id}")
            
            
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(finish, reject, back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)

        if statuses[0] == "PAID" and statuses[1] == "WAIT" and statuses[2] == "PAID":
            if statuses[0] == "PAID" and statuses[1] == "PAID" and statuses[2] == "PAID":
                 db.update_status(job_id)

            # Prepare the message text
            message_text = f"Customer: {unpaid_work_details['customer']}\n\n{'-'*50}\n\nDriver Name: {unpaid_work_details['driver_name']}\n\n{'-'*50}\n\nLane: {unpaid_work_details['lane']}\n\n{'-'*50}\n\nPU: {unpaid_work_details['pu']}\n\n{'-'*50}\n\nRate: {unpaid_work_details['rate']}"
            keyboard = InlineKeyboardMarkup(row_width=2)
        
            
            cancle = InlineKeyboardButton(text="Factoring Payment Paid", callback_data=f"for_factoring_{job_id}")
            
            # Create inline keyboard markup with "Back" button
            back_button = types.InlineKeyboardButton("Back", callback_data="back_to_unpaid")
            keyboard.add(cancle, back_button)

            # Send the message with the details of the unpaid work and the "Back" button
            await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=message_text, reply_markup=keyboard)


         
@dp.callback_query_handler(lambda query: query.data.startswith("for_diriver_payment_"))
async def for_driver_u_p(query: types.CallbackQuery):
    job_id = query.data.split("_")[3]

    db.update_payment_d(job_id)

    await query.answer("Status Changed")


@dp.callback_query_handler(lambda query: query.data.startswith("for_amz_"))
async def for_driver_a_p(query: types.CallbackQuery):

    job_id = query.data.split("_")[2]

    db.update_payment_a(job_id)
    await query.answer("Status Changed")

@dp.callback_query_handler(lambda query: query.data.startswith("for_factoring_"))
async def for_driver_f_p(query: types.CallbackQuery):

    job_id = query.data.split("_")[2]

    db.update_payment_f(job_id)
    await query.answer("Status Changed")



@dp.callback_query_handler(lambda query: query.data == "back_to_unpaid")
async def back_ajn(query: types.CallbackQuery):
    # Get data for unpaid works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()
  
    

    # Create a list to store the unpaid works
    Unpaid_Works = []
    if catch_unpaid:
        
        catch_unpaid = count_unpaid[:10]
        # Add each unpaid work to the Unpaid_Works list
        for idx, row in enumerate(catch_unpaid, start=1):
            Unpaid_Works.append(f"{idx}. Customer: {row[1]}\nDriver Name: {row[2]}\nLane: {row[4]}\nRate: {row[5]}")

        # Create inline keyboard markup with buttons labeled 1 to 10 for unpaid works
        unpaid_keyboard_markup = types.InlineKeyboardMarkup(row_width=5)
        for idx, row in enumerate(catch_unpaid[:10], start=1):
            button = types.InlineKeyboardButton(str(idx), callback_data=f"unpaid_{row[0]}")
            unpaid_keyboard_markup.add(button)

        # Add "Next Page" button if there are more than 10 unpaid works
        if len(catch_unpaid) > 10:
            next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_unpaid")
            unpaid_keyboard_markup.add(next_page_button)

        # Send the list of unpaid works with inline keyboard
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Unpaid Works:", reply_markup=unpaid_keyboard_markup)
    else:
        await query.message.answer("No unpaid works at the moment.")




@dp.callback_query_handler(lambda query: query.data == "back_to_rejected")
async def back_to_rejected_callback(query: types.CallbackQuery):
    # Get data for rejected works
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()
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
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()
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
 
    job_data, gross = db.catch_job_by_jobid(id)
    print(job_data)
    keyboard = InlineKeyboardMarkup(row_width=5)
    back = InlineKeyboardButton("Back", callback_data="Back_finshed")
    keyboard.add(back)
    for data in job_data:
        print(data)
        template = f"Customer: {data[0]}\n\n{'-' * 50}\n\nDriver Name: {data[1]}\n\n{'-' * 50}\n\nLane: {data[3]}\n\n{'-' * 50}\n\nRate: {data[4]}"

        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)

info = {}

@dp.callback_query_handler(lambda query: query.data.startswith("progress_"))
async def progress_id(query: types.CallbackQuery):
    print(query)
    id = query.data.split("_")[1]
    info.clear()
    info["ID"] = id
    job_data, gross = db.catch_job_by_jobid(id)
    keyboard = InlineKeyboardMarkup(row_width=3)
    back = InlineKeyboardButton("Back", callback_data="Back_progress")
    finish = InlineKeyboardButton(text="Finished", callback_data="Finish")
    reject = InlineKeyboardButton(text="Reject", callback_data=f"reject_{id}")
    cancle = InlineKeyboardButton(text="Cancelled", callback_data=f"cancelled_{id}")
    keyboard.add(finish, reject, cancle, back)
    for data in job_data:
        template = f"Customer: {data[0]}\n\n{'-' * 50}\n\nDriver Name: {data[1]}\n\n{'-' * 50}\n\nLane: {data[3]}\n\n{'-' * 50}\n\nRate: {data[4]}\n\n{'-'*50}\n\nPU: {data[6]}"

        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("reject"))
async def reject(query: types.CallbackQuery):
    job_id = query.data.split("_")[1]
 
 
    await query.message.answer("The work is rejected")

    db.reject(job_id)



@dp.message_handler(lambda message: message.text == "Load ID's")
async def load_idx(message: types.Message):
    keyboard = InlineKeyboardMarkup()

    unit = db.get_load_idx()

    for i in unit:
        print(i)
        id_button = InlineKeyboardButton(text=i[0], callback_data=f"unit_{i[0]}")
        keyboard.add(id_button)
    back = InlineKeyboardButton("Back", callback_data=f"back_to_main_to_{unit[0][0]}")    
    keyboard.add(back)
    await message.answer("Please select ID: ", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("unit_"))
async def back_toto(query: types.CallbackQuery):
    unit = query.data.split("_")[1]
    keyboard = InlineKeyboardMarkup()

    texts = ["Change", "Delete", "View Jobs","Back to Main"]
    for text in texts:
        print(text)
        button = InlineKeyboardButton(text=text, callback_data=f"{text.lower()}_{unit}_action_")
        keyboard.add(button)

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please select an option", reply_markup=keyboard)

new = {}

@dp.callback_query_handler(lambda query: query.data.endswith("_action_"))
async def handle_action(query: types.CallbackQuery, state: FSMContext):
    action, unit = query.data.split("_")[0], query.data.split("_")[1]
    print(action)
    new["unit"] = unit

    if action == "change":
        await query.answer("Please enter New id for change: " + unit)
        await state.set_state(States.change)
    elif action == "delete":
        
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
        keyboard.add(*buttons_for_super_admin)  

        await query.message.answer("Ok Deleted!", reply_markup=keyboard)


        db.delete_element(unit)
        await state.finish()
    elif action == "back to main":
        # await query.answer("Going back to main for unit " + unit)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
        keyboard.add(*buttons_for_super_admin)            
        await query.message.answer("You are in Main", reply_markup=keyboard)

    elif action == "view jobs":
        global buttonhhssa
        test, gross = db.catch_job_by_id(unit)
        keyboard = InlineKeyboardMarkup()
        n = 0
        print(test)
        for i in test:
            print(gross)
            buttonhhssa = InlineKeyboardButton(text=f"{n + 1}", callback_data=f"view_job_{i[0]}")
        
            text = f"Driver Name: {i[2]}\n{'-'*40}\n\nCustomer: {i[1]}\n{'-'*40}\n\nLane: {i[3]}\n"
        keyboard.add(buttonhhssa)
        back = InlineKeyboardButton(text="Back", callback_data=f"Backkkk_{unit}")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text =text, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith("view_job_"))
async def view_s(query: types.CallbackQuery, state: FSMContext):
    idx = query.data.split("_")[2]

    # Fetch data from the database
    try:
        catch, gross = db.catch_job_by_jobid(idx)
        if not catch or not gross:
            await query.answer("No data found for this job.", show_alert=True)
            return
    except Exception as e:
        await query.answer(f"Error fetching data.{e}", show_alert=True)
        return

    for i in catch:
        template = (
            f"Driver Name: {i[2]}\n{'-'*40}\n\n"
            f"Customer: {i[1]}\n{'-'*40}\n\n"
            f"Lane: {i[4]}\n{'-'*40}\n\n"
            f"PU: {i[7]}\n{'-'*40}\n\n"
            f"Gross: {gross[0][0]}\n{'-'*40}\n\n"
            f"Miles: {i[8]}\n{'-'*40}\n\n"
        )
        keyboard = InlineKeyboardMarkup()
        back = InlineKeyboardButton(text="Back", callback_data=f"backBack_{i[0]}")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=template, reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith("Backkkk"))
async def back_intosd(query: types.CallbackQuery, state: FSMContext):
    unit = query.data.split("_")[1]
    keyboard = InlineKeyboardMarkup()

    texts = ["Change", "Delete", "Back to Main", "View Jobs"]
    for text in texts:
        print(text)
        button = InlineKeyboardButton(text=text, callback_data=f"{text.lower()}_{unit}_action_")
        keyboard.add(button)

    await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Please select an option", reply_markup=keyboard)

@dp.callback_query_handler(lambda query: query.data.startswith("backBack_"))
async def asdgsd(query: types.CallbackQuery):
        id = query.data.split("_")[1]
        test, gross = db.catch_job_by_jobid(id)
        keyboard = InlineKeyboardMarkup()
        n = 0
        print(test)
        for i in test:
            print(gross)
            button = InlineKeyboardButton(text=f"{n + 1}", callback_data=f"view_job_{i[0]}")
        
            text = f"Driver Name: {i[2]}\n{'-'*40}\n\nCustomer: {i[1]}\n{'-'*40}\n\nLane: {i[3]}\n{'-'*40}\n"
        keyboard.add(button)
        back = InlineKeyboardButton(text="Back", callback_data=f"Backkkk_{i[6]}")
        keyboard.add(back)
        await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text =text, reply_markup=keyboard)

@dp.message_handler(state=States.change)
async def change(message: types.Message, state: FSMContext):
    unit = message.text
    old_Unit = new["unit"]
    db.change_id(unit, old_Unit)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
    await message.answer("Ok Changed!", reply_markup=keyboard)
    await state.finish()





@dp.callback_query_handler(lambda query: query.data.startswith("Back_"))
async def back(query: types.CallbackQuery):
    # Extract the action from the callback data
    action = query.data.split("_")[1]
    print(action)
    # Retrieve the necessary data
    all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count, count_unpaid, catch_unpaid = db.catch_works()

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
                print(row)
                await bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=f"Page 1\n\nFinished Works:", reply_markup=finished_keyboard_markup)

            # Add "Next Page" button if there are more than 10 finished works
            if finished_count > 10:
                next_page_button = types.InlineKeyboardButton("Next Page", callback_data="next_page_finished")
                finished_keyboard_markup.add(next_page_button)

            # Send the list of finished works with inline keyboard
            
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
        await state.set_state(States.Factoring)

    if message.text == "No Wait":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Yes", "No Wait"]
        info['paid'] = "WAIT"
        keyboard.add(*buttons)
        await message.answer("Has the AMZ payment been paid?", reply_markup=keyboard)
        await state.set_state(States.Factoring)



@dp.message_handler(state=States.Factoring)
async def factoring(message: types.Message, state: FSMContext):
    if message.text == "Yes":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Yes", "No Wait"]
        info['amz'] = "PAID"
        keyboard.add(*buttons)
        await message.answer("Has the Factoring payment been paid?", reply_markup=keyboard)
        await state.set_state(States.note)

    if message.text == "No Wait":
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Yes", "No Wait"]
        info['amz'] = "WAIT"
        keyboard.add(*buttons)
        await message.answer("Has the AMZ Factoring been paid?", reply_markup=keyboard)
        await state.set_state(States.note)


@dp.message_handler(state=States.note)
async def note(message: types.Message, state: FSMContext):
    if message.text == "Yes":
        info['factoring'] = "PAID"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text="Skip")
        keyboard.add(button)
        await message.answer("Please enter Note", reply_markup=keyboard)
        await state.set_state(States.no_note)
    if message.text == "No Wait":
        info['factoring'] = "WAIT"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button = types.KeyboardButton(text="Skip")
        keyboard.add(button)
        await message.answer("Please enter Note", reply_markup=keyboard)
        await state.set_state(States.no_note)





@dp.message_handler(state=States.no_note)
async def update_data(message: types.Message, state: FSMContext):
    job_id = info["ID"]
    payment_status = info["paid"]
    amz_status = info["amz"]
    note = message.text
    factoring = info["factoring"]

    if note == "Skip":
        if payment_status == "WAIT" or amz_status == "WAIT" or factoring == "WAIT":
            db.update_monthly_without_note_if_wait(payment_status, amz_status, job_id, factoring)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
            keyboard.add(*buttons_for_super_admin)
            await message.answer("Job is finished", reply_markup=keyboard)
        else:
            db.update_monthly_without_note(payment_status, amz_status, job_id, factoring)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
            keyboard.add(*buttons_for_super_admin)
            await message.answer("Job is finished", reply_markup=keyboard)

        await state.finish()

    else:
        if payment_status == "WAIT" or amz_status == "WAIT" or factoring == "WAIT":
            db.update_monthly_if_wiant(payment_status, amz_status, job_id, factoring)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
            keyboard.add(*buttons_for_super_admin)
            await message.answer("Job is finished", reply_markup=keyboard)
        
        else:
            db.update_monthly(payment_status, amz_status, note, job_id, factoring)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons_for_super_admin = ['Drivers', 'Works', 'Managers', 'Add new manager', "Weekly Data", 'Remove manager', "Monthly Board", "Load ID's", "Change Data"]
            keyboard.add(*buttons_for_super_admin)
            await message.answer("Job is finished", reply_markup=keyboard)
        await state.finish()




@dp.message_handler(lambda message: message.text == "Managers")
async def managers(message: types.Message):
    print('manager')
    adminNames = db.catch_managers()
    
    for names in adminNames:



        template = f"Name: {names[0]}\n{'-'*45}\nLast entry: {names[1]}"

        await message.answer(template)



@dp.message_handler(lambda message: message.text == "Weekly Data")
async def exel_all(message: types.Message):
    
    await message.answer("Wait a minute data's are collecting....")
    time.sleep(10)
    process_data()

    await send_weekly("Weekly_Data.xlsx")
    

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
    


@dp.message_handler(commands=['escrow'])
async def escrow(message: types.Message):
    money = message.text.split(" ")[1]
    new['escrow'] = money
    await message.delete()
    driver_names = db.catch_a_drivers()
    keyboard = types.InlineKeyboardMarkup(row_width=5)
    for driver in driver_names:
   
        button = types.InlineKeyboardButton(text=driver[0], callback_data=f"escrow_{driver[0]}")
        keyboard.add(button)
    await message.answer("Please select driver", reply_markup=keyboard)
    data_l_d['money'] = message.text.split(" ")[1]



@dp.callback_query_handler(lambda query: query.data.startswith("escrow_"))
async def lay(query: types.CallbackQuery):
    driver_name = query.data.split("_")[1]

    await query.message.answer("Ok layover added")

    db.update_escrow(driver_name, new["escrow"])



@dp.callback_query_handler(lambda query: query.data.startswith("remove_"))
async def call(query: types.CallbackQuery):
    admin_name = query.data.split("_")[1]
    db.remove_manager(admin_name)

    await query.message.answer("Succesfuly removed")

def flatten_list(nested_list):
    flat_list = []
    for sublist in nested_list:
        if isinstance(sublist, list):
            for item in sublist:
                flat_list.append(item)
        else:
            flat_list.append(sublist)
    return flat_list



async def send_weekly(excel_file):
    admin_id = db.admin_check()
   
    for chat_id in admin_id:
    
        if chat_id:
            # Check if `excel_file` is a valid file path
            if os.path.exists(excel_file):
                with open(excel_file, 'rb') as f:
                    await bot.send_document(chat_id=chat_id[0], document=f)
            else:
                print("Invalid file path:", excel_file)
        else:
            print("Invalid chat ID:", chat_id)


    
import time
import asyncio



def aggregate_data(data):
    aggregated_data = {}
    for item in data:
        driver_name, additional_info = item
        if driver_name in aggregated_data:
            existing_info = aggregated_data[driver_name]
            for i in range(len(additional_info)):
                if additional_info[i] is not None:
                    existing_info[i] += additional_info[i]
            aggregated_data[driver_name] = existing_info
        else:
            aggregated_data[driver_name] = additional_info
    return aggregated_data

# Function to sum up the additional information for each driver
def sum_info(additional_info):
    summed_info = [0] * len(additional_info[0])
    for info in additional_info:
        for i, val in enumerate(info):
            if val is not None:
                summed_info[i] += int(val)
    summed_info[0] //= 2  # This line remains as is
    return summed_info

# Async function to process data
def process_data():
    result = db.check_day_column()
    print(result)
    if result:
        result_ = db.fetch_data_for_driver()
        print(result_)
        aggregated_data = aggregate_data(result_)
        print(aggregated_data)
        for driver_name, additional_info in aggregated_data.items():
            summed_info = sum_info(additional_info)
            print(summed_info)
            
            escrow = summed_info[8]
            p_m = summed_info[1] / summed_info[3]
            factoring_fee = 0.1 * summed_info[1]
            dispach_fee = 0.3 * summed_info[1]
            odom = summed_info[3] * 0.1
            driver_profit = summed_info[3] * summed_info[7] - escrow
            company_profit = summed_info[1] - summed_info[2] - summed_info[6] - factoring_fee - dispach_fee - 25 - 25 - 7 - summed_info[0] - 35 - 25 - 0.1 - summed_info[9] - driver_profit
            print(company_profit)
     
            unit = db.take_unit(result_[0][0])
      
            
            for i in unit:
                db.insert_data_to_exel(
                    driver_name, i, "", p_m, summed_info[1], summed_info[3], summed_info[3], "", "", 
                    summed_info[6], summed_info[4], summed_info[5], factoring_fee, dispach_fee, 
                    "25.00$", "25.00$", "7.00$", summed_info[0], "35.00$", "25.00$", "35.00$", 
                    "100.00$", "", "0.1", odom, "", "", escrow, company_profit, driver_profit
                )

        export_table_to_excel("database.db", "for_exel", "Weekly_Data.xlsx")





# Entry point of the script
if __name__ == '__main__':
    


        executor.start_polling(dp, skip_updates=True)
  
   