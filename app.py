from flask import Flask, request, jsonify
import sqlite3
import uuid
from datetime import datetime
import random

app = Flask(__name__)

def get_db():
    return sqlite3.connect("flights.db")

@app.route("/book", methods=["POST"])
def book_flight():
    data = request.json

    flight_id = data.get("flight_id")
    passenger_name = data.get("passenger_name")
    seats = data.get("seats", 1)

    if not flight_id or not passenger_name:
        return jsonify({"error": "Invalid input"}), 400

    # Simulated payment
    payment_status = random.choice(["success", "fail"])
    if payment_status == "fail":
        return jsonify({"error": "Payment failed"}), 400

    conn = get_db()
    cur = conn.cursor()

    try:
        conn.execute("BEGIN")

        cur.execute(
            "SELECT seats_available, price FROM flights WHERE id=?",
            (flight_id,)
        )
        flight = cur.fetchone()

        if not flight:
            conn.rollback()
            return jsonify({"error": "Flight not found"}), 404

        if flight[0] < seats:
            conn.rollback()
            return jsonify({"error": "Not enough seats"}), 400

        final_price = flight[1] * seats
        pnr = str(uuid.uuid4())[:8].upper()

        cur.execute("""
            INSERT INTO bookings
            (flight_id, passenger_name, seats_booked, final_price, status, pnr, booking_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            flight_id,
            passenger_name,
            seats,
            final_price,
            "CONFIRMED",
            pnr,
            datetime.now().isoformat()
        ))

        cur.execute("""
            UPDATE flights
            SET seats_available = seats_available - ?
            WHERE id = ?
        """, (seats, flight_id))

        conn.commit()

        return jsonify({
            "message": "Booking confirmed",
            "pnr": pnr,
            "price": final_price
        })

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
@app.route("/booking/<pnr>", methods=["GET"])
def get_booking(pnr):
    conn = sqlite3.connect("flights.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT booking_id, flight_id, passenger_name, seats_booked,
               final_price, status, pnr, booking_time
        FROM bookings
        WHERE pnr = ?
    """, (pnr,))

    booking = cur.fetchone()
    conn.close()

    if not booking:
        return jsonify({"error": "Booking not found"}), 404

    return jsonify({
        "booking_id": booking[0],
        "flight_id": booking[1],
        "passenger_name": booking[2],
        "seats_booked": booking[3],
        "final_price": booking[4],
        "status": booking[5],
        "pnr": booking[6],
        "booking_time": booking[7]
    })
@app.route("/cancel/<pnr>", methods=["POST"])
def cancel_booking(pnr):
    conn = sqlite3.connect("flights.db")
    cur = conn.cursor()

    try:
        conn.execute("BEGIN")

        cur.execute("""
            SELECT flight_id, seats_booked
            FROM bookings
            WHERE pnr = ? AND status = 'CONFIRMED'
        """, (pnr,))
        booking = cur.fetchone()

        if not booking:
            conn.rollback()
            return jsonify({"error": "Booking not found or already cancelled"}), 404

        flight_id, seats = booking

        cur.execute("""
            UPDATE bookings
            SET status = 'CANCELLED'
            WHERE pnr = ?
        """, (pnr,))

        cur.execute("""
            UPDATE flights
            SET seats_available = seats_available + ?
            WHERE id = ?
        """, (seats, flight_id))

        conn.commit()
        return jsonify({"message": "Booking cancelled successfully"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()
