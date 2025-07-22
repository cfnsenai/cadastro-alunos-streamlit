import streamlit as st
import db
import pandas as pd
import plotly.express as px
import re
import logging
import auth

# Inicializa banco de autenticação
auth.init_db()

# Configuração de log
logging.basicConfig(
    filename='logs_alunos.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def validar_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# Inicializa banco de dados principal
db.conectar()

# Configuração da página
st.set_page_config(page_title="Cadastro de Alunos", layout="centered")

# Estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

# ------ Autenticação ------
if not st.session_state.autenticado:
    st.title("🔐 Login de Usuário")
    aba = st.radio("Acesso", ["Conecte-se", "Cadastro"])

    if aba == "Conecte-se":
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar", key="login"):
            if auth.autenticar_usuario(email, senha):
                st.session_state.autenticado = True
                st.session_state.usuario = email
                st.success("Login autorizado!")
                st.rerun()
            else:
                st.error("Usuário não encontrado, senha incorreta ou acesso não autorizado. Tente novamente ou cadastre-se.")


    elif aba == "Cadastro":
        nome = st.text_input("Nome")
        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")
        if st.button("Cadastrar", key="cadastro"):
            ok, msg = auth.cadastrar_usuario(nome, email, senha)
            if ok:
                st.success(msg)
            else:
                st.error(msg)

# ------ Sistema (usuário logado) ------
else:
    st.sidebar.markdown(f"👤 Usuário: **{st.session_state.usuario}**")
    if st.sidebar.button("🚪 Sair", key="logout"):
        st.session_state.autenticado = False
        st.session_state.usuario = ""
        st.rerun()

    st.title("📚 Sistema de Cadastro de Alunos")
    aba = st.sidebar.radio("Navegação", ["Cadastrar", "Visualizar", "Atualizar", "Excluir", "Exportar CSV"])

    if aba == "Cadastrar":
        st.subheader("➕ Novo Aluno")
        with st.form(key="form_cadastro"):
            nome = st.text_input("Nome", key="nome")
            idade = st.text_input("Idade", key="idade")
            curso = st.text_input("Curso", key="curso")
            email = st.text_input("E-mail", key="email")
            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                if not nome or not idade or not curso or not email:
                    st.warning("Preencha todos os campos.")
                elif not idade.isdigit() or int(idade) <= 0:
                    st.warning("Idade inválida.")
                elif not validar_email(email):
                    st.warning("E-mail inválido.")
                else:
                    db.inserir_aluno(nome.strip(), int(idade), curso.strip(), email.strip())
                    logging.info(f"Aluno cadastrado: {nome}, {idade}, {curso}, {email}")
                    st.success(f"Aluno '{nome}' cadastrado com sucesso!")
                    st.experimental_rerun()

    elif aba == "Visualizar":
        st.subheader("📋 Lista de Alunos")
        df = db.listar_alunos()
        st.dataframe(df)

        if not df.empty:
            st.subheader("📊 Alunos por Curso")
            grafico = px.histogram(df, x="curso", title="Alunos por Curso")
            st.plotly_chart(grafico)

    elif aba == "Atualizar":
        st.subheader("✏️ Atualizar Aluno")
        df = db.listar_alunos()

        if df.empty:
            st.info("Nenhum aluno cadastrado.")
        else:
            aluno_selecionado = st.selectbox("Escolha um aluno", df["id"].astype(str) + " - " + df["nome"])
            id_aluno = int(aluno_selecionado.split(" - ")[0])
            dados = db.buscar_aluno_por_id(id_aluno)

            if not dados.empty:
                nome = st.text_input("Nome", dados["nome"].iloc[0])
                idade = st.text_input("Idade", str(dados["idade"].iloc[0]))
                curso = st.text_input("Curso", dados["curso"].iloc[0])
                email = st.text_input("E-mail", dados["email"].iloc[0])

                if st.button("Atualizar", key="atualizar"):
                    if not nome or not idade or not curso or not email or not idade.isdigit():
                        st.warning("Preencha os campos corretamente.")
                    elif not validar_email(email):
                        st.warning("E-mail inválido.")
                    else:
                        db.atualizar_aluno(id_aluno, nome.strip(), int(idade), curso.strip(), email.strip())
                        logging.info(f"Aluno atualizado (ID: {id_aluno}): {nome}, {idade}, {curso}, {email}")
                        st.success("Aluno atualizado com sucesso!")

    elif aba == "Excluir":
        st.subheader("🗑️ Excluir Aluno")
        df = db.listar_alunos()

        if df.empty:
            st.info("Nenhum aluno cadastrado.")
        else:
            aluno_selecionado = st.selectbox("Escolha um aluno para excluir", df["id"].astype(str) + " - " + df["nome"])
            id_aluno = int(aluno_selecionado.split(" - ")[0])

            if st.button("Excluir", key="excluir"):
                db.excluir_aluno(id_aluno)
                logging.info(f"Aluno excluído (ID: {id_aluno})")
                st.success("Aluno excluído com sucesso!")
                st.experimental_rerun()

    elif aba == "Exportar CSV":
        st.subheader("📤 Exportar Dados para CSV")
        csv = db.exportar_csv()
        st.download_button(
            label="📥 Baixar CSV",
            data=csv,
            file_name="alunos_exportados.csv",
            mime="text/csv"
        )
        st.success("Clique para baixar o arquivo.")
