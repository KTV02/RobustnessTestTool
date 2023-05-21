from tkinter import Tk
from database_helper import DatabaseHelper
from ui import RobustnessTestUI
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper

# Define the paths and filenames
database_file = "results.db"
transformations_file = "transformations.txt"

# Create an instance of DatabaseHelper
database_helper = DatabaseHelper(database_file)
transformations_helper = TransformationsHelper(transformations_file)
files_helper = FilesHelper()


# Check if the database exists and is correct
database_helper.create_results_database(transformations_file)
database_helper.create_container_database()

# Create an instance of RobustnessTestUI
ui = RobustnessTestUI(database_helper,transformations_helper, files_helper)

# Start the UI
ui.run()
