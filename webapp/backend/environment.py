from transformations_helper import TransformationsHelper
from storage_helper import StorageHelper


class Environment:
    def __init__(self):
        self.database_file = "storage/results.db"
        self.transformations_file = "storage/transformations.txt"
        self.tar_dir = "storage/tar/"
        self.assets = "storage/Assets/"
        self.images_folder = "images"
        self.transformation_folder="/transformations/"

    def get_transformation_folder(self):
        return self.transformation_folder

    def get_images_folder(self):
        return self.images_folder

    def get_transformation_file(self):
        return self.transformations_file

    def get_database_file(self):
        return self.database_file

    def get_assets(self):
        return self.assets

    def get_tar_dir(self):
        return self.tar_dir

