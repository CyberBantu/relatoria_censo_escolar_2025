from pathlib import Path

import pandas as pd
import streamlit as st

# carregamento de dados
DATA_DIR = Path(__file__).parent / "dados"

# Setando informações de base
DEPENDENCIA_MAP = {1: "Federal", 2: "Estadual", 3: "Municipal", 4: "Privada"}
LOCALIZACAO_MAP = {1: "Urbana", 2: "Rural"}
DEPENDENCIA_COLORS = {
    "Federal": "#1f77b4",
    "Estadual": "#2ca02c",
    "Municipal": "#ff7f0e",
    "Privada": "#9467bd",
}


def fmt_int(n):
    return f"{n:,.0f}".replace(",", ".")


def fmt_dec(n, d=1):
    s = f"{n:,.{d}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


@st.cache_data(show_spinner="Carregando dados das escolas...")
def load_escola():
    cols = [
        "CO_ENTIDADE", "NO_REGIAO", "NO_UF", "SG_UF",
        "NO_MUNICIPIO", "NO_ENTIDADE",
        "TP_DEPENDENCIA", "TP_LOCALIZACAO",
        "NO_BAIRRO", "LATITUDE", "LONGITUDE",
        "IN_AGUA_POTAVEL", "IN_AGUA_REDE_PUBLICA", "IN_AGUA_INEXISTENTE",
        "IN_ESGOTO_REDE_PUBLICA", "IN_ESGOTO_FOSSA_SEPTICA", "IN_ESGOTO_INEXISTENTE",
        "IN_ENERGIA_REDE_PUBLICA", "IN_ENERGIA_INEXISTENTE",
        "IN_BIBLIOTECA", "IN_BIBLIOTECA_SALA_LEITURA",
        "IN_LABORATORIO_CIENCIAS", "IN_LABORATORIO_INFORMATICA",
        "IN_QUADRA_ESPORTES", "IN_REFEITORIO", "IN_AUDITORIO",
        "IN_BANHEIRO_PNE", "IN_COZINHA", "IN_PATIO_COBERTO",
        "IN_COMPUTADOR", "IN_INTERNET", "IN_INTERNET_ALUNOS", "IN_BANDA_LARGA",
        "IN_DESKTOP_ALUNO", "IN_COMP_PORTATIL_ALUNO", "IN_TABLET_ALUNO",
        "IN_ACESSIBILIDADE_INEXISTENTE",
        "QT_SALAS_UTILIZADAS",
        "IN_ALIMENTACAO",
        "IN_REGULAR", "IN_EJA", "IN_PROFISSIONALIZANTE", "IN_ESPECIAL_EXCLUSIVA",
        "QT_PROF_PSICOLOGO", "QT_PROF_ASSIST_SOCIAL",
    ]

    df = pd.read_parquet(
        DATA_DIR / "Tabela_Escola_2025.parquet",
        columns=cols,
    )

    df["Dependencia"] = df["TP_DEPENDENCIA"].map(DEPENDENCIA_MAP)
    df["Localizacao"] = df["TP_LOCALIZACAO"].map(LOCALIZACAO_MAP)

    return df


@st.cache_data(show_spinner="Carregando dados de matriculas...")
def load_matricula():
    cols = [
        "CO_ENTIDADE", "QT_MAT_BAS",
        "QT_MAT_INF", "QT_MAT_INF_CRE", "QT_MAT_INF_PRE",
        "QT_MAT_FUND", "QT_MAT_FUND_AI", "QT_MAT_FUND_AF",
        "QT_MAT_MED", "QT_MAT_EJA", "QT_MAT_PROF",
    ]

    return pd.read_parquet(
        DATA_DIR / "Tabela_Matricula_2025.parquet",
        columns=cols,
    )


@st.cache_data(show_spinner="Carregando dados de docentes...")
def load_docente():
    return pd.read_parquet(
        DATA_DIR / "Tabela_Docente_2025.parquet",
        columns=["CO_ENTIDADE", "QT_DOC_BAS"],
    )


@st.cache_data(show_spinner="Carregando dados de turmas...")
def load_turma():
    return pd.read_parquet(
        DATA_DIR / "Tabela_Turma_2025.parquet",
        columns=["CO_ENTIDADE", "QT_TUR_BAS"],
    )


@st.cache_data(show_spinner="Processando dados...")
def load_merged():
    escola = load_escola()
    mat = load_matricula()
    doc = load_docente()
    tur = load_turma()

    df = escola.merge(mat, on="CO_ENTIDADE", how="left")
    df = df.merge(doc, on="CO_ENTIDADE", how="left")
    df = df.merge(tur, on="CO_ENTIDADE", how="left")

    int_cols = [
        "QT_MAT_BAS", "QT_MAT_INF", "QT_MAT_INF_CRE", "QT_MAT_INF_PRE",
        "QT_MAT_FUND", "QT_MAT_FUND_AI", "QT_MAT_FUND_AF",
        "QT_MAT_MED", "QT_MAT_EJA", "QT_MAT_PROF",
        "QT_DOC_BAS", "QT_TUR_BAS",
        "QT_PROF_PSICOLOGO", "QT_PROF_ASSIST_SOCIAL",
    ]

    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    return df