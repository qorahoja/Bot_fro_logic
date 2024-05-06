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


    cursor.execute('''CREATE TABLE IF NOT EXISTS jobs (
                jobID TEXT,
                customer TEXT,
                driver_name TEXT,
                unit INTEGER, 
                lane TEXT,
                pu TEXT,
                rate INTEGER,
                dh TEXT,
                miles TEXT,
                booked_by TEXT,
                status TEXT
                )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS mothly (
    jobID TEXT,
    Customer TEXT,
    "LOAD ID" TEXT,
    "DRIVER NAME" TEXT,
    LANE TEXT,
    "PU DATE" TEXT,
    STATUS TEXT,
    RATE TEXT,
    DH TEXT,
    MILES TEXT,
    "BOOKED BY" TEXT,
    NOTES TEXT,
    "AMZ PAYMENT STATUS" TEXT,
    Factoring TEXT,
    "PAYMENT STATUS" TEXT
)
''')
    

    cursor.execute('''CREATE TABLE IF NOT EXISTS admin(
                   admin_name TEXT,
                   admin_id INTEGER PRIMARY KEY,
                   keys TEXT,
                   admin_status TEXT,
                   last_entry TEXT
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
