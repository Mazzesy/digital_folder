import sqlite3
import json
import os
from datetime import datetime


class MyDatabase:
    def __init__(self, database_file):
        self.database_file = database_file
        self.create_database()

    @staticmethod
    def check_database_exists(db_file):
        return os.path.exists(db_file)

    def create_database(self):
        if self.check_database_exists(self.database_file):
            print("Database already exists.")
            return
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS folder (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_name TEXT,
                folder_files TEXT,
                folder_structure TEXT,
                folder_register TEXT,
                timestamp TEXT
            )
    
        '''

        cursor.execute(create_table_query)

        conn.commit()
        cursor.close()
        conn.close()

    def check_if_folder_in_database(self, folder_name):
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 3: Execute a SELECT query to check if the 'id' exists
        cursor.execute('SELECT EXISTS(SELECT 1 FROM folder WHERE folder_name = ?)', (folder_name,))
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Step 4: return the result
        if result[0] == 1:
            return True
        else:
            return False

    def save_folder_structure(self, tree_structure, folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Convert the Python dictionary to a JSON string
        tree_text = json.dumps(tree_structure[0])

        # Step 3: Update/insert the JSON data into the SQLite table
        if self.check_if_folder_in_database(folder_name):  # Update, if the folder already exists
            cursor.execute('UPDATE folder SET folder_structure = ? WHERE folder_name = ?', (tree_text, folder_name))
        else:  # Insert, if the folder does not exist
            cursor.execute('INSERT INTO folder (folder_name, folder_structure) VALUES (?, ?)',
                           (folder_name, tree_text,))
        conn.commit()

        # Close the database connection
        conn.close()

    def get_folder_structure(self, folder_name):
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 2: Execute a SELECT query to retrieve the JSON data
        cursor.execute('SELECT folder_structure FROM folder WHERE folder_name = ?', (folder_name,))

        # Fetch the JSON text
        folder_text = cursor.fetchone()[0]

        # Step 3: Parse the JSON data using json.loads
        folder_structure = json.loads(folder_text)

        # Close the database connection
        conn.close()

        return [folder_structure]

    def get_folder_names(self):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('SELECT folder_name FROM folder')

        folder_names = cursor.fetchall()

        conn.close()

        return folder_names

    def save_folder_files(self, files_dict, folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Convert the Python dictionary to a JSON string
        files_text = json.dumps(files_dict)

        # Step 4: Insert the serialized JSON string into the database
        if self.check_if_folder_in_database(folder_name):  # Update, if the folder already exists
            cursor.execute('UPDATE folder SET folder_files = ? WHERE folder_name = ?', (files_text, folder_name))
        else:  # Insert, if the folder does not exist
            cursor.execute('INSERT INTO folder (folder_files) VALUES (?)', (files_text,))
        conn.commit()

        # Close the database connection
        conn.close()

    def get_folder_files(self, folder_name):
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 2: Execute a SELECT query to retrieve the JSON data
        cursor.execute('SELECT folder_files FROM folder WHERE folder_name = ?', (folder_name,))

        # Fetch the JSON text
        folder_text = cursor.fetchone()[0]

        # Step 3: Parse the JSON data using json.loads
        folder_files = json.loads(folder_text)

        # Close the database connection
        conn.close()

        return folder_files

    def save_folder_register(self, register_names, folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Convert the list of tags to a comma-separated string
        register_text = ";" + ';'.join(register_names) + ";"  # Convert list of tags to a comma-separated string

        # Step 4: Insert the serialized JSON string into the database
        if self.check_if_folder_in_database(folder_name):
            cursor.execute('UPDATE folder SET folder_register = ? WHERE folder_name = ?', (register_text, folder_name))
        else:
            cursor.execute('INSERT INTO folder (folder_register) VALUES (?)', (register_text,))

        conn.commit()

        conn.close()

    def get_folder_register(self, folder_name):
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 2: Execute a SELECT query to retrieve the JSON data
        cursor.execute('SELECT folder_register FROM folder WHERE folder_name = ?', (folder_name,))

        # Fetch the text
        folder_text = cursor.fetchall()[0][0]

        # Step 3: Parse the text data to a list
        folder_register = folder_text.strip(';').split(';')

        # Close the database connection
        conn.close()

        return folder_register

    def save_folder_timestamp(self, folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 4: Insert the serialized JSON string into the database
        if self.check_if_folder_in_database(folder_name):
            cursor.execute('UPDATE folder SET timestamp = ? WHERE folder_name = ?', (datetime.now(), folder_name))
        else:
            cursor.execute('INSERT INTO folder (timestamp) VALUES (?)', (datetime.now(),))

        conn.commit()

        conn.close()

    def get_folder_timestamp(self, folder_name):
        # Step 1: Connect to the SQLite database
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        # Step 2: Execute a SELECT query to retrieve the JSON data
        cursor.execute('SELECT timestamp FROM folder WHERE folder_name = ?', (folder_name,))

        # Fetch the text
        timestamp = cursor.fetchall()[0][0]

        # Close the database connection
        conn.close()

        return timestamp

    def get_folder_history(self):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('SELECT folder_name, timestamp FROM folder')

        folder_history = cursor.fetchall()

        conn.close()

        return folder_history

    def delete_folder(self, folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM folder WHERE folder_name = ?', (folder_name,))

        conn.commit()

        conn.close()

    def rename_folder(self, folder_name, new_folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('UPDATE folder SET folder_name = ? WHERE folder_name = ?', (new_folder_name, folder_name))

        conn.commit()

        conn.close()

    def get_all_folder_names(self):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('SELECT folder_name FROM folder')

        folder_names = cursor.fetchall()
        folder_names = [item[0] for item in folder_names]

        conn.close()

        return folder_names

    def rename_folder_in_structure(self, new_folder_name):
        conn = sqlite3.connect(self.database_file)
        cursor = conn.cursor()

        cursor.execute('SELECT folder_structure FROM folder WHERE folder_name = ?', (new_folder_name,))

        folder_structure = cursor.fetchone()[0]

        folder_structure = json.loads(folder_structure)

        folder_structure['text'] = new_folder_name

        cursor.execute('UPDATE folder SET folder_structure = ? WHERE folder_name = ?',
                       (json.dumps(folder_structure), new_folder_name))

        conn.commit()

        conn.close()
