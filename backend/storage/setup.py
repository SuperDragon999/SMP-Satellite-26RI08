#Set up SQLite
import sqlite3

#Data Logs
database = sqlite3.connect("backend/storage/data/logs.db")
c = database.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS data(
          ID INTEGER PRIMARY KEY,
          sensor INTEGER,
          latency INTEGER
);
''')

database.commit()
database.close()