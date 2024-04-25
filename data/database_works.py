import sqlite3

class UserDatabase:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.conn.close()

    # def user_exists(self, user_id):
    #     self.cursor.execute("SELECT COUNT(*) FROM users WHERE user_id=?", (user_id,))
    #     count = self.cursor.fetchone()[0]
    #     return count > 0



    def insert_driver(self, driver_name, truck_number):
        self.cursor.execute("INSERT INTO 'all' (driver, unit) VALUES (?, ?)", (driver_name,truck_number, ))
        self.conn.commit()
    def catch_driver(self, name):
        self.cursor.execute("SELECT driver FROM 'all' WHERE unit = ?", (name,))
        id = self.cursor.fetchall()
        return id
    def admin_check(self, admin_id):
        self.cursor.execute("SELECT admin_id FROM admin")
        result = self.cursor.fetchall()
        return result
    

                           



    # Fetch the result
        