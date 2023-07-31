import base64
import json
import math
import os
import re
import shutil
import time
from collections import Counter

import numpy as np

from storage_helper import StorageHelper
from transformations_helper import TransformationsHelper
from environment import Environment
from docker_helper import DockerHelper
from eval_helper import EvalHelper
import h5py





class Controller:
    def __init__(self):
        # Initialize the necessary helpers
        self.environment = Environment()
        self.transformations_helper = TransformationsHelper(self.environment)
        self.storage_helper = StorageHelper(self.environment, self.transformations_helper)
        self.docker_helper = DockerHelper()
        self.eval_helper = EvalHelper()
        print("meep")
        # print(self.eval_helper.eval_image("C:/Users/Lennart Kremp/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp/backend/images/image3/output/0/0/output.png","C:/Users/Lennart Kremp/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp/backend/images/image3/solutions/solution-0.png"))
        print(self.evaluate_results("/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp"
                                    "/backend/images/image10/"))

    # self.run_tests("/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp"
    #  "/backend/images/5/")

    #Calculates average etc. of
    def calculateStatisticalMetrics(self,current_transformation):
        # Convert the list to a numpy array
        data_array = np.array(current_transformation)

        # Calculate the mean
        mean = np.mean(data_array)

        # Calculate the median
        median = np.median(data_array)

        # Calculate the standard deviation
        std_deviation = np.std(data_array)

        # Calculate the variance
        variance = np.var(data_array)

        # Calculate the minimum value
        min_value = np.min(data_array)

        # Calculate the maximum value
        max_value = np.max(data_array)

        # Calculate the sum of all elements
        sum_of_elements = np.sum(data_array)
        return [mean, median, std_deviation, variance, min_value, max_value, sum_of_elements]

    def load_docker_containers(self):
        results = self.storage_helper.load_docker_containers()
        return results

    def load_container_results(self, container):
        results = self.storage_helper.get_results(container)
        if results is None or len(results) == 0:
            return "False"
        newest = len(results)
        print("newest: " + str(newest))

        result = results[newest - 1]
        print(result[0])
        fullResult = self.storage_helper.json_2_array(result[0])

        return fullResult

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
        results = container + "output/Stage_1/Sigmoid/"
        transformation_folder = container + self.environment.get_transformation_folder()
        transformation_array, labels = self.get_stored_transformations(transformation_folder)
        metrics=[]

        solutions_path = container + "solutions/"

        # Preallocate the list of arrays
        data3d = []

        # create 3d strucutre for transformation,sample_index, the value array for all testimages
        for _ in range(len(transformation_array)):
            layer = []  # Create a new layer
            # for every trasnformation as often as it has sample steps
            for _ in range(int(transformation_array[_][1])):
                row = list()  # Create a new list
                layer.append(row)
            data3d.append(layer)

        print("TA: " + str(transformation_array))
        foldercount = 0
        # transformation index counts up total transformations (2 with sample_index 3 would still be 2)
        for transformation_index, (transformation, num_folders) in enumerate(transformation_array):
            print(str(transformation_index) + " transformation index")
            print("num: " + str(num_folders))
            for sample_index in range(int(num_folders)):
                current_transformation = []

                print("Transformation: " + str(transformation_index) + " with sample index: " + str(sample_index))
                current_transformation_folder = os.path.join(results, str(foldercount))
                total_images = sum(1 for entry in os.scandir(current_transformation_folder) if entry.is_dir())
                for image_index in range(total_images):
                    print("Image Index: " + str(image_index))
                    current_imagefolder = os.path.join(current_transformation_folder, str(image_index)).replace("\\",
                                                                                                                "/")
                    print(current_imagefolder)
                    solution_filename = "solution-{}.png".format(image_index)
                    solution_filepath = os.path.join(solutions_path, solution_filename)
                    print(solution_filename)

                    output_folder_exists = os.path.exists(current_imagefolder)
                    solution_file_exists = os.path.exists(solution_filepath)
                    print(str(output_folder_exists and solution_file_exists))

                    if output_folder_exists and solution_file_exists:
                        output_filepath = os.path.join(current_imagefolder, "output.png").replace("\\", "/")

                        # Call the eval_image function with the output and solution file paths
                        print(output_filepath)
                        print(solution_filepath)
                        result = self.eval_helper.eval_image(output_filepath, solution_filepath)
                        print(str(image_index) + " image index with result " + str(result))
                        current_transformation.append(result)
                foldercount += 1
                metrics.append(self.calculateStatisticalMetrics(current_transformation))
                data3d[transformation_index][sample_index] = current_transformation
            print(str(data3d))

        self.storage_helper.store_results(container, data3d, labels,metrics)
        # if only results for baseimage or none exists
        if len(data3d) <= 1:
            return False, "No results present"
        return True, data3d

    def input_folder_handler(self, input_folder, transformations, output):
        # Copy the input folder structure without raw.png images
        copied_folders = []
        directories = []
        for root, dirs, files in os.walk(input_folder):
            for directory in dirs:
                directory_path = os.path.join(root, directory)
                directories.append(directory_path)

        input_folder = ""
        if len(directories) > 1:
            raise OSError("Too many directories found in .tar file")
        elif len(directories) == 0:
            # if no directory is found in input folder, it could be that pwd is already inside the input folder
            current_directory = os.getcwd()
            # check if the current directory is not transformations folder (if it were something went wrong and there
            # are no input images)
            if current_directory != "transformations":
                input_folder = current_directory
        elif len(directories) == 1:
            # nice! everything worked
            input_folder = directories[0] + "/"

        for idx, [transformation_name, sampling_rate] in enumerate(transformations):
            for n in range(0, int(sampling_rate)):
                # Create the output folder name using the naming schema
                output_folder_path = f"{os.path.dirname(input_folder)}-{transformation_name}-{n}"
                # Copy the input folder structure without raw.png files
                shutil.copytree(input_folder, output_folder_path, ignore=shutil.ignore_patterns("*.png"))

                copied_folders.append(output_folder_path)

        # Get the current directory
        current_directory = input_folder.split("/transformations/")[0]
        current_directory = os.getcwd() + "/" + current_directory + "/transformations/"

        # ensure no windows double backslash
        current_directory = current_directory.replace("\\", "/")
        print(current_directory)

        # Iterate over the image files in the input_folder
        for root, dirs, files in os.walk(input_folder):
            for file in files:
                if file.lower().endswith(('.png', '.jpg')):
                    # Get the path of the current image
                    raw_png_path = os.path.join(root, file)

                    # Apply transformations to the current image
                    self.transformations_helper.apply_transformations(raw_png_path, transformations, current_directory)

                    # Get the base name and extension of the current image
                    base_name, extension = os.path.splitext(file)

                    # Get the list of transformed images in the current directory
                    transformed_images = [f for f in os.listdir(current_directory) if
                                          f.startswith(base_name) and f.endswith('.png')]
                    # Create the corresponding folder for each transformed image
                    for transformed_image in transformed_images:
                        # Get the transformation name and number from the transformed image name
                        transformed_name, number = transformed_image.replace(base_name + '-', '').rsplit('-', 1)
                        number = number.split(".")[0]

                        # Create the folder name
                        folder_name = f"basefolder-{transformed_name}-{number}"
                        folder_path = os.path.join(current_directory, folder_name)

                        # Move the transformed image to the corresponding folder
                        destination_path = os.path.join(folder_path, transformed_image)
                        shutil.move(os.path.join(current_directory, transformed_image), destination_path)

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
        winpath = "C:/Users/Lennart Kremp/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp/backend/" + dockerpath
        linuxpath = "/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/RobustnessTestTool/webapp/backend/" + dockerpath
        # linuxpath = winpath
        try:
            self.storage_helper.create_test_environment(linuxpath)
        except Exception as e:
            return "Something went wrong while creating testing environment " + str(e)
        try:
            self.docker_helper.start_container(image, linuxpath + self.environment.get_test_dir(),
                                               linuxpath + "output/")
        except Exception as e:
            return "Something went wrong while testing: " + str(e)

        self.evaluate_results(dockerpath)

        return True

        # for folder in self.storage_helper.get_folder_paths(linuxpath + self.environment.get_transformation_folder()):
        #     structure = folder + "/" + "test" + "/"
        #     print("folder: " + structure)
        #     self.docker_helper.start_container(image, structure, linuxpath + "output/" + os.path.basename(folder))

    def image_exists(self, container_name):
        # eigentlich hier tarfile path getten über storagehelper.getdockerpath
        tarfile = self.storage_helper.tarfile_handler(container_name)
        print("finalpath" + str(tarfile))
        if not os.path.isfile(tarfile):
            return "Invalid tarfile"
        return self.docker_helper.is_already_present(tarfile)

    def get_stored_transformations(self, transformations):
        transformation_names = list()
        print(transformations)
        for root, dirs, files in os.walk(transformations):
            for directory in dirs:
                print(directory)
                parts = directory.split('-')
                if len(parts) == 3:
                    transformation_name = parts[1]
                    print(transformation_name)
                    transformation_names.append(transformation_name)
                elif len(parts) == 1 and directory == "basefolder":
                    transformation_names.append("base")

        label_counts = Counter(transformation_names)  # Count the occurrences of each label
        labels = list(label_counts.keys())
        label_counts_2d = [[label, count] for label, count in label_counts.items()]  # Convert to 2D array
        return label_counts_2d, labels
