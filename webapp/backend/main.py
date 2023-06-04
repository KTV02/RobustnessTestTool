from tkinter import Tk
from database_helper import DatabaseHelper
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper
from controller import Controller

# Define the paths and filenames
database_file = "results.db"
transformations_file = "transformations.txt"

# Create an instance of DatabaseHelper
database_helper = DatabaseHelper(database_file)
transformations_helper = TransformationsHelper(transformations_file)
files_helper = FilesHelper()

#SETUP
# Check if the database exists and is correct
database_helper.create_results_database(transformations_file)
database_helper.create_container_database()


# Create an instance of the controller
controller = Controller(database_helper, transformations_helper, files_helper)

