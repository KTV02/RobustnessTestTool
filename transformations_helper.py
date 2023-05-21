class TransformationsHelper:
    def __init__(self, transformations_file):
        self.transformations_file = transformations_file

    def get_available_transformations(self):
        with open(self.transformations_file, "r") as file:
            transformations = file.read().splitlines()
        return transformations
