import os
import tarfile

class FilesHelper:
    
    def __init__(self):
        self.images_folder = "images"  # Pfad zum Ordner für die entpackten Docker-Images
        self.create_images_folder()  # Erstelle den Ordner, falls er noch nicht existiert

    def store_docker(self,file_path):
        if file_path:
            if self.is_tar_file(file_path):
                size = os.path.getsize(file_path)
                success, message, extract_path = self.extract_docker_image(file_path)
                return success,message,extract_path, size
            else:
                return False,"No .tar file detected", None, None

    def create_images_folder(self):
        if not os.path.exists(self.images_folder):
            os.makedirs(self.images_folder)


    def extract_docker_image(self,file_path):
        #Ordner in den .tar entpackt wird hat einen einzigartigen Namen -> getrennt von Namen des Containers
        unique_name = self.generate_unique_name()
        extract_path = os.path.join(self.images_folder, unique_name)

        try:
            with tarfile.open(file_path, "r") as tar:
                tar.extractall(extract_path)
            return True,'f"Docker image extracted to: {extract_path}"',extract_path
        except tarfile.TarError as e:
            return False,f"Failed to extract Docker image: {str(e)}",None
        

    def is_tar_file(self,file_path):
        return tarfile.is_tarfile(file_path)
    
    def generate_unique_name(self):
        i = 1
        while True:
            unique_name = f"image{i}"
            extract_path = os.path.join(self.images_folder, unique_name)
            if not os.path.exists(extract_path):
                return unique_name
            i += 1

