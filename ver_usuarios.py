import sqlite3

conn = sqlite3.connect("usuarios.db")
c = conn.cursor()
c.execute("SELECT id, nome, email, autorizado FROM usuarios")
usuarios = c.fetchall()
for u in usuarios:
    print(u)
conn.close()
