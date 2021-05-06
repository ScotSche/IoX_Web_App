import sqlite3
import base64


connection = sqlite3.connect("iox.db")
print("Opened database successfully");

connection.execute('''CREATE TABLE Dashboard
         (ID INT PRIMARY KEY,
         Image      TEXT        NOT NULL,
         Device     TEXT        NOT NULL,
         Tag        CHAR(5)     NOT NULL,
         Location   CHAR(50)    NOT NULL,
         Status     CHAR(4)     NOT NULL);''')

print("Table created successfully");


imagePath = 'resources/MeasuringUnit.png'

connection.execute("INSERT INTO Dashboard (Image,Device,Tag,Location,Status) \
      VALUES (?, ?, ?, ?, ?)", (imagePath, 'DeviceName', 'D-005', 'Location', '0xFF'));

connection.execute("INSERT INTO Dashboard (Image,Device,Tag,Location,Status) \
      VALUES (?, ?, ?, ?, ?)", (imagePath, 'DeviceName', 'D-005', 'Location', '0xFF'));

connection.execute("INSERT INTO Dashboard (Image,Device,Tag,Location,Status) \
      VALUES (?, ?, ?, ?, ?)", (imagePath, 'DeviceName', 'D-005', 'Location', '0xFF'));

connection.execute("INSERT INTO Dashboard (Image,Device,Tag,Location,Status) \
      VALUES (?, ?, ?, ?, ?)", (imagePath, 'DeviceName', 'D-005', 'Location', '0xFF'));

connection.commit()

print("Records created successfully");

connection.close()