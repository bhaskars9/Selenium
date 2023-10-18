import sqlite3
import os



######### TO DO ####
# Add logging instead of printing

class DatabaseManager:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
            print("Connected to the database.")
        except sqlite3.Error as e:
            print("Error connecting to the database:", e)

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS Jobs
                  (id INTEGER PRIMARY KEY,
                  jk VARCHAR(40),
                  location TEXT,
                  role TEXT,
                  date DATETIME DEFAULT CURRENT_TIMESTAMP)'''
        try:
            self.conn.execute(query)
            self.conn.commit()
            # print("Table 'Jobs' created successfully.")
        except sqlite3.Error as e:
            print("Error creating table:", e)

    def insert_record(self, Job):
        query = '''INSERT INTO Jobs (jk, role, location) VALUES (?, ?, ?)'''
        try:
            self.conn.execute(query, (Job.jk, Job.role, Job.location))
            self.conn.commit()
            print("Record inserted successfully.")
        except sqlite3.Error as e:
            print("Error inserting record:", e)
    
    def job_exists(self, jk):
        res = self.conn.execute('SELECT * FROM Jobs WHERE jk = ?', (jk,))
        job = res.fetchone()
        return job is not None
    
    def retrieve_records(self):
        query = '''SELECT * FROM Jobs'''
        try:
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                print("ID:", row[0])
                print("Job link: "+row[1])
                print("Location:", row[2])
                print("Role:", row[3])
                print("Date:", row[4])
                print("------------")
        except sqlite3.Error as e:
            print("Error retrieving records:", e)

    def add_column(self, new_col, dtype='VARCHAR(50)', def_val = ''):
        query = f"ALTER TABLE Jobs ADD {new_col} {dtype} DEFAULT {def_val}"
        try:
            self.conn.execute(query)
            self.conn.commit()
            print("Column added successfully.")
        except sqlite3.Error as e:
            print("Error Adding column:", e)


    def custom_query(self, query):
        """No output is returned"""
        try:
            self.conn.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            print("Error Processing query:", e)
    
    def custom_retrive(self, query):
        try:
            cursor = self.conn.execute(query)
            rows = cursor.fetchall()
            return (list(map(lambda x: x[0], cursor.description)), rows)
        except sqlite3.Error as e:
            print("Error Processing query:", e)

    def close_connection(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")
    
    def delete_database(self):
        self.close_connection()  # Close the connection before deleting the file
        os.remove(self.db_name)
        print("Database deleted successfully.")


class Job:
    def __init__(self, jk, location, role):
        self.jk = jk
        self.location = location
        self.role = role



