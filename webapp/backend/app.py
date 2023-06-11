import base64

from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS from flask_cors
from controller import Controller

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes -> to prevent same origin error

controller = Controller()


@app.route('/api/docker-containers', methods=['GET'])
def get_docker_containers():
    docker_list = controller.load_docker_containers()
    return jsonify(docker_list)


@app.route('/api/add-docker-container', methods=['POST'])
def add_docker_container():
    tar_path = controller.save_user_tar(request.files['file'])
    container_name = request.form['name']

    success, message = controller.store_container(tar_path, container_name)
    print("Registration: " + message)
    if success:
        return jsonify({'message': 'Docker container added successfully'})
    else:
        return jsonify({'message': message}), 400


@app.route('/api/load-container-results', methods=['POST'])
def load_container_results():
    container_id = request.json.get('container')
    print(container_id)
    results = controller.load_container_results(container_id)
    return jsonify(results)


@app.route('/api/transform-images', methods=['POST'])
def transform_images():
    transformations = request.json.get('transformations')
    container_name = request.json.get('container_name')

    data_url = request.json.get('image_path')

    # Save data url to actual file on server
    image_path = controller.save_test_image(data_url, container_name)

    print("testimage:" + str(image_path))

    print(transformations)
    success = controller.transform_images(container_name, image_path, transformations)

    return jsonify(str(success))


@app.route('/api/build-docker', methods=['POST'])
def build_docker():
    container_name = request.json.get('container_name')
    controller.build_docker(container_name)
    return "yet to implement"


@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    container_name = request.json.get('container_name')
    controller.run_tests(container_name)

    return "testmethod yet to implement"


@app.route('/api/available-transformations', methods=['GET'])
def get_available_transformations():
    transformations = controller.get_available_transformations()
    return jsonify(transformations)


if __name__ == '__main__':
    app.run()
