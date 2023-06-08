import os
import time
from storage_helper import StorageHelper
from transformations_helper import TransformationsHelper
from environment import Environment

class Controller:
    def __init__(self):
        # Initialize the necessary helpers
        self.environment = Environment()
        self.transformations_helper = TransformationsHelper(self.environment)
        self.storage_helper = StorageHelper(self.environment,self.transformations_helper)


    def load_docker_containers(self):
        results = self.storage_helper.load_docker_containers()
        return results

    def save_user_tar(self, tar_file):
        temp_path = self.environment.get_tar_dir()+"temp"+str(int(time.time()))+".tar"
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

    def run_tests_for_container(self, container, images, transformations):
        print("backend:")
        print(transformations)
        output = "./images/ " + container + "/transformations/"
        self.transformations_helper.apply_transformations(images, transformations, output)
        # Implementation for running tests for a container

    # returns an Array of labels of the available transformations
    def get_available_transformations(self):
        return self.transformations_helper.get_available_transformations()

    def exit(self):
        pass