import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import (
    load_merged, DEPENDENCIA_COLORS, fmt_int, fmt_dec,
)

# setando configurações da página e estilos customizados
st.set_page_config(page_title="Relatorio - Censo Escolar 2025", layout="wide")
st.markdown(
    """<style>
    .block-container {
        padding-top: 1.5rem;
    }

    div[data-testid="stHorizontalBlock"] {
        align-items: start !important;
    }

    div[data-testid="column"] {
        align-self: stretch !important;
    }

    div[data-testid="column"] > div {
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    div[data-testid="stMetric"] {
        background: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: .5rem;
        padding: .8rem 1rem;
        min-height: 120px;
        box-sizing: border-box;
        width: 100%;
        margin-top: 0 !important;
    }

    .metric-destaque div[data-testid="stMetric"] {
        border-left: 0px solid #636EFA !important;
    }
    </style>""",
    unsafe_allow_html=True,
)

st.title("Relatorio - Censo Escolar 2025")
st.markdown(
    """
    <div style="
        background: linear-gradient(to right, rgba(99, 110, 250, 0.05), rgba(239, 85, 59, 0.05));
        border-left: 4px solid #636EFA;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 24px;
    ">
        <p style="
            margin: 0;
            font-size: 15px;
            line-height: 1.6;
            color: #555;
        ">
            📊 <strong>Explore os dados do Censo Escolar com filtros interativos</strong><br>
            <span style="font-size: 13px; color: #777;">
                Os dados são provenientes do INEP e foram processados para esta aplicação, as regras para escolas analisas podem ser encontradas no Site do INEP.<br>
                Selecione os filtros desejados para analisar as escolas brasileiras.
            </span>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
df = load_merged()

# Card autor
st.sidebar.markdown(
    """
    <div style="
        background: linear-gradient(135deg, rgba(99, 110, 250, 0.1), rgba(239, 85, 59, 0.1));
        border: 1px solid rgba(99, 110, 250, 0.3);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <p style="
            margin: 0;
            font-size: 14px;
            color: #888;
            font-weight: 500;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        ">Elaborado por</p>
        <a href="https://www.linkedin.com/in/christianbasilioo/" target="_blank" style="
            font-size: 18px;
            font-weight: 600;
            color: #636EFA;
            text-decoration: none;
            transition: all 0.3s ease;
        ">Christian Basilio</a>
    </div>
    """,
    unsafe_allow_html=True
)
# Filtros

st.sidebar.header("Filtros")

# Regiao
regioes = sorted(df["NO_REGIAO"].dropna().unique())
sel_regioes = st.sidebar.multiselect("Regiao", regioes)

# Estado
if sel_regioes:
    ufs_disp = sorted(df.loc[df["NO_REGIAO"].isin(sel_regioes), "SG_UF"].dropna().unique())
else:
    ufs_disp = sorted(df["SG_UF"].dropna().unique())
sel_ufs = st.sidebar.multiselect("Estado (UF)", ufs_disp)

# Municipio
if sel_ufs:
    mun_disp = sorted(df.loc[df["SG_UF"].isin(sel_ufs), "NO_MUNICIPIO"].dropna().unique())
    sel_mun = st.sidebar.multiselect("Municipio", mun_disp)
else:
    sel_mun = []

# Dependencia
deps_disp = sorted(df["Dependencia"].dropna().unique())
sel_deps = st.sidebar.multiselect("Dependencia Administrativa", deps_disp)

# Localizacao
locs_disp = sorted(df["Localizacao"].dropna().unique())
sel_locs = st.sidebar.multiselect("Localizacao", locs_disp)

# Infraestrutura
st.sidebar.subheader("Infraestrutura")
INFRA_FILTERS = {
    "Com Internet": ("IN_INTERNET", 1),
    "Sem Internet": ("IN_INTERNET", 0),
    "Com Biblioteca": ("IN_BIBLIOTECA", 1),
    "Com Lab. Informatica": ("IN_LABORATORIO_INFORMATICA", 1),
    "Com Lab. Ciencias": ("IN_LABORATORIO_CIENCIAS", 1),
    "Com Quadra Esportes": ("IN_QUADRA_ESPORTES", 1),
    "Com Alimentacao": ("IN_ALIMENTACAO", 1),
    "Sem Esgoto": ("IN_ESGOTO_INEXISTENTE", 1),
    "Sem Agua": ("IN_AGUA_INEXISTENTE", 1),
    "Sem Energia": ("IN_ENERGIA_INEXISTENTE", 1),
    "Sem Acessibilidade": ("IN_ACESSIBILIDADE_INEXISTENTE", 1),
}
sel_infra = st.sidebar.multiselect("Filtrar por Infraestrutura", list(INFRA_FILTERS.keys()))

# Matriculas
st.sidebar.subheader("Matriculas")
min_mat = st.sidebar.number_input("Matriculas minimas (Ed. Basica)", min_value=0, value=0, step=10)
max_mat = st.sidebar.number_input(
    "Matriculas maximas (Ed. Basica)", min_value=0, value=0, step=10,
    help="Deixe 0 para sem limite",
)

# Botao limpar
if st.sidebar.button("Limpar todos os filtros"):
    st.rerun()

# aplicação dos filtros
mask = pd.Series(True, index=df.index)

if sel_regioes:
    mask &= df["NO_REGIAO"].isin(sel_regioes)
if sel_ufs:
    mask &= df["SG_UF"].isin(sel_ufs)
if sel_mun:
    mask &= df["NO_MUNICIPIO"].isin(sel_mun)
if sel_deps:
    mask &= df["Dependencia"].isin(sel_deps)
if sel_locs:
    mask &= df["Localizacao"].isin(sel_locs)

for label in sel_infra:
    col, val = INFRA_FILTERS[label]
    mask &= df[col] == val

if min_mat > 0:
    mask &= df["QT_MAT_BAS"] >= min_mat
if max_mat > 0:
    mask &= df["QT_MAT_BAS"] <= max_mat

dff = df[mask]

# Indicadores principais
total = len(dff)
pct = (total / len(df) * 100) if len(df) else 0
total_mat = int(dff["QT_MAT_BAS"].sum())
total_doc = int(dff["QT_DOC_BAS"].sum())
media_mat_escola = total_mat / total if total else 0
mat_por_doc = total_mat / total_doc if total_doc else 0

c1, c2, c3 = st.columns(3)
c1.metric("Escolas filtradas", fmt_int(total))
c2.metric("% do total", fmt_dec(pct, 2) + "%")
c3.metric("Matriculas", fmt_int(total_mat))

c4, c5, c6 = st.columns(3)
c4.metric("Docentes", fmt_int(total_doc))
c5.metric("Mat./Escola", fmt_dec(media_mat_escola, 2))
c6.metric("Mat./Docente", fmt_dec(mat_por_doc, 2))

st.divider()

# Abas
tab_dados, tab_infra, tab_mat, tab_geo = st.tabs(
    ["Dados", "Infraestrutura", "Matriculas", "Analise Geografica"]
)

# ── Aba dados
with tab_dados:
    st.subheader("Tabela de Escolas")
    # Card: % escolas sem psicologos e sem assistentes sociais
    total_escolas = len(dff)
    if total_escolas > 0:
        sem_psi = int((dff["QT_PROF_PSICOLOGO"] == 0).sum())
        sem_as = int((dff["QT_PROF_ASSIST_SOCIAL"] == 0).sum())
        pct_sem_psi = sem_psi / total_escolas * 100
        pct_sem_as = sem_as / total_escolas * 100
    else:
        sem_psi = sem_as = 0
        pct_sem_psi = pct_sem_as = 0.0

    cp1, cp2 = st.columns(2)
    cp1.metric("Escolas sem Psicologos", f"{fmt_dec(pct_sem_psi, 2)}%", help=f"{fmt_int(sem_psi)} de {fmt_int(total_escolas)} escolas")
    cp2.metric("Escolas sem Assist. Sociais", f"{fmt_dec(pct_sem_as, 2)}%", help=f"{fmt_int(sem_as)} de {fmt_int(total_escolas)} escolas")

    busca = st.text_input("Buscar escola por nome", placeholder="Digite o nome da escola...")

    display_cols = {
        "NO_ENTIDADE": "Escola",
        "Dependencia": "Dependencia",
        "NO_MUNICIPIO": "Municipio",
        "SG_UF": "UF",
        "NO_REGIAO": "Regiao",
        "Localizacao": "Localizacao",
        "QT_MAT_BAS": "Matriculas",
        "QT_DOC_BAS": "Docentes",
        "QT_TUR_BAS": "Turmas",
        "QT_SALAS_UTILIZADAS": "Salas",
        "IN_INTERNET": "Internet",
        "IN_BIBLIOTECA": "Biblioteca",
        "IN_LABORATORIO_INFORMATICA": "Lab. Info.",
        "IN_QUADRA_ESPORTES": "Quadra",
        "IN_ALIMENTACAO": "Alimentacao",
        "QT_PROF_PSICOLOGO": "Psicologos",
        "QT_PROF_ASSIST_SOCIAL": "Assist. Sociais",
    }

    df_table = dff[list(display_cols.keys())].rename(columns=display_cols).copy()

    # Matriculas por Docente
    mat_num = pd.to_numeric(df_table["Matriculas"], errors="coerce").fillna(0).astype(float)
    doc_num = pd.to_numeric(df_table["Docentes"], errors="coerce").fillna(0).astype(float)
    df_table["Mat./Docente"] = (mat_num / doc_num.replace(0.0, float("nan"))).round(2)

    # Psicologos por 100 alunos
    psi_num = pd.to_numeric(df_table["Psicologos"], errors="coerce").fillna(0).astype(float)
    df_table["Psic./100 alunos"] = (psi_num / mat_num.replace(0.0, float("nan")) * 100).round(4)

    # Assistentes Sociais por 100 alunos
    ass_num = pd.to_numeric(df_table["Assist. Sociais"], errors="coerce").fillna(0).astype(float)
    df_table["AS/100 alunos"] = (ass_num / mat_num.replace(0.0, float("nan")) * 100).round(4)

    if busca:
        df_table = df_table[df_table["Escola"].str.contains(busca, case=False, na=False)]

    bool_cols = ["Internet", "Biblioteca", "Lab. Info.", "Quadra", "Alimentacao"]
    for col in bool_cols:
        df_table[col] = df_table[col].map({1: "Sim", 0: "Nao"})

    st.dataframe(
        df_table.reset_index(drop=True),
        use_container_width=True,
        height=500,
    )

    st.caption(f"Exibindo {fmt_int(len(df_table))} escolas")

    # Download
    csv = dff.to_csv(index=False, sep=";", encoding="utf-8-sig")
    st.download_button(
        "Baixar dados filtrados (CSV)",
        csv, "censo_escolar_filtrado.csv", "text/csv",
    )

    st.divider()

    col_d1, col_d2 = st.columns(2)

    with col_d1:
        st.subheader("Mat./Docente por Dependencia")
        mat_doc_dep = dff.groupby("Dependencia").agg(
            Matriculas=("QT_MAT_BAS", "sum"),
            Docentes=("QT_DOC_BAS", "sum"),
        ).reset_index()
        mat_doc_dep["Mat./Docente"] = (
            mat_doc_dep["Matriculas"] / mat_doc_dep["Docentes"].replace(0, float("nan"))
        ).round(2)
        fig = px.bar(
            mat_doc_dep, x="Dependencia", y="Mat./Docente",
            text="Mat./Docente", color="Dependencia",
            color_discrete_map=DEPENDENCIA_COLORS,
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Matriculas por Docente", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col_d2:
        st.subheader("Mat./Docente por Localizacao")
        mat_doc_loc = dff.groupby("Localizacao").agg(
            Matriculas=("QT_MAT_BAS", "sum"),
            Docentes=("QT_DOC_BAS", "sum"),
        ).reset_index()
        mat_doc_loc["Mat./Docente"] = (
            mat_doc_loc["Matriculas"] / mat_doc_loc["Docentes"].replace(0, float("nan"))
        ).round(2)
        fig = px.bar(
            mat_doc_loc, x="Localizacao", y="Mat./Docente",
            text="Mat./Docente",
            color="Localizacao",
            color_discrete_map={"Urbana": "#636EFA", "Rural": "#EF553B"},
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Matriculas por Docente", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ── Aba infraestrutura
with tab_infra:
    st.subheader("Cobertura de Infraestrutura")

    INFRA_INDICATORS = {
        "Alimentacao": "IN_ALIMENTACAO",
        "Cozinha": "IN_COZINHA",
        "Energia Publica": "IN_ENERGIA_REDE_PUBLICA",
        "Agua Publica": "IN_AGUA_REDE_PUBLICA",
        "Agua Potavel": "IN_AGUA_POTAVEL",
        "Internet": "IN_INTERNET",
        "Banda Larga": "IN_BANDA_LARGA",
        "Computador": "IN_COMPUTADOR",
        "Esgoto Publico": "IN_ESGOTO_REDE_PUBLICA",
        "Biblioteca": "IN_BIBLIOTECA",
        "Patio Coberto": "IN_PATIO_COBERTO",
        "Refeitorio": "IN_REFEITORIO",
        "Quadra Esportes": "IN_QUADRA_ESPORTES",
        "Lab. Informatica": "IN_LABORATORIO_INFORMATICA",
        "Lab. Ciencias": "IN_LABORATORIO_CIENCIAS",
        "Banheiro PNE": "IN_BANHEIRO_PNE",
        "Auditorio": "IN_AUDITORIO",
    }

    # Geral
    rows = []
    for label, col in INFRA_INDICATORS.items():
        pct = dff[col].mean() * 100
        rows.append({"Indicador": label, "Percentual": pct})
    infra_geral = pd.DataFrame(rows).sort_values("Percentual", ascending=True)

    fig = px.bar(
        infra_geral, x="Percentual", y="Indicador", orientation="h",
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_traces(texttemplate="%{x:.2f}%", textposition="outside")
    fig.update_layout(
        yaxis_title="", xaxis_title="% das Escolas",
        height=550, margin=dict(t=10, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Comparativo por dependencia
    st.subheader("Comparativo por Dependencia Administrativa")
    comp_dim = st.radio(
        "Comparar por:", ["Dependencia", "Localizacao"], horizontal=True,
        key="infra_comp",
    )
    sel_indicadores = st.multiselect(
        "Selecione indicadores para comparar",
        list(INFRA_INDICATORS.keys()),
        default=["Internet", "Biblioteca", "Lab. Informatica", "Quadra Esportes", "Alimentacao"],
    )

    if sel_indicadores:
        comp_rows = []
        for grupo in dff[comp_dim].dropna().unique():
            sub = dff[dff[comp_dim] == grupo]
            for label in sel_indicadores:
                col = INFRA_INDICATORS[label]
                pct = sub[col].mean() * 100
                comp_rows.append({comp_dim: grupo, "Indicador": label, "Percentual": pct})

        comp_df = pd.DataFrame(comp_rows)
        fig = px.bar(
            comp_df, x="Indicador", y="Percentual", color=comp_dim,
            barmode="group", text_auto=".2f",
            color_discrete_map=DEPENDENCIA_COLORS if comp_dim == "Dependencia" else None,
        )
        fig.update_layout(
            yaxis_title="% das Escolas", xaxis_title="",
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Aba matriculas
with tab_mat:
    st.subheader("Distribuicao de Matriculas")

    niveis = {
        "Creche": int(dff["QT_MAT_INF_CRE"].sum()),
        "Pre-escola": int(dff["QT_MAT_INF_PRE"].sum()),
        "Fund. Anos Iniciais": int(dff["QT_MAT_FUND_AI"].sum()),
        "Fund. Anos Finais": int(dff["QT_MAT_FUND_AF"].sum()),
        "Ensino Medio": int(dff["QT_MAT_MED"].sum()),
        "EJA": int(dff["QT_MAT_EJA"].sum()),
        "Profissional": int(dff["QT_MAT_PROF"].sum()),
    }
    mat_df = pd.DataFrame(list(niveis.items()), columns=["Nivel", "Matriculas"])

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        fig = px.bar(mat_df, x="Nivel", y="Matriculas", color="Nivel", text_auto=".3s")
        fig.update_layout(
            showlegend=False, xaxis_title="", yaxis_title="Matriculas",
            height=400, xaxis_tickangle=-30,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_m2:
        fig = px.pie(mat_df, values="Matriculas", names="Nivel", hole=0.35)
        fig.update_traces(textposition="inside", textinfo="percent+label")
        fig.update_layout(showlegend=False, height=400, margin=dict(t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    # Matriculas por dependencia
    st.subheader("Matriculas por Dependencia")
    mat_dep = dff.groupby("Dependencia").agg(
        Total=("QT_MAT_BAS", "sum"),
        Infantil=("QT_MAT_INF", "sum"),
        Fundamental=("QT_MAT_FUND", "sum"),
        Medio=("QT_MAT_MED", "sum"),
        EJA=("QT_MAT_EJA", "sum"),
        Profissional=("QT_MAT_PROF", "sum"),
    ).reset_index()

    mat_dep_long = mat_dep.melt(
        id_vars="Dependencia",
        value_vars=["Infantil", "Fundamental", "Medio", "EJA", "Profissional"],
        var_name="Nivel", value_name="Matriculas",
    )

    fig = px.bar(
        mat_dep_long, x="Dependencia", y="Matriculas", color="Nivel",
        barmode="group", text_auto=".3s",
    )
    fig.update_layout(xaxis_title="", yaxis_title="Matriculas", height=450)
    st.plotly_chart(fig, use_container_width=True)

    # Top municipios por matriculas
    st.subheader("Top 20 Municipios por Matriculas")
    top_mun = dff.groupby(["NO_MUNICIPIO", "SG_UF"])["QT_MAT_BAS"].sum().reset_index()
    top_mun.columns = ["Municipio", "UF", "Matriculas"]
    top_mun["Label"] = top_mun["Municipio"] + " - " + top_mun["UF"]
    top_mun = top_mun.nlargest(20, "Matriculas").sort_values("Matriculas", ascending=True)

    fig = px.bar(top_mun, x="Matriculas", y="Label", orientation="h",
                 text="Matriculas", color_discrete_sequence=["#636EFA"])
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(yaxis_title="", height=550, margin=dict(t=10, b=0))
    st.plotly_chart(fig, use_container_width=True)

# ── Aba analise geografica
with tab_geo:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Escolas por Estado")
        uf_data = dff.groupby("SG_UF").agg(
            Escolas=("CO_ENTIDADE", "size"),
            Matriculas=("QT_MAT_BAS", "sum"),
        ).reset_index().sort_values("Escolas", ascending=True)
        fig = px.bar(uf_data, x="Escolas", y="SG_UF", orientation="h",
                     text="Escolas", color_discrete_sequence=["#636EFA"])
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis_title="", height=600, margin=dict(t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    with col_g2:
        st.subheader("Matriculas por Estado")
        uf_data2 = uf_data.sort_values("Matriculas", ascending=True)
        fig = px.bar(uf_data2, x="Matriculas", y="SG_UF", orientation="h",
                     text="Matriculas", color_discrete_sequence=["#EF553B"])
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        fig.update_layout(yaxis_title="", height=600, margin=dict(t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)
    # Escolas por regiao + dependencia
    st.subheader("Escolas por Regiao e Dependencia")
    reg_dep = dff.groupby(["NO_REGIAO", "Dependencia"]).size().reset_index(name="Qtd")
    fig = px.bar(
        reg_dep, x="NO_REGIAO", y="Qtd", color="Dependencia",
        text="Qtd",
        color_discrete_map=DEPENDENCIA_COLORS,
        barmode="group",
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(xaxis_title="Regiao", yaxis_title="Quantidade", height=400)
    st.plotly_chart(fig, use_container_width=True)
    # Mapa
    st.subheader("Mapa")
    df_map = dff.dropna(subset=["LATITUDE", "LONGITUDE"]).copy()
    map_limit = 10_000
    if len(df_map) > map_limit:
        df_map = df_map.sample(map_limit, random_state=42)
    if len(df_map) > 0:
        import math
        lat_min, lat_max = df_map["LATITUDE"].min(), df_map["LATITUDE"].max()
        lon_min, lon_max = df_map["LONGITUDE"].min(), df_map["LONGITUDE"].max()
        center_lat = (lat_min + lat_max) / 2
        center_lon = (lon_min + lon_max) / 2
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        max_range = max(lat_range, lon_range, 0.01)
        zoom = max(1, math.floor(8.5 - math.log2(max_range + 0.01)))

        fig = px.scatter_map(
            df_map, lat="LATITUDE", lon="LONGITUDE",
            color="Dependencia", color_discrete_map=DEPENDENCIA_COLORS,
            hover_name="NO_ENTIDADE",
            hover_data={
                "Dependencia": True,
                "NO_MUNICIPIO": True,
                "SG_UF": True,
                "Localizacao": True,
                "QT_MAT_BAS": True,
                "QT_DOC_BAS": True,
                "QT_PROF_PSICOLOGO": True,
                "QT_PROF_ASSIST_SOCIAL": True,
                "LATITUDE": False,
                "LONGITUDE": False,
            },
            labels={
                "NO_MUNICIPIO": "Municipio",
                "SG_UF": "UF",
                "QT_MAT_BAS": "Matriculas",
                "QT_DOC_BAS": "Docentes",
                "QT_PROF_PSICOLOGO": "Psicologos",
                "QT_PROF_ASSIST_SOCIAL": "Assist. Sociais",
            },
            zoom=zoom, center={"lat": center_lat, "lon": center_lon}, height=500,
        )
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhuma escola com coordenadas para os filtros selecionados.")
