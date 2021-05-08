import sqlite3

class DBConnection:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(DBConnection)
            return cls.instance
        return cls.instance

    def __init__(self, db_name='iox.db'):
        self.name = db_name
        # connect takes url, dbname, user-id, password
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def getAllOverviewData(self):
        self.cursor.execute("SELECT * FROM Dashboard")
        return self.cursor.fetchall()


#   JupyterLab stuff

#import sqlite3
#import pandas as pd

#connection = sqlite3.connect("PID.db")
#cursor = connection.cursor()

##Create master table with all devices (for overview)
#sql_query = """
#CREATE TABLE IF NOT EXISTS devices (
#id INTEGER PRIMARY KEY,
#tag VARCHAR(6),
#name TEXT,
#order_code TEXT,
#serial_number TEXT,
#device_type TEXT,
#measured_value TEXT,
#measuring_method TEXT,
#manufacturer TEXT,
#plant VARCHAR(4),
#facility VARCHAR(4),
#tank VARCHAR(5),
#ti TEXT,
#ba TEXT,
#image TEXT);"""

#cursor.execute(sql_query)

#df = pd.read_excel('C:/Users/sebas/OneDrive/Desktop/Gerätedaten.xlsx', sheet_name='Gerät')

#for i in range(len(df)):  
#    sql_query = """
#    INSERT INTO devices (tag, name, order_code, serial_number, device_type, measured_value,
#    measuring_method, manufacturer, plant, facility, tank, ti, ba) \
#    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""" 
    
#    data_tuple = (df.loc[i, "Device tag"], df.loc[i, "Name"], df.loc[i, "Order code"], 
#    df.loc[i, "Serial number"], df.loc[i, "Device type"], df.loc[i, "Measured value"], 
#    df.loc[i, "Measuring method"], df.loc[i, "Hersteller"], df.loc[i, "Plant"], df.loc[i, "Facility"], 
#    df.loc[i, "Tanks"], df.loc[i, "TI"], df.loc[i, "BA"])
    
#    cursor.execute(sql_query, data_tuple)
#    print("Executed")


##Create measurement table with all measurements (for devices)
#sql_query = """
#CREATE TABLE IF NOT EXISTS measurements (
#id INTEGER PRIMARY KEY,
#tag VARCHAR(6),
#measuring TEXT,
#distance FLOAT,
#level_absolut FLOAT,
#level_relative FLOAT,
#medium_type TEXT,
#tank_type TEXT,
#tank_height FLOAT,
#tank_diameter FLOAT,
#max_filling_speed TEXT,
#max_draining_speed TEXT,
#blocking_distance FLOAT,
#actual_diagnostics TEXT,
#used_calculation TEXT,
#echo_amplitude INTEGER,
#operation_time TEXT,
#envelope_curve TEXT);"""

#cursor.execute(sql_query)

##Create measurement table with all measurements (for devices)
#sql_query = """
#CREATE TABLE IF NOT EXISTS device_status (
#id INTEGER PRIMARY KEY,
#tag VARCHAR(6),
#status VARCHAR(4),
#damping_factor_empty FLOAT);"""

#connection.commit()
#connection.close()