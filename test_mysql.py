
from app import get_mysql_connection

try:
    connection = get_mysql_connection()

    cursor = connection.cursor()
    cursor.execute("SELECT DATABASE()")

    result = cursor.fetchone()

    print("MySQL connection successful!")
    print("Connected database:", result[0])

    cursor.close()
    connection.close()

except Exception as e:
    print("Connection failed:", e)
