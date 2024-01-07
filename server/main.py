import requests
import time
import numpy as np

from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
from geopy.distance import geodesic
from sklearn.cluster import KMeans
from python_tsp.exact import solve_tsp_dynamic_programming
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
address_cache = {}

@app.route('/', methods=['GET'])
def home():
    return redirect("https://youtu.be/dQw4w9WgXcQ?si=s5egZJ1Kr7_xkytG", code=302)

@app.route('/api', methods=['GET'])
def get_data():
    # Logic to fetch data goes here
    #data = {'message': 'U sure u wanna GET? I dont think so bud :)'}
    #return jsonify(data)
    return redirect("https://youtu.be/dQw4w9WgXcQ?si=s5egZJ1Kr7_xkytG", code=302)

@app.route('/api', methods=['POST'])
def post_data():
    # Logic to handle POST requests goes here
    data = request.get_json()
    address_list = data.get('addresses', [])
    warehouse = data.get('warehouse', None)[0]
    courier_list = data.get('couriers', [])

    # Translate addresses to coordinates
    coordinates = []
    for address in address_list:
        try:
            coordinates.append(get_address(address))
        except Exception as e:
            return e.args[0], 500
        
    try:
        warehouseLocation = get_address(warehouse)
    except Exception as e:
        return e.args[0], 500


    # Calculate distances between points
    #distances = []
    #for i in range(len(coordinates)):
    #    for j in range(i+1, len(coordinates)):
    #        start = coordinates[i]
    #        end = coordinates[j]
    #        distance = geodesic(start, end).m
    #        distances.append([i,distance])

    # Use KMeans to make clusters
    kmeans = KMeans(n_clusters=len(courier_list), n_init=10)
    kmeans.fit(coordinates)
    
    # Create a dictionary where the keys are the courier names and the values are the coordinates of points assigned to that courier
    courier_dict = {}
    for i in range(len(kmeans.labels_)):
        courier = courier_list[kmeans.labels_[i]]
        if courier not in courier_dict:
            courier_dict[courier] = [coordinates[i]]
            courier_dict[courier].append(warehouseLocation)
        else:
            courier_dict[courier].append(coordinates[i])

    routes = {}
    # solve tsp for each courier
    for courier in courier_dict:
        # create distance matrix for tsp
        distances = []
        for i in range(len(courier_dict[courier])):
            distances.append([])
            for j in range(len(courier_dict[courier])):
                start = courier_dict[courier][i]
                end = courier_dict[courier][j]
                distance = geodesic(start, end).m
                distances[i].append(distance)
        # solve tsp
        path = solve_tsp_dynamic_programming(np.array(distances))
        # create route
        routes[courier] = []
        for i in range(len(path[0])):
            routes[courier].append(courier_dict[courier][path[0][i]])

    # Process the data and return a response
    response = format_routes(routes)
    return jsonify(response)


def get_address(address):
    if address in address_cache:
        return address_cache[str(address)]
    
    response = requests.get(f'https://geocode.maps.co/search?q={address}&api_key=658d4f89d6a8f549657909ovw64c95d')

    if response.status_code == 200:
        try:
            result = response.json()
            lat = result[0]['lat']
            lon = result[0]['lon']
            print(f'[Address: {address}] Latitude: {lat}, Longitude: {lon}')
        except Exception as e:
            raise Exception(f'Error fetching address: {address}!')
        
        address_cache[str(address)] = (lat, lon)
        time.sleep(1)

        return lat, lon
    else:
        raise Exception(f'Error fetching address: {address}!')
    

def format_routes(routes):
    formatted_routes = {}
    for courier, route in routes.items():
        formatted_markers = []
        # TODO: Add proper paths between markers. Currently, it's just a straight line
        formatted_lines = [] # lines between markers

        for coordinate in route:
            formatted_markers.append({'lat': coordinate[0], 'lon': coordinate[1]})
            formatted_lines.append({'lat': coordinate[0], 'lon': coordinate[1]})
        formatted_lines.append({'lat': route[0][0], 'lon': route[0][1]})

        formatted_routes[courier] = {
            'markers': formatted_markers, 
            'lines': formatted_lines
        }

    return formatted_routes


if __name__ == '__main__':
    app.run()