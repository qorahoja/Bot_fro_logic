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



    def catch_driver(self, name):
        self.cursor.execute("SELECT driver_name FROM jobs WHERE unit = ?", (name,))
        id = self.cursor.fetchall()
        return id
    
    def admin_check(self):
        self.cursor.execute("SELECT admin_id FROM admin")
        result = self.cursor.fetchall()
        return result

    def catch_key(self, admin_id):
        self.cursor.execute("SELECT keys FROM admin WHERE admin_id = ?", (admin_id,))
        result = self.cursor.fetchone()
        return result
    
    def add_admin(self):
        self.cursor.execute("INSERT INTO admin (admin_id, keys, admin_status) VALUES (6869550806, '1234', 'Super')")
        self.conn.commit()

    def catch_admin_status(self, admin_id):
        self.cursor.execute("SELECT admin_status FROM admin WHERE admin_id = ?", (admin_id,))
        result = self.cursor.fetchone()
        return result
    
    def catch_all_drivers(self):
        self.cursor.execute("SELECT driver_name FROM jobs")
        result = self.cursor.fetchall()
        total_count = len(result)
        return result, total_count
    
    def insert_all(self, jobID, customer, LOAD_ID, DRIVER_NAME, LANE, PU, RATE, DH, MILES, BOOKED_BY, status):
        self.cursor.execute("INSERT INTO jobs (jobID, customer, driver_name, unit, lane, pu, rate, dh, miles, booked_by, status) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (jobID,customer, DRIVER_NAME, LOAD_ID ,LANE, PU, RATE, DH, MILES, BOOKED_BY, status))
        self.conn.commit()

    def catch_works(self):
    # Execute query for all rows
        self.cursor.execute("SELECT customer, driver_name, unit, lane, rate FROM jobs")
        all_rows = self.cursor.fetchall()
        
        # Get the row count for all rows
        total_count = len(all_rows)

        # Execute query for Finished status
        self.cursor.execute("SELECT jobID, customer, driver_name, unit, lane, rate FROM jobs WHERE status = 'Finished'")
        catch_finished = self.cursor.fetchall()
        
        # Get the row count for Finished status
        finished_count = len(catch_finished)
        
        # Execute query for In Progress status
        self.cursor.execute("SELECT jobID, customer, driver_name, unit, lane, rate FROM jobs WHERE status = 'In Progress'")
        catch_in_progress = self.cursor.fetchall()
        
        # Get the row count for In Progress status
        in_progress_count = len(catch_in_progress)
        
        return all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count

    def catch_job_by_id(self, id):
        self.cursor.execute("SELECT customer, driver_name, unit, lane, rate FROM jobs WHERE jobID = ?", (id,))
        result = self.cursor.fetchall()
        return result

    # Fetch the result
    def catch_managers(self):
        self.cursor.execute("SELECT admin_name, last_entry FROM admin WHERE admin_status = ?", ("Manager",))
        result = self.cursor.fetchall()
        return result
        
    def last_entry(self, time, admin_id):
        self.cursor.execute('UPDATE admin SET last_entry = ? WHERE  admin_id = ?', (time,admin_id))
        self.conn.commit()
    

    def add_manager(self, manager_id, key):
        self.cursor.execute("INSERT INTO admin (admin_id, keys, admin_status) VALUES (?,?, 'Manager')", (manager_id, key))
        self.conn.commit()

    def remove_manager(self, manager_name):
        self.cursor.execute("DELETE FROM admin WHERE admin_name = ?", (manager_name,))
        self.conn.commit()