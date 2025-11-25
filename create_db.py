import sqlite3
import pandas as pd

# Read the dataset (replace with your correct path)
df = pd.read_csv('Flight_Data.csv')

# Create a connection to SQLite database
conn = sqlite3.connect('flights.db')
cursor = conn.cursor()

# Create the database schema
cursor.execute('''
CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY,
   Origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    times TEXT NOT NULL,
    price REAL NOT NULL,
    seats INTEGER NOT NULL
);
''')

# Populate the database with data from the dataset
for index, row in df.iterrows():
    cursor.execute('''
    INSERT INTO flights (origin, destination, times, price, seats)
    VALUES (?, ?, ?, ?, ?)
    ''', (row['Origin'], row['destination'], row['time'], row['price'], row['seats']))

conn.commit()

# Close the database connection
conn.close()