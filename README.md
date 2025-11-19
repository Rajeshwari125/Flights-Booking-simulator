🛠️ Tasks Completed
1️⃣ Designed and Implemented Database Schema
Created a SQLite database (flights.db).

Implemented a flights table with fields:

origin, destination

departure_time, arrival_time

base_price

available_seats

Defined primary key using id INTEGER PRIMARY KEY AUTOINCREMENT.

2️⃣ Populated Database with Simulated Flight Data

Inserted multiple sample flight records (Chennai → Mumbai, Chennai → Delhi, etc.).

Ensured data includes realistic:

Dates and timings

Prices

Seat counts

3️⃣ Built REST APIs Using FastAPI

Created a FastAPI backend application with the following endpoints:

✔ GET /flights

Returns all flights from the database.

✔ GET /search?origin=&destination=

Allows users to search flights by origin and destination.

Retrieves specific filtered results from SQLite.

4️⃣ Implemented Basic Input Handling

Parameters passed through API query strings.

Ensures origin and destination are validated before executing queries.

5️⃣ Simulated External Airline Data

Added hard-coded simulated flight records to represent external airline feeds.

📤 Output of Milestone 1
✔ Populated flight database

A fully functional SQLite DB containing sample flight schedules.

✔ Working Flight Search API

API endpoints for:

Retrieving all flights

Searching by origin & destination

JSON responses successfully tested using Python requests.

✔ Simulated Airline Data Feeds

Sample data added to mimic external airline schedule APIs.

🎯 Final Result

By completing Milestone 1, a complete flight search foundation was built.
The system now supports:

A structured database

A functional backend

Search features

API testing and validation

This lays the groundwork for adding dynamic pricing, booking features, user authentication, and schedule updates in future milestones.
