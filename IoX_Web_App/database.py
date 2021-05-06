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


#class Database:
#    connection = sqlite3.connect("iox.db")

#    connection.execute('''CREATE TABLE if not exists Dashboard
#         (ID INT PRIMARY KEY,
#         Image      TEXT        NOT NULL,
#         Device     TEXT        NOT NULL,
#         Tag        CHAR(5)     NOT NULL,
#         Location   CHAR(50)    NOT NULL,
#         Status     CHAR(4)     NOT NULL);''')

#    connection.commit()
#    print("Initializing process finished")

#    @classmethod
#    def checkIfTableExists(name):
#        connection.execute('''CREATE TABLE if not exists %s
#         (ID INT PRIMARY KEY,
#         record      TEXT        NOT NULL,);''' % (name))
#        connection.commit()

#    @classmethod
#    def getAllOverviewData(object):
#        mycursor = object.connection.cursor()
#        mycursor.execute("SELECT * FROM Dashboard")
#        return mycursor.fetchall()



#IMAGEPATH = 'RESOURCES/MEASURINGUNIT.PNG'

#CONNECTION.EXECUTE("INSERT INTO DASHBOARD (IMAGE,DEVICE,TAG,LOCATION,STATUS) \
#      VALUES (?, ?, ?, ?, ?)", (IMAGEPATH, 'DEVICENAME', 'D-001', 'LOCATION', '0XFF'));

#CONNECTION.EXECUTE("INSERT INTO DASHBOARD (IMAGE,DEVICE,TAG,LOCATION,STATUS) \
#      VALUES (?, ?, ?, ?, ?)", (IMAGEPATH, 'DEVICENAME', 'D-002', 'LOCATION', '0XFF'));

#CONNECTION.EXECUTE("INSERT INTO DASHBOARD (IMAGE,DEVICE,TAG,LOCATION,STATUS) \
#      VALUES (?, ?, ?, ?, ?)", (IMAGEPATH, 'DEVICENAME', 'D-003', 'LOCATION', '0XFF'));

#CONNECTION.EXECUTE("INSERT INTO DASHBOARD (IMAGE,DEVICE,TAG,LOCATION,STATUS) \
#      VALUES (?, ?, ?, ?, ?)", (IMAGEPATH, 'DEVICENAME', 'D-004', 'LOCATION', '0XFF'));

#CONNECTION.COMMIT()

#CONNECTION.CLOSE()