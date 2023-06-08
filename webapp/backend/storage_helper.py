import sqlite3
import os
import datetime
import tarfile


def get_current_datetime():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


class StorageHelper:
    def __init__(self, environment,transformations_helper):
        self.environment=environment
        self.create_results_database(transformations_helper.get_available_transformations())
        self.create_container_database()
        self.create_dir(self.environment.get_tar_dir())
        self.create_dir(self.environment.get_images_folder())

    # creates the database for the file paths
    def create_container_database(self):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS docker_containers
                     (name TEXT, path TEXT, date_added TEXT, size INTEGER)''')
        conn.commit()
        conn.close()

    def create_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Directory created: {dir_path}")
        else:
            print(f"Directory already exists: {dir_path}")


    def load_docker_containers(self):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT name,path FROM docker_containers")
        results = c.fetchall()
        conn.close()

        return results

    def save_docker_container(self, extract_path, name, size):
        # Save data to the SQLite database
        try:
            conn = sqlite3.connect(self.environment.get_database_file())
            c = conn.cursor()
            c.execute("INSERT INTO docker_containers VALUES (?, ?, ?, ?)",
                      (name, extract_path, get_current_datetime(), size))
            conn.commit()
            conn.close()
            return True, f"Container '{name}' successfully registered"
        except:
            return False, f"Container failed to register: {str(e)}"

    def create_results_database(self, transformations):
        if not self.database_exists():
            # Datenbank existiert nicht, erstelle sie vollständig
            conn = sqlite3.connect(self.environment.get_database_file())
            c = conn.cursor()

            columns = ["dockerpath", "date", "score"] + [f"{transformation}result" for transformation in
                                                         transformations]
            column_definitions = ", ".join(f"{column} TEXT" for column in columns)

            create_table_query = f"CREATE TABLE results ({column_definitions})"
            c.execute(create_table_query)

            conn.commit()
            conn.close()
        else:
            # Datenbank existiert, überprüfe und ergänze fehlende Spalten
            conn = sqlite3.connect(self.environment.get_database_file())
            c = conn.cursor()

            existing_columns = self.get_existing_columns(c, "results")

            columns_to_add = [f"{transformation}result" for transformation in transformations if
                              f"{transformation}result" not in existing_columns]

            for column in columns_to_add:
                alter_table_query = f"ALTER TABLE results ADD COLUMN {column} TEXT"
                c.execute(alter_table_query)

            conn.commit()
            conn.close()

    def check_results_exist(self, path):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT dockerpath FROM results WHERE Dockerpath=?", (path,))
        print("Dockerpath= " + path)
        result = c.fetchone()
        conn.close()
        print(result)
        return result is not None

    def get_result_score(self, path):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT score FROM results WHERE Dockerpath=?", (path,))
        result = c.fetchone()
        conn.close()
        return result

    def database_exists(self):
        return os.path.exists(self.environment.get_database_file())

    def get_existing_columns(self, cursor, table_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        return columns

    def store_docker(self, tar_path):
        if tar_path:
            if self.is_tar_file(tar_path):
                size = os.path.getsize(tar_path)
                success, message, extract_path = self.extract_docker_image(tar_path)
                return success, message, extract_path, size
            else:
                return False, "No .tar file detected", None, None

    def extract_docker_image(self, file_path):
        # Ordner in den .tar entpackt wird hat einen einzigartigen Namen -> getrennt von Namen des Containers
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.environment.get_images_folder(), unique_name)

        try:
            with tarfile.open(file_path, "r") as tar:
                tar.extractall(extract_path)
            return True, 'f"Docker image extracted to: {extract_path}"', extract_path
        except tarfile.TarError as e:
            return False, f"Failed to extract Docker image: {str(e)}", None

    def is_tar_file(self, file_path):
        return tarfile.is_tarfile(file_path)

    def generate_unique_name(self):
        i = 1
        while True:
            unique_name = f"image{i}"
            extract_path = os.path.join(self.environment.get_images_folder(), unique_name)
            if not os.path.exists(extract_path):
                return unique_name
            i += 1
