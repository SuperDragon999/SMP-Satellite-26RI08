#Set up SQLite
import sqlite3

database = sqlite3.connect("backend/storage/data/dataLogs.db")
c = database.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS data(
          ID INTEGER PRIMARY KEY,
          STATION TEXT NOT NULL,
          DATA TEXT NOT NULL
);
''') #NOT DONE YET, TODO

#remember to drop the table done so far because it's not the actual thing

database.commit()
database.close()