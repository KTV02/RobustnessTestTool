import base64
import os
import re
import time
from storage_helper import StorageHelper
from transformations_helper import TransformationsHelper
from environment import Environment
from docker_helper import DockerHelper


class Controller:
    def __init__(self):
        # Initialize the necessary helpers
        self.environment = Environment()
        self.transformations_helper = TransformationsHelper(self.environment)
        self.storage_helper = StorageHelper(self.environment, self.transformations_helper)
        self.docker_helper = DockerHelper()

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
        print("imagepath:"+str(images))
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
        self.storage_helper.create_dir(self.storage_helper.get_dockerpath(container_name)+self.environment.get_transformation_folder())
        return self.storage_helper.save_test_image(data_url, container_name)

    def build_docker(self, container_name):
        time.sleep(10)
        pass

    def run_tests(self, container_name):
        pass

    def image_exists(self, container_name):
        # eigentlich hier tarfile path getten über storagehelper.getdockerpath
        return self.docker_helper.is_already_present(
            "C:\\Users\\lkrem\OneDrive\\Studium\\Bachelorarbeit\\RobustnessTestTool\\dockers\\Isensee_RobustMIS.tar")
