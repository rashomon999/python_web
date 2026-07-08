from app import mysql
conn = mysql.connect()
cur = conn.cursor()
cur.execute('SELECT id, nombre, imagen, url FROM python_libros')
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()