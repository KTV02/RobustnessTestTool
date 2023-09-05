import base64
import time

from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS from flask_cors
from controller import Controller
import traceback

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes -> to prevent same origin error

controller = Controller()


@app.route('/api/get-docker-containers', methods=['GET'])
def get_docker_containers():
    docker_list = controller.load_docker_containers()
    return jsonify(docker_list)


@app.route('/api/delete-docker-container', methods=['DELETE'])
def delete_docker_container():
    container = request.json.get('container')
    print("Container to be deleted: " + str(container))
    success = controller.delete_docker_container(container)
    return jsonify(success)


@app.route('/api/add-docker-container', methods=['PUT'])
def add_docker_container():
    container_name = request.json.get('name')
    print("Container name:"+str(container_name))
    try:
        success, message,size = controller.store_container(container_name)
    except FileNotFoundError as e:
        return jsonify(str(e))

    print("Registration: " + message)
    if success:
        return jsonify({'message': 'Docker container added successfully. Size of model: ' + str(size) + ' bytes'})
    else:
        return jsonify({'message': message}), 400


@app.route('/api/add-docker-container-frontend', methods=['PUT'])
def add_docker_container_frontend():
    container_name = request.form['container_name']
    tar_path = request.files['tarfile']

    success, message, size = controller.store_container_frontend(tar_path, container_name)
    if success:
        return jsonify({'message': 'Docker container added successfully. Size of model: ' + str(size) + ' bytes'})
    else:
        return jsonify({'message': message}), 400


@app.route('/api/set-ground-truth', methods=['PUT'])
def add_ground_truth():
    try:
        controller.add_images(request.json.get('container'), "solutions/")
    except FileNotFoundError as error:
        return str(error)

    return jsonify("success")


@app.route('/api/set-test-images', methods=['PUT'])
def add_test_images():
    try:
        controller.add_images(request.json.get('container'), "transformations/")
    except FileNotFoundError as error:
        return str(error)

    return jsonify("success")


@app.route('/api/load-container-results', methods=['POST'])
def load_container_results():
    container = request.json.get('container')
    print("Container selected: " + str(container))
    result = controller.load_container_results(container)
    print("result is:")
    print(result)
    return jsonify(result)


@app.route('/api/transform-images', methods=['POST'])
def transform_images():
    transformations = request.json.get('transformations')
    container_name = request.json.get('container_name')

    try:
        success = controller.transform_images(container_name, transformations)
    except OSError as e:
        print(f"Caught an exception: {e}")
        traceback.print_exc()
        return jsonify("An Eception occurred: " + str(e))

    return jsonify(str(success))


@app.route('/api/build-docker', methods=['POST'])
def build_docker():
    container_name = request.json.get('container_name')
    controller.build_docker(container_name)
    return "yet to implement"


@app.route('/api/image-exists', methods=['POST'])
def image_exists():
    container_name = request.json.get('container_name')
    if controller.image_exists(container_name):
        # image already exists, no need to load from tar
        return jsonify("True")
    else:
        return jsonify("False")


@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    container_name = request.json.get('container_name')
    success = controller.run_tests(container_name)
    print(success)

    return jsonify(str(success))


@app.route('/api/evaluate-results', methods=['POST'])
def evaluate_results():
    container_name = request.json.get('container_name')
    success, data = controller.evaluate_results(container_name)

    # Prepare the response JSON
    response = {
        "success": success,
        "data": data
    }

    # Return the response as JSON
    return jsonify(response)


@app.route('/api/available-transformations', methods=['GET'])
def get_available_transformations():
    transformations = controller.get_available_transformations()
    return jsonify(transformations)


if __name__ == '__main__':
    app.run()
