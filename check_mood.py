import sqlite3

conn = sqlite3.connect("database/mindwell.db")
cursor = conn.cursor()

cursor.execute(
    "UPDATE journal SET mood = ? WHERE mood = ?",
    ("Happy", "😊 Happy")
)

conn.commit()
conn.close()

print("Done! 😊 Happy changed to Happy")