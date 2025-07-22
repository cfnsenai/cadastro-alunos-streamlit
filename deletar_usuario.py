import sqlite3

def listar_usuarios():
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("SELECT id, nome, email, autorizado FROM usuarios")
    usuarios = c.fetchall()
    conn.close()
    print("Usuários cadastrados:")
    for u in usuarios:
        print(u)

def deletar_usuario(email):
    conn = sqlite3.connect("usuarios.db")
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    print(f"Tentativa de remoção para: {email}")

# Substitua abaixo pelo e-mail que você quer deletar
email_para_apagar = "s2b.claudioneves@gmail.com
listar_usuarios()
deletar_usuario(email_para_apagar)
listar_usuarios()
