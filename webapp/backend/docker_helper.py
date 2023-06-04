import subprocess

class DockerHelper:
    def tar2image(self, tar_path):
        # Build an image from the tar file
        cmd = f"docker load --input {tar_path}"
        subprocess.run(cmd, shell=True, check=True)
        
        # Extract the image name from the loaded output
        output = subprocess.check_output("docker images --format '{{.Repository}}:{{.Tag}}' | head -n 1", shell=True, text=True)
        image_name = output.strip()

        return image_name

    def start_container(self, image_name, input_dir, output_dir):
        # Start a Docker container from the image
        cmd = f"docker run --gpus 1 --runtime nvidia --ipc=host -v {input_dir}:/input -v {output_dir}:/output {image_name} /usr/local/bin/run_network.sh"
        subprocess.run(cmd, shell=True, check=True)