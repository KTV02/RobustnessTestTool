import base64
import glob
import json
import re
import shutil
import sqlite3
import os
import datetime
import tarfile
import tkinter as tk
from tkinter import filedialog

import h5py
import numpy as np
from werkzeug.utils import secure_filename


def get_current_datetime():
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime


class StorageHelper:
    def __init__(self, environment, transformations_helper):
        self.environment = environment
        self.create_results_database()
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

    def create_results_database(self):
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
                    resultfile TEXT,
                    FOREIGN KEY (dockerid) REFERENCES docker_containers(id)
                )
                '''
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

    def get_results(self, path):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute(
            "SELECT resultfile FROM results  WHERE dockerid = ? ORDER BY date",
            (path,))
        print("Dockerpath= " + str(path))
        result = c.fetchall()
        conn.close()
        return result

    def json_2_array(self, path):
        # Read the JSON file
        with open(path, 'r') as file:
            json_data = json.load(file)

        # Reconstruct the 3D array
        print(json_data)
        return json_data

    def get_dockerpath(self, container_id):
        print(container_id)
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT path FROM docker_containers WHERE id =?", (container_id,))
        result = c.fetchone()
        if result is None:
            return False
        dockerpath = result[0]
        print(dockerpath)
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
        extract_path = os.path.join(self.environment.get_images_folder(), unique_name).replace("\\", "/")
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

            # name format of testimages, will be passed to the function in the future
            name = "raw"
            type = ".png"
            testimage = name + type

            self.extract_tar(extracted_path,output)

            # Verify if the extracted path points to a .tar file
            return
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

    def get_folder_paths(self, directory):
        folder_paths = []
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                folder_paths.append(item_path)
        return folder_paths

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
            print("destoe:" + str(destination_tar))
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

    def create_test_environment(self, dockerpath):
        # create test directory
        self.create_dir(dockerpath + self.environment.get_test_dir())
        # get number of transformations
        transformations = dockerpath + self.environment.get_transformation_folder()
        count = 0
        for item in os.listdir(transformations):
            item_path = os.path.join(transformations, item)
            if os.path.isdir(item_path):
                count += 1

        base_folder = os.path.join(dockerpath + "/" + self.environment.get_test_dir(), "Stage_1")
        subfolder_1 = "Sigmoid"
        # subfolder_2 = "1"

        # Create the base folder
        os.makedirs(base_folder, exist_ok=True)

        # Create the subfolders
        os.makedirs(os.path.join(base_folder, subfolder_1), exist_ok=True)

        # iterate over every folder in the /transformations and copy the images to the correct position in "running"
        transformation_counter = 0
        for folder in os.scandir(transformations):
            # make sure its actually a transformation folder
            if folder.is_dir():
                # create one folder for each transformation
                destination_folder = os.path.join(base_folder + "/" + subfolder_1 + "/" + str(transformation_counter))
                os.makedirs(destination_folder, exist_ok=True)
                # path to current transformation folder
                folder_path = os.path.join(transformations, folder)
                # for every testimage
                count = 0
                for file in os.listdir(folder_path):
                    filepath = os.path.join(folder_path, file)
                    # make sure is image
                    if os.path.isfile(filepath) and self.environment.valid_image(filepath):
                        image = filepath
                        source_image_path = os.path.join(folder_path, image)

                        destination_image_folder = os.path.join(destination_folder, str(count))
                        os.makedirs(destination_image_folder, exist_ok=True)
                        destination_image_path = os.path.join(destination_image_folder, "raw.png")
                        print(destination_image_path)
                        shutil.copy2(source_image_path, destination_image_path)
                        count += 1
                        print("Copied", image, "from", folder, "to", destination_folder)
                transformation_counter += 1

        print("Folder structure created successfully.")

    def store_results(self, container, data3d, labels, metrics):
        print("Saving file")
        # create uniqe filename -> datetime and remove specialcharacters and append path to container
        self.create_dir(container + "results")
        filename = container + "results/" + re.sub(r'\W+', '',
                                                   f"data{str(datetime.datetime.now())}") + ".json"  # Specify the filename for your HDF5 file
        print(filename)
        # Convert the 3D list to a structured NumPy array
        # dt = h5py.special_dtype(vlen=np.dtype('int32'))
        # data_array = np.array([np.array(subarr, dtype=dt) for subarr in data3d])

        # Convert the 3D Python list to a compatible data structure
        converted_data = json.dumps(data3d)
        converted_labels = json.dumps(labels)
        converted_metrics = json.dumps(metrics)
        save = {
            "data": converted_data,
            "metrics": converted_metrics,
            "labels": converted_labels

        }
        # Save the converted data to a JSON file
        with open(filename, 'w') as file:
            json.dump(save, file)

        self.insert_new_result(container, filename)

    def insert_new_result(self, container, resultfile):
        # if full path is passed -> shorten to local path before storing in db
        if ":" in resultfile:
            resultfile = resultfile.split("backend/")[1]

        print("Inserting new Result in " + container)
        path = "images/" + container.split("images/")[1]
        print(path)
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT id FROM docker_containers WHERE path=?", (path,))
        id = c.fetchone()
        if id is not None and id[0] is not None and isinstance(id[0], int):
            id = id[0]
        else:
            return "No ID found for container: " + container
        print("id of docker is: " + str(id))
        c.execute("INSERT INTO results (dockerid,date,resultfile) VALUES(?,?,?)",
                  (id, datetime.datetime.now(), resultfile))
        conn.commit()
        conn.close()

    def open_file_dialog(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        file_path = filedialog.askopenfilename(filetypes=[('tar files', '*.tar')])
        if file_path is not None and self.is_tar_file(file_path):
            return file_path
        else:
            return "False"

    def extract_tar(self, extracted_path,output):
        if extracted_path.endswith('.tar'):
            # Extract the contents of the .tar file to a specific folder
            tar_output_folder = output
            with tarfile.open(extracted_path, 'r') as tar:
                for file in tar.getmembers():
                    if os.path.basename(file.name).lower().endswith(('.png', '.jpg')):
                        tar.extract(file, path=tar_output_folder)
            return tar_output_folder
        else:
            return "No path to tar file found"
