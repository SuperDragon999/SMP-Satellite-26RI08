#Set up SQLite
import sqlite3

#Data Logs
database = sqlite3.connect("backend/storage/data/logs.db")
c = database.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS data(
          ID INTEGER PRIMARY KEY,
          Satellite TEXT NOT NULL,
          Main_Bus_Voltage INTEGER,
          Temperature INTEGER,
          Solar_Generation INTEGER
);
''') #Simple version

c.execute('''
CREATE TABLE IF NOT EXISTS commands(
          ID INTEGER PRIMARY KEY,
          Satellite TEXT NOT NULL,
          Command TEXT NOT NULL
);
''') #Prelimnary version

database.commit()
database.close()