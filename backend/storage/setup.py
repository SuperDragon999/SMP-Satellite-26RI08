#Set up SQLite
import sqlite3
import pandas as pd

#Data Logs
database = sqlite3.connect("backend/storage/data/logs.db")
c = database.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS data(
          ID INTEGER PRIMARY KEY,
          sensor INTEGER,
          latency INTEGER,
          type TEXT
);
''')

c.execute('''
CREATE TABLE IF NOT EXISTS ctrl(
          record INTEGER
);
''')

query = f"SELECT COUNT(*) FROM ctrl"
data = pd.read_sql(query, database)
ctrl_size = int(data.iloc[0, 0])
if ctrl_size == 0:
    x = 0 #default recording status is 0
    c.execute('''
    INSERT INTO ctrl VALUES (?);
    ''', (x, ))

database.commit()
database.close()