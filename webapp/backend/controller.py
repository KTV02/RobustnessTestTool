import base64
import os
import re
import shutil
import time
from storage_helper import StorageHelper
from transformations_helper import TransformationsHelper
from environment import Environment
from docker_helper import DockerHelper
from eval_helper import EvalHelper


class Controller:
    def __init__(self):
        # Initialize the necessary helpers
        self.environment = Environment()
        self.transformations_helper = TransformationsHelper(self.environment)
        self.storage_helper = StorageHelper(self.environment, self.transformations_helper)
        self.docker_helper = DockerHelper()
        self.eval_helper = EvalHelper()

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
        print("imagepath:" + str(images))

        if os.path.isfile(images):
            # If the image path points to a file, apply transformations directly
            answer = self.transformations_helper.apply_transformations(images, transformations, output)
        elif os.path.isdir(images):
            # If the image path points to a folder, call input_folder_handler function
            answer = self.input_folder_handler(images, transformations, output)
        else:
            return "Invalid image path: " + str(images)

        if answer != "False":
            return "True"
        else:
            return answer

    def evaluate_results(self, container):
        results = container + self.environment.get_transformation_folder()
        pass

    def input_folder_handler(self, input_folder, transformations, output):
        # Copy the input folder structure without raw.png images
        copied_folders = []
        for idx, [transformation_name, sampling_rate] in enumerate(transformations):
            for n in range(0, int(sampling_rate)):
                # Create the output folder name using the naming schema
                output_folder_path = f"{os.path.dirname(input_folder)}-{transformation_name}-{n}"
                # output_folder_path = os.path.join(output, output_folder_name)
                # Copy the input folder structure without raw.png files
                shutil.copytree(input_folder, output_folder_path, ignore=shutil.ignore_patterns("raw.png"))

                copied_folders.append(output_folder_path)

        # Iterate over raw.png files in the original input folder
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file == "raw.png":
                    raw_png_path = os.path.join(root, file)
                    print("raw png path " + str(raw_png_path))
                    raw_png_internal_path = os.path.relpath(raw_png_path, input_folder)
                    print("internal path " + str(raw_png_internal_path))

                    # Apply transformations to each copied folder
                    for copied_folder in copied_folders:
                        # Generate the transformed image name using the naming schema
                        transformed_image_name = f"{os.path.basename(copied_folder)}.png"
                        transformed_image_name = transformed_image_name.replace("basefolder", "raw")
                        print(str(transformed_image_name))
                        transformed_image_path = os.path.join(output, transformed_image_name)
                        # Apply transformations using the transformation_helper and save the transformed image
                        self.transformations_helper.apply_transformations(raw_png_path, transformations, output)

                        # Replace the corresponding raw.png with the transformed image in each copied folder
                        destination_path = os.path.join(copied_folder, raw_png_internal_path)
                        shutil.move(transformed_image_path, destination_path)
                        # Move image from root folder inside corresponding copied folder
                        # Ignore
                        # transformed_image_internal_path = transformed_image_internal_path.replace("raw.png", transformed_image_name)
                        # shutil.copy2(transformed_image_path, transformed_image_internal_path)

        return "True"

    # returns an Array of labels of the available transformations
    def get_available_transformations(self):
        return self.transformations_helper.get_available_transformations()

    def exit(self):
        pass

    def save_test_image(self, data_url, container_name):
        self.storage_helper.create_dir(
            self.storage_helper.get_dockerpath(container_name) + self.environment.get_transformation_folder())

        return self.storage_helper.save_test_image(data_url, container_name)

    def build_docker(self, container_name):
        tarfile = self.storage_helper.tarfile_handler(container_name)
        self.docker_helper.build_docker(tarfile)
        time.sleep(10)

    def run_tests(self, container_name):
        dockerpath = self.storage_helper.get_dockerpath(container_name)
        tarfile = self.storage_helper.tarfile_handler(container_name)
        image = self.docker_helper.get_image_name(tarfile)
        linuxpath = "/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp/backend/" + dockerpath
        for folder in self.storage_helper.get_folder_paths(linuxpath + self.environment.get_transformation_folder()):
            structure = folder + "/" + "test" + "/"
            print("folder: " + structure)
            self.docker_helper.start_container(image, structure, linuxpath + "output/" + os.path.basename(folder))

    def image_exists(self, container_name):
        # eigentlich hier tarfile path getten über storagehelper.getdockerpath
        tarfile = self.storage_helper.tarfile_handler(container_name)
        print("finalpath" + str(tarfile))
        if not os.path.isfile(tarfile):
            return "Invalid tarfile"
        return self.docker_helper.is_already_present(tarfile)
