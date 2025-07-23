import os
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st

# Pega a URL do banco de dados do secrets.toml
DATABASE_URL = st.secrets["DATABASE_URL"]

# Cria o engine com SQLAlchemy
engine = create_engine(DATABASE_URL)

# ----- Funções CRUD -----

def conectar():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                idade INTEGER,
                curso TEXT,
                email TEXT,
                data_nascimento DATE,
                data_matricula DATE,
                genero TEXT,
                endereco TEXT,
                numero TEXT,
                cep TEXT,
                nome_mae TEXT,
                nome_pai TEXT,
                data_ocorrencia DATE,
                descricao_ocorrencia TEXT
            )
        """))

def inserir_aluno(nome, idade, curso, email, data_nascimento, data_matricula,
                  genero, endereco, numero, cep, nome_mae, nome_pai,
                  data_ocorrencia, descricao_ocorrencia):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO alunos (
                nome, idade, curso, email, data_nascimento, data_matricula,
                genero, endereco, numero, cep, nome_mae, nome_pai,
                data_ocorrencia, descricao_ocorrencia
            )
            VALUES (
                :nome, :idade, :curso, :email, :data_nascimento, :data_matricula,
                :genero, :endereco, :numero, :cep, :nome_mae, :nome_pai,
                :data_ocorrencia, :descricao_ocorrencia
            )
        """), {
            "nome": nome,
            "idade": idade,
            "curso": curso,
            "email": email,
            "data_nascimento": data_nascimento,
            "data_matricula": data_matricula,
            "genero": genero,
            "endereco": endereco,
            "numero": numero,
            "cep": cep,
            "nome_mae": nome_mae,
            "nome_pai": nome_pai,
            "data_ocorrencia": data_ocorrencia,
            "descricao_ocorrencia": descricao_ocorrencia
        })

def listar_alunos():
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM alunos ORDER BY id", conn)
    return df

def buscar_aluno_por_id(id):
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM alunos WHERE id = %s", conn, params=(id,))
    return df

def atualizar_aluno(id, nome, idade, curso, email, data_nascimento, data_matricula,
                    genero, endereco, numero, cep, nome_mae, nome_pai,
                    data_ocorrencia, descricao_ocorrencia):
    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE alunos SET
                nome = :nome,
                idade = :idade,
                curso = :curso,
                email = :email,
                data_nascimento = :data_nascimento,
                data_matricula = :data_matricula,
                genero = :genero,
                endereco = :endereco,
                numero = :numero,
                cep = :cep,
                nome_mae = :nome_mae,
                nome_pai = :nome_pai,
                data_ocorrencia = :data_ocorrencia,
                descricao_ocorrencia = :descricao_ocorrencia
            WHERE id = :id
        """), {
            "id": id,
            "nome": nome,
            "idade": idade,
            "curso": curso,
            "email": email,
            "data_nascimento": data_nascimento,
            "data_matricula": data_matricula,
            "genero": genero,
            "endereco": endereco,
            "numero": numero,
            "cep": cep,
            "nome_mae": nome_mae,
            "nome_pai": nome_pai,
            "data_ocorrencia": data_ocorrencia,
            "descricao_ocorrencia": descricao_ocorrencia
        })

def excluir_aluno(id):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM alunos WHERE id = :id"), {"id": id})

def exportar_csv():
    df = listar_alunos()
    return df.to_csv(index=False).encode('utf-8')
