from database_helper import DatabaseHelper
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper


class Controller:
    def __init__(self, database_helper, transformations_helper, files_helper):
        # Initialize the necessary helpers
        self.database_helper = database_helper
        self.transformations_helper = transformations_helper
        self.files_helper = files_helper

    def load_docker_containers(self):
        results = self.database_helper.load_docker_containers()
        return results

    def store_container(self, file_path, name):
        # store docker container
        success, message, extract_path, size = self.files_helper.store_docker(file_path)
        # if store worked -> create database
        if success:
            success, message = self.database_helper.save_docker_container(extract_path, name, size)
        return success, message

    def results_available(self, path):
        return self.database_helper.check_results_exist(path)

    def get_result_score(self, path):
        return self.database_helper.get_result_score(path)

    def run_tests_for_container(self,container,images,transformations):
        output="./images/"+container+"/transformations/"
        self.transformations_helper.apply_transformations(images,transformations,output)
        # Implementation for running tests for a container

    #returns an Array of labels of the available transformations
    def get_available_transformations(self):
        return self.transformations_helper.get_available_transformations()

    def exit(self):
        pass