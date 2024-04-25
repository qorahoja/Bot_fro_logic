import sqlite3

def create_database(db_name):
    # Connect to SQLite database (will create it if not exists)
    conn = sqlite3.connect(db_name)
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()
    
    # Create a table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      user_id INTEGER PRIMARY KEY,
                      username TEXT,   
                      truck_number TEXT,
                      phone_number TEXT,
                      status_driver TEXT)''')


    cursor.execute('''CREATE TABLE IF NOT EXISTS "all" (
                   driver TEXT,
                   unit INTEGER,
                   days_worked INTEGER,
                   P_M TEXT,
                   Gross TEXT,
                   all_mile INTEGER,
                   loaded INTEGER,
                   Empty INTEGER,
                   Fuel TEXT,
                   Tolls TEXT,
                   Layover TEXT, 
                   Detention TEXT,
                   Factoring_fee TEXT,
                   Dispatch_Fee TEXT,
                   accounting TEXT,
                   safety TEXT,
                   Mobile_expenses TEXT,
                   Truck_payment TEXT,
                   Ifta_permits TEXT,
                   Eld_for_company TEXT,
                   Truck_payment_per_mile TEXT,
                   Odom INTEGER,
                   PD_ins TEXT,
                   Rate TEXT,
                   EScrow TEXT,
                   Company_Profit TEXT,
                   Driver_PROFIT TEXT
                )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin(
                   admin_id INTEGER PRIMARY KEY,
                   keys TEXT,
                   admin_status TEXT
    )''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Name of the database file
    database_name = "database.db"
    # Create the database
    create_database(database_name)
    print(f"Database '{database_name}' created successfully.")
