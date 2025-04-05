import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------
# CARREGAR E TRATAR OS DADOS
# -----------------------

@st.cache_data
def carregar_dados():
    leadtime_diario = pd.read_parquet('Datasets/ESFT0100_atual.parquet')

    # Aplicar filtros
    leadtime_diario = leadtime_diario[
        (leadtime_diario["marca"] != "VAULT") &
        (leadtime_diario["estado"] != "EX") &
        (leadtime_diario["serie"] == "3") &
        (leadtime_diario["receita"] == True) &
        (leadtime_diario["canal_venda_cliente"] != "") &
        (leadtime_diario["canal_venda_cliente"].notna()) &
        (leadtime_diario["dt_embarque"] != "")
    ]

    # Preencher valores ausentes
    leadtime_diario['dt_aprov_credito'].fillna(leadtime_diario['dt_implant_ped'], inplace=True)
    leadtime_diario['dt_entrega'].fillna(leadtime_diario['dt_aprov_credito'], inplace=True)
    leadtime_diario['dt_emis_nf'].fillna(leadtime_diario['dt_embarque'], inplace=True)
    
    # Remover duplicatas
    leadtime_diario = leadtime_diario.drop_duplicates(subset=['nota_fiscal'])

    return leadtime_diario

# -----------------------
# CÁLCULO DE TMO EXPEDIÇÃO
# -----------------------

FERIADOS = [
    "2025-01-01", "2025-04-18", "2025-05-01", "2025-09-07",
    "2025-10-12", "2025-11-02", "2025-11-15", "2025-12-25"
]

def calcular_tmo_expedicao(row):
    start = row['dt_embarque']
    end = row['dt_emis_nf']
    if pd.isna(start) or pd.isna(end):
        return np.nan  
    if start == end:
        return 0  

    dec = 0 if end.weekday() in [5, 6] else 1  
    start_np = np.datetime64(start.date())
    end_np = np.datetime64(end.date()) + np.timedelta64(1, 'D')

    return np.busday_count(start_np, end_np, holidays=FERIADOS) - dec

# -----------------------
# GERAR GRÁFICOS
# -----------------------

CORES_MARCA = {
    'PAPAIZ': 'blue',
    'YALE': 'yellow',
    'LA FONTE': 'darkred',
    'SILVANA CDSP': 'orange',
    'VAULT': 'gray',
    'Total': 'darkgreen',
}

def exibir_graficos():
    st.title("📊 LEAD TIME EXPEDIÇÃO")

    leadtime_diario = carregar_dados()
    leadtime_diario["TMO_EXPEDICAO"] = leadtime_diario.apply(calcular_tmo_expedicao, axis=1)

    # -----------------------
    # LEAD TIME MÉDIO POR MARCA
    # -----------------------

    leadtime_marca = leadtime_diario.groupby("marca")["TMO_EXPEDICAO"].mean().round(2)
    leadtime_total = pd.Series({"TOTAL": leadtime_diario["TMO_EXPEDICAO"].mean().round(2)})
    leadtime_marca = pd.concat([leadtime_marca, leadtime_total])

    cores = [CORES_MARCA.get(marca, "gray") for marca in leadtime_marca.index]

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=leadtime_marca.index, y=leadtime_marca.values, ax=ax, palette=cores)
    ax.patches[-1].set_facecolor(CORES_MARCA.get("Total", "darkgreen"))

    for bar in ax.patches:
        ax.annotate(f"{bar.get_height():.2f}", 
                    (bar.get_x() + bar.get_width() / 2, bar.get_height()), 
                    ha='center', va='bottom', fontsize=10, color='black')

    ax.set_title("Lead Time Médio por Marca (e Total)", fontsize=14, fontweight="bold")
    ax.set_xlabel("")
    ax.set_ylabel("Dias")
    plt.xticks(rotation=45)

    st.pyplot(fig)

    # -----------------------
    # LEAD TIME DIÁRIO - GRÁFICO ÚNICO COM TODAS AS MARCAS
    # -----------------------

    st.subheader("Lead Time Diário por Marca")

    leadtime_agrupado = leadtime_diario.groupby(["dt_emis_nf", "marca"])["TMO_EXPEDICAO"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(14, 6))

        barplot = sns.barplot(
            data=leadtime_agrupado,
            x="dt_emis_nf",
            y="TMO_EXPEDICAO",
            hue="marca",
            palette=CORES_MARCA
        )

        ax.set_title("Lead Time Diário por Marca", fontsize=14, fontweight="bold")
        ax.set_xlabel("Data")
        ax.set_ylabel("Dias")
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        ax.set_xticklabels(leadtime_agrupado["dt_emis_nf"].dt.strftime("%d-%m").unique(), rotation=45)

        # 💬 Adicionar valor no topo de cada barra
        for bar in barplot.patches:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{height:.2f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 5),  # distância do topo da barra
                            textcoords='offset points',
                            ha='center', va='bottom',
                            fontsize=8, color='black')

        st.pyplot(fig)
