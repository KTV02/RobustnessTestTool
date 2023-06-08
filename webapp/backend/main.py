from tkinter import Tk
from transformations_helper import TransformationsHelper
from controller import Controller
from storage_helper import StorageHelper

# Define the paths and filenames
database_file = "results.db"
transformations_file = "transformations.txt"

# Create an instance of DatabaseHelper
transformations_helper = TransformationsHelper(transformations_file)
storage_helper=StorageHelper(database_file)

#SETUP
# Check if the database exists and is correct
storage_helper.create_results_database(transformations_file)
storage_helper.create_container_database()


# Create an instance of the controller
controller = Controller( storage_helper, transformations_helper,)

