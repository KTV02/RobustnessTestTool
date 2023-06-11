import base64
import os
import re
import time
from storage_helper import StorageHelper
from transformations_helper import TransformationsHelper
from environment import Environment


class Controller:
    def __init__(self):
        # Initialize the necessary helpers
        self.environment = Environment()
        self.transformations_helper = TransformationsHelper(self.environment)
        self.storage_helper = StorageHelper(self.environment, self.transformations_helper)

    def load_docker_containers(self):
        results = self.storage_helper.load_docker_containers()
        return results

    def load_container_results(self, container_id):
        result = self.storage_helper.get_result_score(container_id)
        return result

    def save_user_tar(self, tar_file):
        temp_path = self.environment.get_tar_dir() + "temp" + str(int(time.time())) + ".tar"
        # save tar file locally
        tar_file.save(temp_path)
        return temp_path

    def store_container(self, tar_path, name):
        print(str(tar_path))
        # store docker container
        success, message, extract_path, size = self.storage_helper.store_docker(tar_path)
        # if store worked -> create database
        if success:
            success, message = self.storage_helper.save_docker_container(extract_path, name, size)
        return success, message

    def results_available(self, path):
        return self.storage_helper.check_results_exist(path)

    def get_result_score(self, path):
        return self.storage_helper.get_result_score(path)

    def transform_images(self, container, images, transformations):
        output = str(self.storage_helper.get_dockerpath(container)) + self.environment.get_transformation_folder()
        print("output:" + str(output))
        answer = self.transformations_helper.apply_transformations(images, transformations, output)
        if answer != "False":
            return "True"
        else:
            return answer

    # returns an Array of labels of the available transformations
    def get_available_transformations(self):
        return self.transformations_helper.get_available_transformations()

    def exit(self):
        pass

    def save_test_image(self, data_url, container_name):
        dockerpath = self.storage_helper.get_dockerpath(container_name)
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
        else:
            return "Not a supported Filetype: " + mime_type

        # Generate a unique file name
        filename = 'baseimage.' + extension
        filename = output + filename

        # Save the file to disk
        with open(filename, 'wb') as f:
            if encoding == 'base64':
                f.write(base64.b64decode(data))
            else:
                return "Encoding not supported: " + encoding
        return filename

    def build_docker(self, container_name):
        pass

    def run_tests(self, container_name):
        pass
