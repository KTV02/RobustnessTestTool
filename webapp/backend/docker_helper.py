import json
import subprocess
import time

import docker
import tarfile


class DockerHelper:

    def __init__(self):
        self.client = docker.from_env()

    def get_image_name(self, tarfilepath):
        # Open the tar file in read mode
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
        cmd = f"docker run --gpus 1 --runtime nvidia --ipc=host -v {input_dir}:/input -v {output_dir}:/output {image_name} /usr/local/bin/run_network.sh"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        output = result.stdout
        print("Result: "+str(result)+" Output: "+str(output))

    def build_docker(self, imagetar):
        print("building docker")
        with open(imagetar, 'rb') as f:
            self.client.images.load(f)
        print("done")
