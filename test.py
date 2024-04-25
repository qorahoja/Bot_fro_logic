# import fitz

# def extract_text_from_pdf(pdf_path):
#     # Open the PDF file
#     with fitz.open(pdf_path) as pdf:
#         # Get the second page
#         page = pdf[1]  # Index starts from 0, so 1 represents the second page
        
#         # Extract text from the page
#         text = page.get_text()
#         # print(text.split("\n"))
        
#         return text



# def find_next_line_after_week(text_content):
#     # Split the text by lines
#     lines = text_content.split('\n')
    
#     # Search for the line containing "Week"
#     for i, line in enumerate(lines):
#         if line == "Week":
#             # Check if the next line exists
#             if i + 1 < len(lines):
#                 return lines[i + 1]
#             else:
#                 return "Next line after 'Week' not found"
    
#     return "'Week' not found"




# import pandas as pd

# def fuel_data(file_name):
#     try:
#         # Read the Excel file
#         df = pd.read_excel(file_name)
        
#         # Filter rows where specific column contains float values
#         amt_column = df.iloc[:, 15]  # Assuming 'Unnamed: 15' is the 16th column
#         float_values = amt_column.apply(lambda x: isinstance(x, (float, int)))
#         filtered_df = df[float_values].copy()  # Create a copy to avoid the warning
        
#         # Filter out rows where 'Unnamed: 4' column contains float values
#         filtered_df = filtered_df[~filtered_df['Unnamed: 4'].apply(lambda x: isinstance(x, (float, int)))]
        
#         # Rename columns to 'Unnamed: 15' and 'Unnamed: 1'
#         filtered_df.columns = ['Unnamed: 15' if col == 'Column_15' else 'Unnamed: 1' if col == 'Column_1' else col for col in filtered_df.columns]
        
#         # Remove quotation marks using .loc[]
#         filtered_df.loc[:, 'Unnamed: 15'] = filtered_df['Unnamed: 15'].astype(str).str.replace('"', '')
        
#         # Convert 'Unnamed: 15' column to numeric using .loc[] to avoid the warning
#         filtered_df.loc[:, 'Unnamed: 15'] = pd.to_numeric(filtered_df['Unnamed: 15'], errors='coerce')
        
#         # Drop rows with NaN values in the 'Unnamed: 15' column
#         filtered_df = filtered_df.dropna(subset=['Unnamed: 15'])
        
#         # Group by 'Unnamed: 1' (Driver Name) and calculate the total fuel consumed and number of days worked
#         grouped_df = filtered_df.groupby('Unnamed: 1').agg({'Unnamed: 15': 'sum', 'Unnamed: 4': 'nunique'}).reset_index()
#         grouped_df.columns = ['Driver Name', 'Total Fuel', 'Days Worked']
        
#         # Calculate remaining fuel for drivers who worked more than 7 days
#         grouped_df['Remaining Fuel'] = grouped_df.apply(lambda row: row['Total Fuel'] - 7 * row['Days Worked'] if row['Days Worked'] > 7 else 0, axis=1)
        
#         # Print the result
#         print("Driver Name, Total Fuel, Number of Days Worked, and Remaining Fuel for Extra Days:")
#         print("-" * 30)
        
#         for index, row in grouped_df.iterrows():
#             driver_name = row['Driver Name']
#             total_fuel = row['Total Fuel']
#             days_worked = row['Days Worked']
#             remaining_fuel = row['Remaining Fuel']
#             if days_worked >= 7:
#                 print(f"{driver_name}: {remaining_fuel}$, {days_worked} days worked")
#             else:
#                 print(f"{driver_name}: {total_fuel}$, {days_worked} days worked")
                
#     except FileNotFoundError:
#         print(f"File '{file_name}' not found.")
#     except Exception as e:
#         print(f"An error occurred: {e}")

# # Call the function
# fuel_data('Invoice_RAJ_CARRIER_LLC_com,_Cube_Systems_LLC_org,_Cube_Systems.xlsx')



# if data:
#     print("Total fuel values per driver:")
#     print("{:<20} {:<10}".format("Driver Name", "Total Fuel"))
#     print("-" * 30)
#     for driver, fuel in data:
#         print("{:<20} {:<10}".format(driver, fuel))





# import pandas as pd

# def convert_xlsx_to_csv(xlsx_file_path, csv_file_path):
#     # Read the XLSX file into a pandas DataFrame
#     df = pd.read_excel(xlsx_file_path)
    
#     # Write the DataFrame to a CSV file
#     df.to_csv(csv_file_path, index=False)
    
#     print(f"XLSX file '{xlsx_file_path}' has been converted to CSV file '{csv_file_path}'.")

# # Specify the paths for the XLSX and CSV files
# xlsx_file_path = 'Invoice_RAJ_CARRIER_LLC_com,_Cube_Systems_LLC_org,_Cube_Systems.xlsx'
# csv_file_path = 'converted_output.csv'

# # Call the function to convert the XLSX to CSV
# convert_xlsx_to_csv(xlsx_file_path, csv_file_path)




import pandas as pd

def compress_csv_to_xlsx(csv_file_path, xlsx_file_path):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Write the DataFrame to an XLSX file
    df.to_excel(xlsx_file_path, index=False)
    
    print(f"CSV file '{csv_file_path}' has been compressed to XLSX file '{xlsx_file_path}'.")

# Specify the paths for the CSV and XLSX files
csv_file_path = 'data.csv'
xlsx_file_path = 'input.xlsx'

# Call the function to compress the CSV to XLSX
compress_csv_to_xlsx(csv_file_path, xlsx_file_path)
