import streamlit as st
import db
import pandas as pd
import plotly.express as px
import re
import logging
import auth
from datetime import date

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

        # Gera chave única do formulário a cada sucesso
        if "form_reset" not in st.session_state:
            st.session_state.form_reset = 0

        if st.session_state.get("cadastro_ok", False):
            st.session_state.cadastro_ok = False
            st.session_state.form_reset += 1

        with st.form(key=f"form_cadastro_{st.session_state.form_reset}"):
            nome = st.text_input("Nome")
            idade = st.text_input("Idade")
            curso = st.text_input("Curso")
            email = st.text_input("E-mail")
            data_nascimento = st.date_input("Data de Nascimento", value=date.today())
            data_matricula = st.date_input("Dados de Matrícula", value=date.today())
            genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"])
            endereco = st.text_input("Endereço")
            numero = st.text_input("Número")
            cep = st.text_input("CEP")
            nome_mae = st.text_input("Nome da Mãe")
            nome_pai = st.text_input("Nome do Pai")
            data_ocorrencia = st.date_input("Dados da Ocorrência", value=date.today())
            descricao_ocorrencia = st.text_area("Descrição da Ocorrência")

            submitted = st.form_submit_button("Cadastrar")

            if submitted:
                if not nome or not idade.isdigit():
                    st.warning("Preencha corretamente os campos obrigatórios.")
                else:
                    db.inserir_aluno(
                        nome.strip(),
                        int(idade),
                        curso.strip(),
                        email.strip(),
                        data_nascimento,
                        data_matricula,
                        genero,
                        endereco,
                        numero,
                        cep,
                        nome_mae,
                        nome_pai,
                        data_ocorrencia,
                        descricao_ocorrencia.strip()
                    )
                    st.success(f"Aluno '{nome}' cadastrado com sucesso!")
                    st.session_state.cadastro_ok = True




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
                with st.form(key="form_atualizar"):
                    nome = st.text_input("Nome", dados["nome"].iloc[0])
                    idade = st.text_input("Idade", str(dados["idade"].iloc[0]))
                    curso = st.text_input("Curso", dados["curso"].iloc[0])
                    email = st.text_input("E-mail", dados["email"].iloc[0])
                    data_nascimento = st.date_input("Data de Nascimento", value=pd.to_datetime(dados["data_nascimento"].iloc[0]))
                    data_matricula = st.date_input("Data de Matrícula", value=pd.to_datetime(dados["data_matricula"].iloc[0]))
                    genero = st.selectbox("Gênero", ["Masculino", "Feminino", "Outro"], index=["Masculino", "Feminino", "Outro"].index(dados["genero"].iloc[0]))
                    endereco = st.text_input("Endereço", dados["endereco"].iloc[0])
                    numero = st.text_input("Número", dados["numero"].iloc[0])
                    cep = st.text_input("CEP", dados["cep"].iloc[0])
                    nome_mae = st.text_input("Nome da Mãe", dados["nome_mae"].iloc[0])
                    nome_pai = st.text_input("Nome do Pai", dados["nome_pai"].iloc[0])
                    data_ocorrencia = st.date_input("Data da Ocorrência", value=pd.to_datetime(dados["data_ocorrencia"].iloc[0]))
                    descricao_ocorrencia = st.text_area("Descrição da Ocorrência", dados["descricao_ocorrencia"].iloc[0])

                    if st.form_submit_button("Atualizar"):
                        db.atualizar_aluno(
                            id_aluno, nome, int(idade), curso, email,
                            data_nascimento, data_matricula, genero,
                            endereco, numero, cep, nome_mae, nome_pai,
                            data_ocorrencia, descricao_ocorrencia
                        )
                        logging.info(f"Aluno atualizado (ID: {id_aluno}): {nome}, {idade}, {curso}, {email}")
                        st.success("Aluno atualizado com sucesso!")
                        st.rerun()

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
                st.rerun()

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