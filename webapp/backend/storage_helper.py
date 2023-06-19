import base64
import glob
import re
import sqlite3
import os
import datetime
import tarfile

from werkzeug.utils import secure_filename


def get_current_datetime():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


class StorageHelper:
    def __init__(self, environment, transformations_helper):
        self.environment = environment
        self.create_results_database(transformations_helper.get_available_transformations())
        self.create_container_database()
        self.create_dir(self.environment.get_tar_dir())
        self.create_dir(self.environment.get_images_folder())

    # creates the database for the file paths
    def create_container_database(self):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS docker_containers
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT, path TEXT, date_added TEXT, size INTEGER)''')
        conn.commit()
        conn.close()

    def create_results_database(self, transformations):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        # Check if the 'results' table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='results'")
        table_exists = c.fetchone()

        query = ""
        if not table_exists:
            # Tabelle existiert nicht, erstelle sie vollständig

            # Create the results table with foreign key
            query = '''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY,
                    dockerid INTEGER,
                    date TEXT,
                    score DOUBLE,
                    {transformation_columns},
                    FOREIGN KEY (dockerid) REFERENCES docker_containers(id)
                )
                '''.format(
                transformation_columns=", ".join(f"{transformation}result TEXT" for transformation in transformations))
        else:
            # Get the current columns of the 'results' table
            c.execute("PRAGMA table_info(results)")
            existing_columns = [column[1] for column in c.fetchall()]

            # Add missing columns
            columns_to_add = []
            for transformation in transformations:
                if f"{transformation}result" not in existing_columns:
                    columns_to_add.append(f"{transformation}result TEXT")

            if columns_to_add:
                # Alter the table to add missing columns
                query = '''
                        ALTER TABLE results
                        {columns_to_add}
                        '''.format(columns_to_add=", ".join("ADD COLUMN " + column for column in columns_to_add))
        # Execute the query
        c.execute(query)
        # Commit the changes and close the connection
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
        c.execute("SELECT name,id FROM docker_containers")
        results = c.fetchall()
        conn.close()

        return results

    def save_docker_container(self, extract_path, name, size):
        # Save data to the SQLite database
        try:
            conn = sqlite3.connect(self.environment.get_database_file())
            c = conn.cursor()
            # Null Value muss man übergeben, damit DB sich um ID kümmert
            c.execute("INSERT INTO docker_containers VALUES (NULL,?, ?, ?, ?)",
                      (name, extract_path, get_current_datetime(), size))
            conn.commit()
            conn.close()
            return True, f"Container '{name}' successfully registered"
        except Exception as e:
            return False, f"Container failed to register: {str(e)}"

    def check_results_exist(self, path):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT dockerpath FROM results WHERE Dockerpath=?", (path,))
        print("Dockerpath= " + path)
        result = c.fetchone()
        conn.close()
        print(result)
        return result is not None

    def get_dockerpath(self, container_id):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT path FROM docker_containers WHERE id =?", (container_id,))
        result = c.fetchone()
        dockerpath = result[0]
        if "\\" in dockerpath:
            dockerpath = dockerpath.replace("\\", "/")
        conn.close()
        return dockerpath

    def get_result_score(self, dockerid):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        print(dockerid)
        c.execute("SELECT score FROM results WHERE dockerid=?", (dockerid,))
        result = c.fetchone()
        conn.close()
        return result

    def database_exists(self):
        return os.path.exists(self.environment.get_database_file())

    def get_existing_columns(self, cursor, table_name):
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        return columns

    def store_docker(self, tar_url):
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.environment.get_images_folder(), unique_name)
        self.create_dir(extract_path)
        extract_path = extract_path + "/"

        tar = self.save_tar_file(tar_url, extract_path)
        if tar:
            # EIGENTLICH CHECKEN OB TARFILE:::: TEMP
            # if self.is_tar_file(tar):
            if True:
                # size = os.path.getsize(tar)
                size = 1
                return True, "Tar file saved successfully", extract_path, size
            else:
                return False, "No .tar file detected", False, False

    def save_tar_file(self, file, path):

        print("strurl" + str(file))

        # Check the file type based on the file extension
        filename = secure_filename(file.filename)
        _, extension = os.path.splitext(filename)
        file_type = extension.lower()[1:]  # Remove the leading dot

        if file_type == "txt":
            tarpath = path + "tarfile.txt"
            file.save(tarpath)
            return str(tarpath) + " saved to " + str(tarpath)
        elif file_type == "tar":
            tarpath = path + "tarfile.tar"
            file.save(tarpath)
            return str(tarpath) + " saved to " + str(tarpath)
        else:
            return "Filetype not compatible"
        # Eigentlich wird tarfile auf server gespeichert TEMPORÄR HIER AUSKOMMENTIERT
        # file.save(tarpath)

        # # Extract the file type and data from the data URL
        # match = re.search(r'^data:(.*?);(.*?),(.*)$', url)
        # mime_type = match.group(1)
        # encoding = match.group(2)
        # data = match.group(3)
        #
        # extension = ""
        # # Determine the file extension based on the MIME type
        # if mime_type == 'application/x-tar':
        #     extension = '.tar'
        # else:
        #     return "Not a tar file: " + mime_type
        #
        # # Generate a unique file name
        # filename = 'docker' + extension
        # filename = path + filename
        # print("endfilename: "+str(filename))
        #
        # # Save the file to disk
        # with open(filename, 'wb') as f:
        #     if encoding == 'base64':
        #         f.write(base64.b64decode(data))
        #     else:
        #         return "Encoding not supported: " + encoding
        return tarpath

    def save_test_image(self, data_url, container_name):
        dockerpath = self.get_dockerpath(container_name)
        output = dockerpath + self.environment.get_transformation_folder()

        # Extract the file type and data from the data URL
        match = re.search(r'^data:(.*?);(.*?),(.*)$', data_url)
        mime_type = match.group(1)
        encoding = match.group(2)
        data = match.group(3)

        extension = ""
        # Determine the file extension based on the MIME type
        if mime_type == 'image/jpeg':
            extension = 'jpg'
        elif mime_type == 'image/png':
            extension = 'png'
        elif mime_type == 'image/jpg':
            extension = 'jpg'
        elif mime_type == 'text/plain':
            # Decode the data to get the content of the text file
            decoded_data = base64.b64decode(data).decode('utf-8')

            # Extract the path from the text file
            extracted_path = decoded_data.strip()

            # Verify if the extracted path points to a .tar file
            if extracted_path.endswith('.tar'):
                # Extract the contents of the .tar file to a specific folder
                tar_output_folder = output + 'basefolder/'
                with tarfile.open(extracted_path, 'r') as tar:
                    tar.extractall(path=tar_output_folder)
                # Return the output folder where the contents are extracted
                return tar_output_folder
            else:
                return "No path to tar file found in uploaded file: "+str(match)
        else:
            return "Not a supported Filetype: " + mime_type

        filename = 'baseimage.' + extension
        filename = output + filename

        # Save the file to disk
        with open(filename, 'wb') as f:
            if encoding == 'base64':
                f.write(base64.b64decode(data))
            else:
                return "Encoding not supported: " + encoding
        return filename

    # can handle txt file and tar file
    def tarfile_handler(self, container):
        returnfile = ""

        path = self.get_dockerpath(container)
        txtpath = path + "tarfile.txt"
        tarpath = path + "tarfile.tar"
        if os.path.isfile(txtpath):
            with open(txtpath, 'r') as txt_file:
                # Read the first line
                destination_tar = txt_file.readline().strip()

            # Check if is a valid filepath
            if os.path.isfile(destination_tar) and destination_tar.endswith('.tar'):
                returnfile = destination_tar
        elif os.path.isfile(tarpath):
            returnfile = tarpath
        return returnfile

    # def extract_docker_image(self, file_path):
    #     # Ordner in den .tar entpackt wird hat einen einzigartigen Namen -> getrennt von Namen des Containers
    #     unique_name = self.generate_unique_name()
    #     extract_path = os.path.join(self.environment.get_images_folder(), unique_name)
    #
    #     try:
    #         with tarfile.open(file_path, "r") as tar:
    #             tar.extractall(extract_path)
    #         return True, 'f"Docker image extracted to: {extract_path}"', extract_path
    #     except tarfile.TarError as e:
    #         return False, f"Failed to extract Docker image: {str(e)}", None

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
