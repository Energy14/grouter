import psycopg2
from db import credentials


def make_connection():
    con = psycopg2.connect(database=credentials.database,
                           user=credentials.user,
                           password=credentials.password,
                           host=credentials.host, port="5432")
    return con.cursor()


def get_addresses():
    cursor = make_connection()

    cursor.execute("SELECT name, lat, lon FROM addresses")
    result = cursor.fetchall()
    addresses = {}
    for row in result:
        addresses[row[0]] = (row[1], row[2])

    cursor.close()

    return addresses


def add_address(name, lat, lon):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO addresses (name, lat, lon) VALUES ('{name}', '{lat}', {lon}) "
                   f"ON CONFLICT (name) DO UPDATE SET lat = '{lat}', lon = {lon} "
                   f"RETURNING id")
    address_id = cursor.fetchone()[0]
    cursor.connection.commit()

    cursor.close()

    return address_id


def update_addresses(addresses):
    for name, (lat, lon) in addresses.items():
        add_address(name, lat, lon)


def get_user(username):
    cursor = make_connection()

    cursor.execute(f"SELECT id, role, date_created, pass_hash FROM users where username = '{username}'")
    result = cursor.fetchall()

    if len(result) == 0:
        return None

    cursor.close()

    return {
        'id': result[0][0],
        'username': username,
        'role': result[0][1],
        'date_created': result[0][2],
        'pass_hash': result[0][3]
    }


def get_couriers():
    cursor = make_connection()

    cursor.execute("SELECT id, username, role, date_created, pass_hash FROM users where role = 'courier'")
    result = cursor.fetchall()
    couriers = {}
    for row in result:
        couriers[row[0]] = {
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'date_created': row[3],
            'pass_hash': row[4]
        }

    cursor.close()

    return couriers


def add_user(username, pass_hash, role):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO users (username, role, pass_hash) VALUES ('{username}', '{role}', '{pass_hash}')")
    cursor.connection.commit()

    cursor.close()


def get_active_routes(courier_id):
    cursor = make_connection()

    route_id_sql = f"SELECT id, distance, ride_time FROM routes WHERE courier_id = {courier_id} and complete = false"
    cursor.execute(route_id_sql)
    result = cursor.fetchall()
    routes = {}
    for row in result:
        routes[row[0]] = {
            'id': row[0],
            'courier_id': courier_id,
            'distance': row[1],
            'ride_time': row[2],
            'orders': []
        }

    cursor.execute(f"SELECT id, user_id, address_id, route_id FROM orders "
                   f"WHERE route_id IN (SELECT id FROM routes WHERE courier_id = {courier_id} and complete = false)")
    result = cursor.fetchall()
    for row in result:
        routes[row[3]]['orders'].append({
            'id': row[0],
            'user_id': row[1],
            'address_id': row[2]
        })

    cursor.close()

    return routes


def get_order_route(order_id):
    cursor = make_connection()

    cursor.execute(f"SELECT route_id FROM orders "
                   f"WHERE orders.id = {order_id}")
    result = cursor.fetchall()
    route_id = result[0][0]

    cursor.close()

    return route_id


def save_route(courier_id, coords, order_dict, distance=0, ride_time='1 hour'):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO routes (courier_id, distance, ride_time) "
                   f"VALUES ({courier_id}, {distance}, '{ride_time}') "
                   f"RETURNING id")
    route_id = cursor.fetchone()[0]
    cursor.connection.commit()

    for coord in coords:
        order_id = order_dict.get(coord, None)
        if order_id is not None:
            cursor.execute(f"UPDATE orders SET route_id = {route_id} WHERE id = {order_id}")
        else:
            address_id = add_address(f"warehouse_{route_id}", coord[0], coord[1])
            cursor.execute(f"INSERT INTO orders (user_id, route_id, address_id) VALUES ({courier_id}, {route_id}, {address_id})")
    cursor.connection.commit()

    cursor.close()


def save_routes(routes, order_dict, distances, durations):
    cursor = make_connection()

    for courier_name, coords in routes.items():
        cursor.execute(f"SELECT id FROM users WHERE username = '{courier_name}'")
        result = cursor.fetchall()

        if len(result) == 0:
            raise Exception(f"Courier {courier_name} not found")

        courier_id = result[0][0]
        save_route(courier_id, coords, order_dict, distances[courier_name], durations[courier_name])

    cursor.close()


def get_route(route_id):
    cursor = make_connection()

    cursor.execute(f"SELECT id, courier_id, distance, ride_time, complete FROM routes WHERE id = {route_id}")
    result = cursor.fetchall()
    route = {
        'id': result[0][0],
        'courier_id': result[0][1],
        'distance': result[0][2],
        'ride_time': result[0][3],
        'complete': result[0][4],
        'orders': [],
    }

    cursor.execute(f"SELECT orders.id, user_id, address_id, route_id, lat, lon FROM orders "
                   f"JOIN public.addresses a on a.id = orders.address_id "
                   f"WHERE route_id = {route_id}")
    result = cursor.fetchall()

    route['orders'] = []
    for row in result:
        route['orders'].append({
            'order_id': row[0],
            'user_id': row[1],
            'address_id': row[2],
            'route_id': row[3],
            'coordinates': (row[4], row[5])
        })

    cursor.close()

    return route


def get_active_orders(user_id=None):
    cursor = make_connection()

    order_sql = (f"SELECT orders.id, address_id, route_id, addresses.name FROM orders "
                 f"LEFT JOIN routes ON orders.route_id = routes.id "
                 f"JOIN addresses ON orders.address_id = addresses.id ")

    if user_id is None:
        order_sql += f"WHERE route_id IS NULL "
    else:
        order_sql += f"WHERE route_id IS NOT NULL AND complete = false AND user_id = {user_id}"

    cursor.execute(order_sql)
    result = cursor.fetchall()
    orders = []
    for row in result:
        orders.append({
            'id': row[0],
            'address_id': row[1],
            'route_id': row[2],
            'address': row[3]
        })

    cursor.close()

    return orders


def add_order(user_id, address_id):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO orders (user_id, address_id) VALUES ({user_id}, {address_id})")
    cursor.connection.commit()

    cursor.close()
