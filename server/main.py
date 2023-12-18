from flask import Flask, jsonify, request
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/api', methods=['GET'])
def get_data():
    # Logic to fetch data goes here
    data = {'message': 'Hello, World!'}
    return jsonify(data)

@app.route('/api', methods=['POST'])
def post_data():
    # Logic to handle POST requests goes here
    data = request.get_json()
    # Process the data and return a response
    response = {'message': 'Data received successfully'}
    return jsonify(response)

if __name__ == '__main__':
    app.run()