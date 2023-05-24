from database_helper import DatabaseHelper
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper

class Controller:
    def __init__(self,database_helper, transformations_helper, files_helper):
        # Initialize the necessary helpers
        self.database_helper = database_helper
        self.transformations_helper = transformations_helper
        self.files_helper =files_helper
        

    def load_docker_containers(self):
        results = self.database_helper.load_docker_containers()
        return results
        

    def store_container(self,file_path,name):
        # store docker container
        success, message, extract_path, size = self.files_helper.store_docker(file_path)
        # if store worked -> create database
        if success:
            success, message = self.database_helper.save_docker_container(extract_path, name, size)
        return success, message

    def results_available(self, path):
        return self.database_helper.check_results_exist(path)

    def get_result_score(self,path):
        return self.database_helper.get_result_score(path)

    def run_tests_for_container(self):
        # Implementation for running tests for a container
        pass

    def exit(self):
        pass

    # Add more methods as needed


##    def showTransformationGraphs(self):
##
##        # Lösche alle vorhandenen Graphen-Widgets
##        for graph_frame in self.graph_frames:
##            graph_frame.grid_forget()
##            graph_frame.destroy()
##        self.graph_frames = []
##
##        # Lade und zeige die Graphen für jede Zeile in der "transformations.txt"
##        transformations = self.transformations_helper.get_available_transformations()
##        num_columns = math.floor(self.window.winfo_width() / 200)  # Anzahl der Spalten basierend auf der Fensterbreite
##        num_rows = math.ceil(len(transformations) / num_columns)  # Anzahl der Zeilen basierend auf der Anzahl der Graphen
##
##        # Read the transformation names from the transformations.txt file
##        with open('transformations.txt', 'r') as file:
##            transformation_names = file.readlines()
##
##        # Erzeuge und zeige die Graphen-Widgets mit Beschriftungen
##        for i, transformation in enumerate(transformations):
##            graph_frame = tk.Frame(self.window, width=200, height=150, borderwidth=1, relief=tk.SOLID)
##            graph_frame.grid(row=(i // num_columns) + 3, column=i % num_columns, padx=10, pady=10)
##            self.graph_frames.append(graph_frame)
##
##            # Label the box with the transformation name
##            transformation_name = transformation_names[i].strip()  # Get the transformation name for the current box
##            label = tk.Label(self.window, text=transformation_name)
##            label.grid(row=(i // num_columns) + 2, column=i % num_columns, padx=10, pady=5)
##
##            # Hier kannst du den Code zum Erstellen und Anzeigen des Graphen einfügen
##            # Verwende graph_frame als Eltern-Widget für die Graphen-Elemente
