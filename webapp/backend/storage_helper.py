import base64
import glob
import json
import re
import shutil
import sqlite3
import os
import datetime
import tarfile
from PIL import Image

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
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT, path TEXT,modelpath TEXT, date_added TEXT, size INTEGER)''')
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
                    FOREIGN KEY (dockerid) REFERENCES docker_containers(id) ON DELETE CASCADE
                )
                '''
        # Execute the query
        c.execute(query)
        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def create_dir(self, dir_path):
        dir_path=dir_path.replace("\\","/")
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

    def save_docker_container(self, extract_path, dockerpath, name, size):
        # Save data to the SQLite database
        try:
            conn = sqlite3.connect(self.environment.get_database_file())
            c = conn.cursor()
            # Null Value muss man übergeben, damit DB sich um ID kümmert
            c.execute("INSERT INTO docker_containers VALUES (NULL,?, ?, ?, ?, ?)",
                      (name, extract_path, dockerpath, get_current_datetime(), size))
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

    def get_folderpath(self, container_id):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT path FROM docker_containers WHERE id =?", (container_id,))
        result = c.fetchone()
        if result is None:
            return False
        dockerpath = result[0]
        print("this is the dockerpath " + str(dockerpath))
        if "\\" in dockerpath:
            dockerpath = dockerpath.replace("\\", "/")
        conn.close()
        return os.path.normpath(dockerpath)

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

    def store_docker(self, tar_file):
        """
        Creates folder for model and registers in database
        :param tar_file: The path to the model inside a tar file
        :return: Error Message or Success message with path and filesize of model
        """

        if tar_file:
            if self.is_tar_file(tar_file):
                unique_name = self.generate_unique_name()
                imagefolder_path = os.path.join(self.environment.get_images_folder(), unique_name).replace("\\", "/")
                self.create_dir(imagefolder_path)
                return True, "Tar file saved successfully!", imagefolder_path, tar_file
            else:
                return False, "No .tar file detected", False, False

    def store_docker_frontend(self, tar_url):
        """
        Creates folder for model,stores tar there and registers in database
        :param tar_url: the url from the frontend to the tar file
        :return: Error Message or Success message with path and filesize of model
        """
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.environment.get_images_folder(), unique_name).replace("\\", "/")
        self.create_dir(extract_path)
        extract_path = extract_path + "/"

        tar = self.save_tar_file_from_frontend(tar_url, extract_path)
        if os.path.isfile(tar):
            if self.is_tar_file(tar):
                size = os.path.getsize(tar)
                return True, "Tar file saved successfully!", extract_path, size
            else:
                return False, "No .tar file detected", False, False
        else:
            raise SystemError(tar)

    def save_tar_file_from_frontend(self, file, path):

        print("strurl" + str(file))

        # Check the file type based on the file extension
        filename = secure_filename(file.filename)
        _, extension = os.path.splitext(filename)
        file_type = extension.lower()[1:]  # Remove the leading dot

        if file_type == "tar":
            tarpath = path + "tarfile.tar"
            file.save(tarpath)
            return tarpath
        else:
            return "Filetype not compatible"

    def save_test_image(self, data_url, container_name):
        dockerpath = str(self.get_folderpath(container_name))
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

            self.extract_tar(extracted_path, output)

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

    # def get_folder_paths(self, directory):
    #     folder_paths = []
    #     for item in os.listdir(directory):
    #         item_path = os.path.join(directory, item)
    #         if os.path.isdir(item_path):
    #             folder_paths.append(item_path)
    #     return folder_paths

    # can handle txt file and tar file
    def tarfile_handler_frontend(self, container):
        returnfile = ""

        path = self.get_folderpath(container)
        txtpath = os.path.join(path, "tarfile.txt")
        print("Model reference path:")
        destination_tar = ""
        if os.path.isfile(txtpath):
            with open(txtpath, 'r') as txt_file:
                # Read the first line
                destination_tar = txt_file.readline().strip()
        else:
            raise FileNotFoundError("Model location reference corrupted")

        # Check if is a valid filepath
        if os.path.isfile(destination_tar) and destination_tar.endswith('.tar'):
            returnfile = destination_tar
        else:
            raise FileNotFoundError("Either model does not exist or has been deleted")

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

    def get_modelpath(self, container_id):
        """
        Returns the path to the tar file containing the image segmentation model
        :param container_id: the container id the model belongs to
        :return: the path to the segmentation model
        """
        print(str(container_id))
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT modelpath FROM docker_containers WHERE id =?", (container_id,))
        result = c.fetchone()
        if result is None:
            raise FileNotFoundError("Model location has not been set")
        modelpath = result[0]
        if "\\" in modelpath:
            modelpath = modelpath.replace("\\", "/")
        conn.close()

        if not os.path.isfile(modelpath) or not modelpath.endswith('.tar'):
            raise FileNotFoundError("Model location corrupted! Has it been deleted?")

        return modelpath

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
        self.create_dir(os.path.join(dockerpath,self.environment.get_test_dir()).replace("\\","/"))
        # get number of transformations
        transformations = os.path.join(dockerpath,self.environment.get_transformation_folder()).replace("\\","/")
        count = 0
        for item in os.listdir(transformations):
            item_path = os.path.join(transformations, item)
            if os.path.isdir(item_path):
                count += 1

        base_folder = os.path.join(os.path.join(dockerpath,self.environment.get_test_dir()), "Stage_1").replace("\\","/")
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
        self.create_dir(os.path.join(container,"results/").replace("\\","/"))
        name="results/" + re.sub(r'\W+', '',f"data{str(datetime.datetime.now())}") + ".json"  # Specify the filename for your HDF5 file
        filename = os.path.join(container,name).replace("\\","/")
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

    def extract_tar(self, extracted_path, output):
        print(extracted_path)
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

    def testdata_exists(self, container):
        containerpath = str(self.get_folderpath(container))
        testimages = self.has_images(containerpath + "transformations/")
        groundtruths = self.has_images(containerpath + "solutions/")
        if isinstance(testimages, str) or isinstance(groundtruths, str):
            return "Error occurred while checking testdata"
        if testimages is None or not testimages:
            return "Testimages not present"
        if groundtruths is None or not groundtruths:
            return "Ground truths not present"
        return True

    def has_images(self, folder_path):
        for root, _, files in os.walk(folder_path):
            for file in files:
                try:
                    with Image.open(os.path.join(root, file)) as img:
                        img.verify()
                        return True
                except:
                    print("error has occured while checking if testdata present")
        return False

    def container_exists(self, container):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        c.execute("SELECT id FROM docker_containers WHERE id=?", (container,))
        result = c.fetchone()
        conn.close()
        if not result:
            return False
        else:
            return True

    def delete_folder(self, path: str):
        """
        Deletes a folder at the given path if it exists.
        :param path: The path of the folder to delete.
        """
        print(os.path.exists(path))
        if os.path.exists(path) and os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return False

        if os.path.exists(path) and os.path.isdir(path):
            return False

        return True

    def delete_docker_container(self, container):
        conn = sqlite3.connect(self.environment.get_database_file())
        c = conn.cursor()
        # check if docker container to be deleted actually exists
        if not self.container_exists(container):
            return "Container to be deleted does not exist"

        # deleting container files
        path = os.path.join(os.getcwd(), str(self.get_folderpath(container)))
        print("Dockerpath: " + str(path))
        if not self.delete_folder(path):
            return "Container files could not be deleted!"

        # deleting docker container from database
        c.execute("DELETE FROM docker_containers WHERE id =?", (container,))
        conn.commit()
        # check if successfull
        if self.container_exists(container):
            return "Container could not be deleted from DB!"

        conn.close()

        return True

    def ground_truth_checker(self, path):
        files = os.listdir(path)
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg'))]
        dirs = [d for d in files if os.path.isdir(os.path.join(path, d))]

        if image_files:
            print("Ground Truths correctly formattted.")
            return True

        if len(dirs) != 1:
            raise SyntaxError("Ground Truths not present or formatted incorrectly")

        inner_path = os.path.join(path, dirs[0])
        inner_files = os.listdir(inner_path)
        inner_image_files = [f for f in inner_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        if not inner_image_files:
            raise SyntaxError("Ground Truths not present or formatted incorrectly")

        for image_file in inner_image_files:
            shutil.move(os.path.join(inner_path, image_file), os.path.join(path, image_file))

        shutil.rmtree(inner_path)
        print("Ground truth format repaired")
