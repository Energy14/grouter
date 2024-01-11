import traceback

import requests
import time
import numpy as np

from flask import Flask, jsonify, render_template, request, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from geopy.distance import geodesic
from sklearn.cluster import KMeans
from python_tsp.exact import solve_tsp_dynamic_programming

from db import db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
address_cache = {}
bcrypt = Bcrypt(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    return redirect("/login", code=302)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "register" in request.form:
        return redirect("/register", code=302)
    if "login" in request.form:
        return redirect_by_role()
    return render_template('login_view.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if "login" in request.form:
        return redirect("/login", code=302)
    if "register" in request.form:
        if not has_required_fields(request.form, ['username', 'password', 'confirm', 'role']):
            return render_template('register_view.html', message='Please fill in all fields')

        if request.form['password'] != request.form['confirm']:
            return render_template('register_view.html', message='Passwords do not match')

        pass_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        username = request.form['username']

        try:
            db.add_user(username, pass_hash, request.form['role'])
        except:
            return render_template('register_view.html', message=f'Username {username} already in use')

        return redirect_by_role()

    return render_template('register_view.html')


def has_required_fields(form, fields):
    for field in fields:
        if field not in form:
            return False

    return True


@app.route('/admin', methods=['GET', 'POST'])
def admin_view():
    if request.method == 'GET':
        return redirect("/login", code=303)

    user = check_auth()
    if user is None or user['role'] != 'admin':
        return redirect("/login", code=303)

    active_orders = db.get_active_orders()
    formatted_order_addresses = []
    for order in active_orders:
        formatted_order_addresses.append((str(order['id']), order['address']))

    couriers = db.get_couriers()
    formatted_couriers = []
    for courier in couriers.values():
        formatted_couriers.append((str(courier['id']), courier['username']))

    return render_template('admin_view.html',
                           serverHost=request.environ['HTTP_HOST'],
                           active_order_addresses=formatted_order_addresses,
                           couriers=formatted_couriers)


@app.route('/courier', methods=['GET', 'POST'])
def courier_view():
    if request.method == 'GET':
        return redirect("/login", code=303)

    user = check_auth()
    if user is None or user['role'] != 'courier':
        return redirect("/login", code=303)

    active_routes = db.get_active_routes(user['id'])
    formatted_routes = []
    for route in active_routes.values():
        formatted_routes.append((str(route['id']), route['distance'], route['ride_time']))

    return render_template('courier_view.html',
                           serverHost=request.environ['HTTP_HOST'],
                           active_routes=formatted_routes,
                           **user)


@app.route('/user', methods=['GET', 'POST'])
def user_view():
    if request.method == 'GET':
        return redirect("/login", code=303)

    user = check_auth()
    if user is None or user['role'] != 'user':
        return redirect("/login", code=303)

    active_orders = db.get_active_orders(user['id'])
    formatted_order_addresses = []
    for order in active_orders:
        formatted_order_addresses.append((str(order['id']), order['address']))

    return render_template('user_view.html',
                           serverHost=request.environ['HTTP_HOST'],
                           active_orders=formatted_order_addresses,
                           user_id=user['id'], )


@app.route('/api', methods=['GET'])
def get_data():
    # Logic to fetch data goes here
    # data = {'message': 'U sure u wanna GET? I dont think so bud :)'}
    # return jsonify(data)
    return redirect("https://youtu.be/dQw4w9WgXcQ?si=s5egZJ1Kr7_xkytG", code=302)


@app.route('/api/admin', methods=['POST'])
def post_data():
    # Logic to handle POST requests goes here
    data = request.get_json()

    address_list = data.get('addresses', [])
    warehouse = data.get('warehouse', None)[0]
    courier_list = data.get('couriers', [])

    # Discard courier ids
    courier_name_list = []
    for courier in courier_list:
        courier_name_list.append(courier[0])

    # Translate addresses to coordinates
    coordinates = []
    order_dict = {}

    for address, order_id in address_list:
        try:
            coords = get_coordinates(address)
            coordinates.append(coords)
            order_dict[coords] = order_id
        except Exception as e:
            return e.args[0], 500

    try:
        warehouseLocation = get_coordinates(warehouse)
    except Exception as e:
        return e.args[0], 500

    # Calculate distances between points
    # distances = []
    # for i in range(len(coordinates)):
    #    for j in range(i+1, len(coordinates)):
    #        start = coordinates[i]
    #        end = coordinates[j]
    #        distance = geodesic(start, end).m
    #        distances.append([i,distance])

    # Use KMeans to make clusters
    kmeans = KMeans(n_clusters=len(courier_name_list), n_init=10)
    kmeans.fit(coordinates)

    # Create a dictionary where the keys are the courier names and the values are the coordinates of points assigned to that courier
    courier_dict = {}
    for i in range(len(kmeans.labels_)):
        courier = courier_name_list[kmeans.labels_[i]]
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

    # Process the data
    formatted_routes, distances, durations = format_routes(routes)

    # Save the routes to the database
    try:
        db.save_routes(routes, order_dict, distances, durations)
    except Exception as e:
        return e.args[0], 500

    return jsonify(formatted_routes)


@app.route('/api/user/save-order', methods=['POST'])
def save_order():
    data = request.get_json()

    address_names = data.get('address', None)
    user_id = data.get('user_id', None)

    if user_id is None:
        return f'Missing required field {user_id}', 500
    if address_names is None:
        return f'Missing required field {address_names}', 500

    for address_name in address_names:
        try:
            address = get_coordinates(address_name)
        except Exception as e:
            return e.args[0], 500

        try:
            address_id = db.add_address(address_name, address[0], address[1])
            db.add_order(user_id, address_id)
        except Exception as e:
            return e.args[0], 500

    return jsonify({'message': 'success'}), 200


@app.route('/api/user/find-order-route', methods=['POST'])
def find_order_route():
    data = request.get_json()

    address_name, order_id = data.get('order', None)[0]

    if order_id is None:
        return f'Missing required field {order_id}', 500

    try:
        route_id = db.get_order_route(order_id)
    except Exception as e:
        return e.args[0], 500

    if route_id is None:
        return f'Route with order [{order_id}] not found', 500

    try:
        route = db.get_route(route_id)
    except Exception as e:
        return e.args[0], 500

    coordinates = []
    for order in route['orders']:
        coordinates.append(order['coordinates'])

    formatted_route = format_routes({route['id']: coordinates})[0]

    return jsonify(formatted_route), 200


@app.route('/api/courier/find-route', methods=['POST'])
def find_route():
    data = request.get_json()

    packed_route = data.get('route', None)[0]

    if packed_route is None:
        return f'Missing required field route', 500

    route_time, route_id = packed_route

    try:
        route = db.get_route(route_id)
    except Exception as e:
        return e.args[0], 500

    coordinates = []
    for order in route['orders']:
        coordinates.append(order['coordinates'])

    formatted_route = format_routes({route['id']: coordinates})[0]

    return jsonify(formatted_route), 200


def get_coordinates(address):
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
    distances = {}
    durations = {}

    for courier, route in routes.items():
        formatted_markers = []
        formatted_lines = []  # lines between markers
        distance = 0
        duration = 0

        for coordinate in route:
            formatted_markers.append({'lat': coordinate[0], 'lon': coordinate[1]})

        for i in range(len(route) - 1):
            response = requests.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                params={
                    "travelMode": "WALKING",
                    "mode": "walking",
                    "units": "METRIC",
                    "origin": f"{route[i][0]},{route[i][1]}",
                    "destination": f"{route[i + 1][0]},{route[i + 1][1]}",
                    "key": "AIzaSyCyVKM3YSZsfnbIUlUDSuPshLM5e8mWzh4"
                }
            )

            for step in response.json()['routes'][0]['legs'][0]['steps']:
                start = step['start_location']
                end = step['end_location']
                formatted_lines.append({'lat': start['lat'], 'lon': start['lng']})
                formatted_lines.append({'lat': end['lat'], 'lon': end['lng']})

            for leg in response.json()['routes'][0]['legs']:
                distance += leg['distance']['value']
                duration += leg['duration']['value']

        response = requests.get(
            "https://maps.googleapis.com/maps/api/directions/json",
            params={
                "travelMode": "WALKING",
                "mode": "walking",
                "units": "METRIC",
                "origin": f"{route[-1][0]},{route[-1][1]}",
                "destination": f"{route[0][0]},{route[0][1]}",
                "key": "AIzaSyCyVKM3YSZsfnbIUlUDSuPshLM5e8mWzh4"
            }
        )
        for step in response.json()['routes'][0]['legs'][0]['steps']:
            start = step['start_location']
            end = step['end_location']
            formatted_lines.append({'lat': start['lat'], 'lon': start['lng']})
            formatted_lines.append({'lat': end['lat'], 'lon': end['lng']})

        for leg in response.json()['routes'][0]['legs']:
            distance += leg['distance']['value']
            duration += leg['duration']['value']

        formatted_routes[courier] = {
            'markers': formatted_markers,
            'lines': formatted_lines
        }

        distances[courier] = distance
        durations[courier] = duration

    return formatted_routes, distances, durations


def redirect_by_role():
    user = check_auth()

    if user is None:
        return redirect("/login", code=303)
    elif user['role'] == 'courier':
        return redirect("/courier", code=307)
    elif user['role'] == 'admin':
        return redirect("/admin", code=307)
    elif user['role'] == 'user':
        return redirect("/user", code=307)
    else:
        return redirect("/login", code=303)


def check_auth(username=None, password=None):
    if username is None:
        if 'username' not in request.form:
            return None
        username = request.form['username']

    if password is None:
        if 'password' not in request.form:
            return None
        password = request.form['password']

    try:
        user = db.get_user(username)
    except:
        return None

    if user is None:
        return None

    if not bcrypt.check_password_hash(user['pass_hash'], password):
        return None

    return user


def update_address_cache():
    print('Updating address cache')
    db.update_addresses(address_cache)

    db_addresses = db.get_addresses()
    address_cache.update(db_addresses)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_address_cache, trigger="interval", seconds=300)
    scheduler.start()

    update_address_cache()

    app.run()
