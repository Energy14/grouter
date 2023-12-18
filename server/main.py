import requests

from flask import Flask, jsonify, request
from flask_cors import CORS
from geopy.distance import geodesic
from sklearn.cluster import KMeans
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
    address_list = data.get('addresses', [])
    courier_list = data.get('couriers', [])

    # Translate addresses to coordinates
    coordinates = []
    for address in address_list:
        response = requests.get(f'https://geocode.maps.co/search?q={address}')

        if response.status_code == 200:
            result = response.json()
            lat = result[0]['lat']
            lon = result[0]['lon']
            print(f'Latitude: {lat}, Longitude: {lon}')
            
            coordinates.append((lat, lon))

    # Calculate distances between points
    distances = []
    for i in range(len(coordinates)):
        for j in range(i+1, len(coordinates)):
            start = coordinates[i]
            end = coordinates[j]
            distance = geodesic(start, end).m
            distances.append([i,distance])
    print(distances)

    # Use KMeans to make clusters
    kmeans = KMeans(n_clusters=len(courier_list))
    kmeans.fit(coordinates)
    print(kmeans.labels_)
    
    # Create a dictionary where the keys are the courier names and the values are the coordinates of points assigned to that courier
    courier_dict = {}
    for i in range(len(kmeans.labels_)):
        courier = courier_list[kmeans.labels_[i]]
        if courier not in courier_dict:
            courier_dict[courier] = [coordinates[i]]
        else:
            courier_dict[courier].append(coordinates[i])
    print(courier_dict)
    # Process the data and return a response
    response = {'message': 'Data received successfully', 'coordinates': coordinates, 'distances': distances, 'courier_dict': courier_dict}
    return jsonify(response)
    
if __name__ == '__main__':
    app.run()