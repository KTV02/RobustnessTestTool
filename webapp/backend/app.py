from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS from flask_cors
from controller import Controller
from database_helper import DatabaseHelper
from transformations_helper import TransformationsHelper
from files_helper import FilesHelper

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes -> to prevent same origin error

controller = Controller(DatabaseHelper("./storage/results.db"), TransformationsHelper("./storage/transformations.txt"), FilesHelper())

@app.route('/api/docker-containers', methods=['GET'])
def get_docker_containers():
    docker_list = controller.load_docker_containers()
    return jsonify(docker_list)

@app.route('/api/add-docker-container', methods=['POST'])
def add_docker_container():
    selected_file = request.files['file']
    container_name = request.form['name']
    success, message = controller.store_container(selected_file, container_name)
    if success:
        return jsonify({'message': 'Docker container added successfully'})
    else:
        return jsonify({'message': message}), 400

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    selected_container = request.json['container']
    controller.run_tests_for_container(selected_container)
    score = controller.get_result_score(selected_container)
    # Retrieve other necessary data for the response
    return jsonify({'score': score})

if __name__ == '__main__':
    app.run()
