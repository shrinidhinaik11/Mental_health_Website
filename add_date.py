import sqlite3

conn = sqlite3.connect("database/mindwell.db")
cursor = conn.cursor()

cursor.execute("SELECT id, title, mood, date FROM journal")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()