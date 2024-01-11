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

    cursor.execute(f"INSERT INTO addresses (name, lat, lon) VALUES ('{name}', '{lat}', {lon}) RETURNING id")
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

    route_id_sql = f"SELECT id, ride_time FROM routes WHERE courier_id = {courier_id} and complete = false"
    cursor.execute(route_id_sql)
    result = cursor.fetchall()
    routes = {}
    for row in result:
        routes[row[0]] = {
            'courier_id': courier_id,
            'ride_time': row[1],
            'orders': []
        }

    cursor.execute(f"SELECT id, user_id, address_id, route_id FROM orders "
                   f"WHERE route_id IN (SELECT id FROM routes WHERE courier_id = {courier_id} and complete = false)")
    result = cursor.fetchall()
    for row in result:
        routes[row[4]]['orders'].append({
            'order_id': row[0],
            'user_id': row[1],
            'address_id': row[2],
            'route_id': row[3]
        })

    cursor.close()

    return routes


def save_route(courier_id, coords, order_dict, ride_time='1 hour'):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO routes (courier_id, ride_time) VALUES ({courier_id}, '{ride_time}') RETURNING id")
    route_id = cursor.fetchone()[0]
    for coord in coords:
        cursor.execute(f"UPDATE orders SET route_id = {route_id} WHERE id = {order_dict[coord]}")
    cursor.connection.commit()

    cursor.close()


def save_routes(routes, order_dict):
    cursor = make_connection()

    for courier_name, coords in routes.items():
        cursor.execute(f"SELECT id FROM users WHERE username = '{courier_name}'")
        result = cursor.fetchall()

        if len(result) == 0:
            raise Exception(f"Courier {courier_name} not found")

        courier_id = result[0][0]
        save_route(courier_id, coords, order_dict)

    cursor.close()


def get_active_orders(user_id=None):
    cursor = make_connection()

    order_sql = (f"SELECT orders.id, address_id, route_id FROM orders "
                 f"JOIN routes ON orders.route_id = routes.id "
                 f"WHERE complete = false ")

    if user_id is not None:
        order_sql += f"AND user_id = {user_id}"

    cursor.execute(order_sql)
    result = cursor.fetchall()
    orders = []
    for row in result:
        orders.append({
            'order_id': row[0],
            'address_id': row[1],
            'route_id': row[2]
        })

    cursor.close()

    return orders


def add_order(user_id, address_id):
    cursor = make_connection()

    cursor.execute(f"INSERT INTO orders (user_id, address_id) VALUES ({user_id}, {address_id})")
    cursor.connection.commit()

    cursor.close()
