import sqlite3
import pandas as pd

connection = sqlite3.connect("PID.db")
cursor = connection.cursor()

#Create master table with all devices (for overview)
sql_query = """
CREATE TABLE IF NOT EXISTS devices (
id INTEGER PRIMARY KEY,
tag VARCHAR(6),
name TEXT,
order_code TEXT,
serial_number TEXT,
device_type TEXT,
measured_value TEXT,
measuring_method TEXT,
manufacturer TEXT,
plant VARCHAR(4),
facility VARCHAR(4),
tank VARCHAR(5),
ti TEXT,
ba TEXT,
image TEXT);"""
cursor.execute(sql_query)

#Create measurement table with all measurements (for devices)
sql_query = """
CREATE TABLE IF NOT EXISTS measurements (
id INTEGER PRIMARY KEY,
tag VARCHAR(6),
measuring TEXT,
distance FLOAT,
level_absolut FLOAT,
level_relative FLOAT,
medium_type TEXT,
tank_type TEXT,
tank_height FLOAT,
tank_diameter FLOAT,
max_filling_speed TEXT,
max_draining_speed TEXT,
blocking_distance FLOAT,
actual_diagnostics TEXT,
used_calculation TEXT,
echo_amplitude FLOAT,
operation_time TEXT,
envelope_curve TEXT);"""
cursor.execute(sql_query)

#Create measurement table with all measurements (for devices)
sql_query = """
CREATE TABLE IF NOT EXISTS device_status (
id INTEGER PRIMARY KEY,
tag VARCHAR(6),
status VARCHAR(4),
damping_factor_empty FLOAT);"""
cursor.execute(sql_query)

connection.commit()
connection.close()