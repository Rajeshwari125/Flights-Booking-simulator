# app.py
from flask import Flask, request, jsonify
import sqlite3
from pricing import compute_dynamic_price_from_record
from datetime import datetime

DB_PATH = 'flights.db'
app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def record_fare_history(conn, flight_id, computed_fare, seats_available, demand_index):
    try:
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS fare_history (id INTEGER PRIMARY KEY AUTOINCREMENT, flight_id INTEGER, timestamp TEXT, computed_fare REAL, seats_available INTEGER, demand_index REAL)'
        )
        cur.execute(
            'INSERT INTO fare_history (flight_id, timestamp, computed_fare, seats_available, demand_index) VALUES (?, datetime("now"), ?, ?, ?)',
            (flight_id, computed_fare, seats_available, demand_index)
        )
        conn.commit()
    except Exception as e:
        # don't crash the API if recording fails; log in real app
        print("fare_history write error:", e)

@app.route('/flights', methods=['GET'])
def get_flights():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM flights')
    rows = cur.fetchall()

    flights = []
    for row in rows:
        rec = dict(row)
        dynamic_price = compute_dynamic_price_from_record(rec)
        rec['dynamic_price'] = dynamic_price
        flights.append(rec)
        # Optional: record fare_history (comment out if too chatty)
        try:
            record_fare_history(conn, rec.get('id'), dynamic_price, rec.get('seats_available'), rec.get('demand_index'))
        except Exception:
            pass

    conn.close()
    return jsonify(flights)

@app.route('/search', methods=['GET'])
def search_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    date = request.args.get('date')  # used for matching the times/departure_time string

    if not origin or not destination:
        return jsonify({'error': 'origin and destination are required'}), 400

    # simple search - matches origin, destination, and times includes date substring
    query = 'SELECT * FROM flights WHERE origin = ? AND destination = ?'
    params = [origin, destination]
    if date:
        query += ' AND (departure_time LIKE ? OR times LIKE ?)'
        params.extend([f"%{date}%", f"%{date}%"])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()

    flights = []
    for row in rows:
        rec = dict(row)
        rec['dynamic_price'] = compute_dynamic_price_from_record(rec)
        flights.append(rec)
    conn.close()
    return jsonify(flights)

@app.route('/sort', methods=['GET'])
def sort_flights():
    sort_by = request.args.get('sort_by', 'price')  # we will compute dynamic_price but allow sorting by base fields
    order = request.args.get('order', 'asc')
    if sort_by not in ['price', 'base_fare', 'times', 'departure_time']:
        return jsonify({'error': 'Invalid sort field'}), 400
    if order not in ['asc', 'desc']:
        return jsonify({'error': 'Invalid sort order'}), 400

    query = f'SELECT * FROM flights ORDER BY {sort_by} {order}'
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()

    flights = []
    for row in rows:
        rec = dict(row)
        rec['dynamic_price'] = compute_dynamic_price_from_record(rec)
        flights.append(rec)
    conn.close()
    return jsonify(flights)

if __name__ == '__main__':
    app.run(debug=True)
