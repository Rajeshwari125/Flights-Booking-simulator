from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('flights.db')
    conn.row_factory = sqlite3.Row
    return conn

# Endpoint to retrieve all flights
@app.route('/flights', methods=['GET'])
def get_flights():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM flights')
    flights = cursor.fetchall()
    conn.close()
    
    flights_list = [dict(flight) for flight in flights]
    return jsonify(flights_list)

# Endpoint to search flights by origin, destination, and date
@app.route('/search', methods=['GET'])
def search_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')
    
    query = 'SELECT * FROM flights WHERE origin = ? AND destination = ? AND times LIKE ?'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (origin, destination, f"%{date}%"))
    flights = cursor.fetchall()
    conn.close()
    
    flights_list = [dict(flight) for flight in flights]
    return jsonify(flights_list)

# Endpoint to sort flights by price or duration
@app.route('/sort', methods=['GET'])
def sort_flights():
    sort_by = request.args.get('sort_by', 'price')  # Default to price
    order = request.args.get('order', 'asc')  # Default to ascending order
    
    if sort_by not in ['price', 'times']:
        return jsonify({'error': 'Invalid sort field'}), 400
    if order not in ['asc', 'desc']:
        return jsonify({'error': 'Invalid sort order'}), 400
    
    query = f'SELECT * FROM flights ORDER BY {sort_by} {order}'
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    flights = cursor.fetchall()
    conn.close()
    
    flights_list = [dict(flight) for flight in flights]
    return jsonify(flights_list)

if __name__ == '__main__':
    app.run(debug=True)