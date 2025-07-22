from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import pandas as pd
from email.mime.text import MIMEText
from hashlib import sha256
import smtplib
import streamlit as st

# Configuração do banco PostgreSQL
DATABASE_URL = st.secrets["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

ADMIN_EMAIL = "claudio.neves@edu.sc.senai.br"

# Inicializa a tabela de usuários
def init_db():
    with engine.connect() as conn:
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT,
                email TEXT UNIQUE,
                senha TEXT,
                autorizado BOOLEAN DEFAULT FALSE
            )
        '''))

# Cadastra novo usuário
def cadastrar_usuario(nome, email, senha):
    try:
        autorizado = True if email == ADMIN_EMAIL else False
        with engine.connect() as conn:
            conn.execute(text('''
                INSERT INTO usuarios (nome, email, senha, autorizado)
                VALUES (:nome, :email, :senha, :autorizado)
            '''), {
                "nome": nome,
                "email": email,
                "senha": sha256(senha.encode()).hexdigest(),
                "autorizado": autorizado
            })
        if not autorizado:
            enviar_email_para_admin(nome, email)
        return True, "Cadastro realizado com sucesso! Aguarde autorização." if not autorizado else "Cadastro administrador ativo."
    except Exception as e:
        return False, f"Erro: {e}"

# Autentica usuário autorizado
def autenticar_usuario(email, senha):
    ADMIN_EMAIL = "claudio.neves@edu.sc.senai.br"
    ADMIN_SENHA = ADMIN_SENHA = st.secrets["ADMIN_PASSWORD"] # Você pode definir via secrets também

    if email == ADMIN_EMAIL:
        return senha == ADMIN_SENHA  # acesso direto sem verificação no banco

    senha_hash = sha256(senha.encode()).hexdigest()
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT autorizado FROM usuarios 
            WHERE email = :email AND senha = :senha
        """), {"email": email, "senha": senha_hash})

        row = result.fetchone()
        return row is not None and row[0] == 1



# Lista usuários não autorizados
def listar_pendentes():
    with engine.connect() as conn:
        result = conn.execute(text('''
            SELECT id, nome, email FROM usuarios WHERE autorizado = FALSE
        ''')).fetchall()
    return result

# Autoriza usuário e envia e-mail
def autorizar_usuario(user_id, email):
    with engine.connect() as conn:
        conn.execute(text('''
            UPDATE usuarios SET autorizado = TRUE WHERE id = :id
        '''), {"id": user_id})
    enviar_email_para_usuario(email)

# Envia e-mail ao administrador
def enviar_email_para_admin(nome, email):
    corpo = f"Novo cadastro:\nNome: {nome}\nEmail: {email}"
    enviar_email(ADMIN_EMAIL, "Novo Cadastro de Usuário", corpo)

# Envia e-mail ao usuário autorizado
def enviar_email_para_usuario(email):
    corpo = "Seu acesso ao sistema foi autorizado! Agora você pode fazer login."
    enviar_email(email, "Acesso Autorizado", corpo)

# Função de envio de e-mail
def enviar_email(destinatario, assunto, corpo):
    remetente = st.secrets["EMAIL"]
    senha = st.secrets["EMAIL_PASSWORD"]

    msg = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Erro ao enviar email: {e}")
