from database_helper import DatabaseHelper
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper
from ui import RobustnessTestUI

# Define the paths and filenames
database_file = "results.db"
transformations_file = "transformations.txt"

# Create an instance of DatabaseHelper
database_helper = DatabaseHelper(database_file)
transformations_helper = TransformationsHelper(transformations_file)
files_helper = FilesHelper()

# Create an instance of RobustnessTestUI
ui = RobustnessTestUI(database_helper, transformations_helper, files_helper)

# Start the UI
ui.run()
