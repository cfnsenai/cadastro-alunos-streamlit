import sqlite3
import pandas as pd
import streamlit as st

# ----- BANCO DE DADOS -----
def conectar():
    conn = sqlite3.connect("alunos.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER,
            curso TEXT
        )
    """)
    conn.commit()
    conn.close()

def inserir_aluno(nome, idade, curso):
    conn = sqlite3.connect("alunos.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO alunos (nome, idade, curso) VALUES (?, ?, ?)", (nome, idade, curso))
    conn.commit()
    conn.close()

def listar_alunos():
    conn = sqlite3.connect("alunos.db")
    df = pd.read_sql_query("SELECT * FROM alunos", conn)
    conn.close()
    return df

def buscar_aluno_por_id(id):
    conn = sqlite3.connect("alunos.db")
    df = pd.read_sql_query("SELECT * FROM alunos WHERE id = ?", conn, params=(id,))
    conn.close()
    return df

def atualizar_aluno(id, nome, idade, curso):
    conn = sqlite3.connect("alunos.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE alunos SET nome=?, idade=?, curso=? WHERE id=?", (nome, idade, curso, id))
    conn.commit()
    conn.close()

def excluir_aluno(id):
    conn = sqlite3.connect("alunos.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alunos WHERE id=?", (id,))
    conn.commit()
    conn.close()

def exportar_csv():
    df = listar_alunos()
    return df.to_csv(index=False).encode('utf-8')

# ----- INTERFACE STREAMLIT -----
conectar()
st.set_page_config(page_title="Cadastro de Alunos", layout="centered")

st.title("📚 Sistema de Cadastro de Alunos")

aba = st.sidebar.radio("Navegação", ["Cadastrar", "Visualizar", "Atualizar", "Excluir", "Exportar CSV"])

# ---------- Cadastrar ----------
if aba == "Cadastrar":
    st.subheader("➕ Novo Aluno")
    nome = st.text_input("Nome")
    idade = st.text_input("Idade")
    curso = st.text_input("Curso")

    if st.button("Cadastrar"):
        if not nome or not idade or not curso:
            st.warning("Preencha todos os campos.")
        elif not idade.isdigit() or int(idade) <= 0:
            st.warning("Idade inválida.")
        else:
            inserir_aluno(nome.strip(), int(idade), curso.strip())
            st.success(f"Aluno '{nome}' cadastrado com sucesso!")

# ---------- Visualizar ----------
elif aba == "Visualizar":
    st.subheader("📋 Lista de Alunos")
    df = listar_alunos()
    st.dataframe(df)

# ---------- Atualizar ----------
elif aba == "Atualizar":
    st.subheader("✏️ Atualizar Aluno")
    df = listar_alunos()
    aluno_selecionado = st.selectbox("Escolha um aluno", df["id"].astype(str) + " - " + df["nome"])

    if aluno_selecionado:
        id_aluno = int(aluno_selecionado.split(" - ")[0])
        dados = buscar_aluno_por_id(id_aluno)

        if not dados.empty:
            nome = st.text_input("Nome", dados["nome"][0])
            idade = st.text_input("Idade", str(dados["idade"][0]))
            curso = st.text_input("Curso", dados["curso"][0])

            if st.button("Atualizar"):
                if not nome or not idade or not curso or not idade.isdigit():
                    st.warning("Preencha os campos corretamente.")
                else:
                    atualizar_aluno(id_aluno, nome.strip(), int(idade), curso.strip())
                    st.success("Aluno atualizado com sucesso!")

# ---------- Excluir ----------
elif aba == "Excluir":
    st.subheader("🗑️ Excluir Aluno")
    df = listar_alunos()
    aluno_selecionado = st.selectbox("Escolha um aluno para excluir", df["id"].astype(str) + " - " + df["nome"])

    if aluno_selecionado:
        id_aluno = int(aluno_selecionado.split(" - ")[0])
        if st.button("Excluir"):
            excluir_aluno(id_aluno)
            st.success("Aluno excluído com sucesso!")

# ---------- Exportar ----------
elif aba == "Exportar CSV":
    st.subheader("📤 Exportar Dados para CSV")
    csv = exportar_csv()
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name="alunos_exportados.csv",
        mime="text/csv"
    )
    st.success("Clique para baixar o arquivo.")

