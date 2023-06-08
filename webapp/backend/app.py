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
    tar_path=controller.save_user_tar(request.files['file'])
    container_name = request.form['name']

    success, message = controller.store_container(tar_path,container_name)
    if success:
        return jsonify({'message': 'Docker container added successfully'})
    else:
        return jsonify({'message': message}), 400

@app.route('/api/run-tests', methods=['POST'])
def run_tests():
    image_path = request.json.get('image_path')
    transformations = request.json.get('transformations')
    container_name = request.json.get('container_name')
    print(transformations)
    success = controller.run_tests_for_container(container_name,image_path, transformations)

    return str(success)

@app.route('/api/available-transformations', methods=['GET'])
def get_available_transformations():
    transformations = controller.get_available_transformations()
    return jsonify(transformations)

if __name__ == '__main__':
    app.run()
