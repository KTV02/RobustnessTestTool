import sqlite3
import os
import datetime


class DatabaseHelper:
    def __init__(self, database_file):
        self.database_file = database_file

    #creates the database for the file paths
    def create_container_database(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS docker_containers
                     (name TEXT, path TEXT, date_added TEXT, size INTEGER)''')
        conn.commit()
        conn.close()


    def load_docker_containers(self):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute("SELECT name,path FROM docker_containers")
        results = c.fetchall()
        conn.close()

        return results

    def save_docker_container(self, extract_path, name, size):
        # Save data to the SQLite database
        try:
            conn = sqlite3.connect(self.database_file)
            c = conn.cursor()
            c.execute("INSERT INTO docker_containers VALUES (?, ?, ?, ?)",
                      (name, extract_path, self.get_current_datetime(), size))
            conn.commit()
            conn.close()
            return True, f"Container '{name}' successfully registered"
        except:
            return False, f"Container failed to register: {str(e)}"
            

    def get_current_datetime(self):
        current_datetime = datetime.datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        return formatted_datetime


    def create_results_database(self, transformations_file):
        if not self.database_exists():
            # Datenbank existiert nicht, erstelle sie vollständig
            conn = sqlite3.connect(self.database_file)
            c = conn.cursor()

            transformations = self.read_transformations(transformations_file)
            columns = ["dockerpath", "date","score"] + [f"{transformation}result" for transformation in transformations]
            column_definitions = ", ".join(f"{column} TEXT" for column in columns)

            create_table_query = f"CREATE TABLE results ({column_definitions})"
            c.execute(create_table_query)

            conn.commit()
            conn.close()
        else:
            # Datenbank existiert, überprüfe und ergänze fehlende Spalten
            conn = sqlite3.connect(self.database_file)
            c = conn.cursor()

            transformations = self.read_transformations(transformations_file)
            existing_columns = self.get_existing_columns(c, "results")

            columns_to_add = [f"{transformation}result" for transformation in transformations if f"{transformation}result" not in existing_columns]

            for column in columns_to_add:
                alter_table_query = f"ALTER TABLE results ADD COLUMN {column} TEXT"
                c.execute(alter_table_query)

            conn.commit()
            conn.close()


    def check_results_exist(self, path):
        #selected_item = self.results_listbox.get(selected_index)
        #name, path = selected_item.split("#")
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute("SELECT * FROM results WHERE Dockerpath=?", (path,))
        print("Dockerpath= "+path)
        result = c.fetchone()
        with open("debug.txt", "w") as file:
            file.write(str(path))
        conn.close()
        return result is not None

    def get_result_score(self, path):
        conn = sqlite3.connect(self.database_file)
        c = conn.cursor()
        c.execute("SELECT score FROM results WHERE Dockerpath=?", (path,))
        result=c.fetchone()
        conn.close()
        return result
        

    def database_exists(self):
        return os.path.exists(self.database_file)

    def read_transformations(self, transformations_file):
        with open(transformations_file, "r") as file:
            transformations = [line.strip() for line in file]
        return transformations

    def get_existing_columns(self, cursor, table_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        return columns
