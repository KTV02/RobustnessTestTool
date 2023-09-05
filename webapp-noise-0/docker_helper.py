import json
import subprocess
import time
import urllib

import docker
import tarfile

import requests
import os


class DockerHelper:

    def __init__(self):

        self.client = docker.from_env()
        # self.client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        for image in self.client.images.list():
            print(str(image.tags))
        print(str(self.client.images.list))
        image_exists = any("fabianisensee:robustmis" in image.tags for image in self.client.images.list())
        print(str(image_exists))

        current_directory = os.getcwd()
        print(current_directory)
        #self.start_container("fabianisensee:robustmis", "/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/dataset/test",  "/mnt/c/Users/lkrem/OneDrive/Studium/Bachelorarbeit/dataset/output")

        # client = docker.DockerClient(base_url='unix://var/run/docker.sock')
        # aversion_info = self.client.version()

        # print(version_info)
        # cmd = f"python --version"
        # result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        # output = result.stdout
        # print(output)
        # self.client = docker.DockerClient(base_url='unix:///var/run/docker.sock')
        # self.client= ""
        # self.check_image_exists("fabianisensee")

    def check_image_exists(self, image_name):
        base_url = 'http://172.20.11.8:2375'
        api_version = 'v1.41'  # Adjust the API version based on your Docker version

        filter_value = urllib.parse.quote('reference=="' + image_name + '"')
        url = f'{base_url}/v{api_version}/images/json?filter={filter_value}'

        try:
            response = requests.get(url)
            response.raise_for_status()
            images = response.json()
            print(len(images))
            return len(images) > 0
        except requests.exceptions.RequestException as e:
            print(f'Error occurred while checking image: {e}')
            return False

    def get_image_name(self, tarfilepath):
        """
        Checks the name of a docker container with a segmentation model
        :param tarfilepath: the path to the tar file containing the model
        :return: the name of the docker container inside the tar file
        """

        # Open the tar file in read mode
        print(tarfilepath)
        with tarfile.open(tarfilepath, 'r') as tar:
            # Check if the manifest.json file is present in the tar file
            if "manifest.json" in tar.getnames():
                # Extract the manifest.json file from the tar file
                tar.extract("manifest.json")

        # Read the contents of manifest.json file
        with open("manifest.json", 'r') as file:
            manifest_content = json.load(file)

        # Extract the image name from the RepoTags field
        return manifest_content[0]['RepoTags'][0]

    # check if the image of the tarfile is already loaded
    def is_already_present(self, tarfilepath):
        image_name = self.get_image_name(tarfilepath)
        print("image name:" + image_name)
        # Check if the image exists
        image_exists = any(image_name in image.tags for image in self.client.images.list())
        print("does image exist? " + str(image_exists))
        return image_exists

    def tar2image(self, tar_path):
        # Build an image from the tar file
        cmd = f"docker load --input {tar_path}"
        subprocess.run(cmd, shell=True, check=True)

        # Extract the image name from the loaded output
        output = subprocess.check_output("docker images --format '{{.Repository}}:{{.Tag}}' | head -n 1", shell=True,
                                         text=True)
        image_name = output.strip()

        return image_name

    def start_container(self, image_name, input_dir, output_dir):
        # Start a Docker container from the image
        cmd = f"sudo docker run --gpus 1 --runtime nvidia --ipc=host -v {input_dir}:/input -v {output_dir}:/output {image_name} /usr/local/bin/run_network.sh"
        print(cmd)



        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Read and print the output in real-time
        while True:
            output = process.stdout.readline().strip()
            if output:
                print(output)
            else:
                break

        # Wait for the process to finish
        process.wait()

        # Check the return code of the process
        if process.returncode != 0:
            print("Error: Command failed with a non-zero exit code.")



        #result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        #output = result.stdout
        #print("Result: " + str(result) + " Output: " + str(output))

    def build_docker(self, imagetar):
        print("building docker")
        with open(imagetar, 'rb') as f:
            self.client.images.load(f)
        print("done")
