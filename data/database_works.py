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
        
        # Execute query for Rejected status
        self.cursor.execute("SELECT jobID, customer, driver_name, unit, lane, rate FROM jobs WHERE status = 'Rejected'")
        catch_rejected = self.cursor.fetchall()
        
        # Get the row count for Rejected status
        rejected_count = len(catch_rejected)
        
        # Execute query for Canceled status
        self.cursor.execute("SELECT jobID, customer, driver_name, unit, lane, rate FROM jobs WHERE status = 'Cancelled'")
        catch_canceled = self.cursor.fetchall()
        
        # Get the row count for Canceled status
        canceled_count = len(catch_canceled)
        
        return all_rows, total_count, catch_finished, finished_count, catch_in_progress, in_progress_count, catch_rejected, rejected_count, catch_canceled, canceled_count

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



    def count_work_by_name(self, driver_name):
        self.cursor.execute("SELECT COUNT(driver_name), driver_name, customer FROM jobs WHERE driver_name = ? AND status = ?", (driver_name, "In Progress"))
        result = self.cursor.fetchall() # Fetch the count value from the first row of the result
        return result
    

    def get_status_payment(self, driver_name):
        self.cursor.execute('SELECT jobID, STATUS, "PAYMENT STATUS" FROM mothly WHERE "DRIVER NAME" = ?', (driver_name,))
        result = self.cursor.fetchall()
        return result

    def insert_all_to_monthly(self, jobID, Customer, LOAD_ID, DRIVER_NAME, LANE, PU_DATE, STATUS, RATE, DH, MILES, BOOKED_BY):
        self.cursor.execute("INSERT INTO mothly (jobID, Customer,'LOAD ID', 'DRIVER NAME', LANE, 'PU DATE', STATUS, RATE, DH, MILES, 'BOOKED BY') VALUES (?,?,?,?,?,?,?,?,?,?,?)", (jobID, Customer, LOAD_ID, DRIVER_NAME, LANE, PU_DATE,STATUS, RATE, DH, MILES, BOOKED_BY))
        self.conn.commit()

    def get_work_details_by_id(self, job_id):
        # Execute a query to fetch the details of the work by its ID
        self.cursor.execute("SELECT * FROM jobs WHERE jobID = ?", (job_id,))
        work_details = self.cursor.fetchone()

        # If work details are found, return them as a dictionary
        if work_details:
            columns = [description[0] for description in self.cursor.description]
            return dict(zip(columns, work_details))
        else:
            return None
    
    def update_monthly(self, payment_status, amz_status, note, job_id):
        self.cursor.execute("UPDATE mothly SET STATUS = 'Finished' NOTES = ?, 'AMZ PAYMENT STATUS' = ?, Factoring = ?, 'PAYMENT STATUS' = ? WHERE jobID = ?", (note, amz_status, "PAID", payment_status, job_id,))
        self.conn.commit()

        self.cursor.execute("UPDATE jobs SET STATUS = 'Finished' WHERE jobID = ?", (job_id))
        self.conn.commit()

    def update_monthly_without_note(self, payment_status, amz_status, job_id):
        self.cursor.execute("UPDATE mothly SET STATUS = 'Finished', 'AMZ PAYMENT STATUS' = ?, Factoring = ?, 'PAYMENT STATUS' = ? WHERE jobID = ?", (amz_status, "PAID", payment_status, job_id))
        self.conn.commit()
        
        self.cursor.execute("UPDATE jobs SET STATUS = 'Finished' WHERE jobID = ?", (job_id,))
        self.conn.commit()

    def update_status(self, jobID):
        self.cursor.execute('UPDATE mothly SET "PAYMENT STATUS" = "PAID" WHERE jobID = ?', (jobID,))
        self.conn.commit()

    def reject(self, jobID):

        
        self.cursor.execute('UPDATE mothly SET "PAYMENT STATUS" = "Rejected" WHERE jobID = ?', (jobID,))
        self.conn.commit()

        self.cursor.execute("UPDATE jobs SET status = 'Rejected' WHERE jobID =  ?", (jobID,))
        self.conn.commit()


    def cancel(self, jobID):

        
        # Update "PAYMENT STATUS" in the mothly table
        self.cursor.execute('UPDATE mothly SET "PAYMENT STATUS" = "Cancelled" WHERE jobID = ?', (jobID,))
        self.conn.commit()

        # Update status in the jobs table
        self.cursor.execute("UPDATE jobs SET status = 'Cancelled' WHERE jobID = ?", (jobID,))
        self.conn.commit()

    def update_payment_status_to_wait(self, job_id):
        self.cursor.execute("UPDATE jobs SET STATUS = 'Finished' WHERE jobID = ?", (job_id,))
        self.conn.commit()

        self.cursor.execute("UPDATE mothly SET 'PAYMENT STATUS' = 'WAIT' WHERE jobID = ?", (job_id,))
        self.conn.commit()