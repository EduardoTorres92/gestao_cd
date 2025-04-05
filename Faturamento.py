import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def exibir_graficos():
    st.title("📈 Dashboard CD - Abril 2024")
    # Criar df_faturamento e df_devolucao com tratamentos diferentes
    df_faturamento = pd.read_parquet('Datasets/ESFT0100_atual.parquet')
    df_faturamento = df_faturamento[df_faturamento["estado"] != "EX"]

    # FATURAMENTO
    operacoes_faturamento = ['1 - Receita', '20 - Receita Revenda', '15 - Transferencia', 
                            '2 - Receita Export', '3 - Receita Rem Vend Futura', '18 - Venda a ordem']
    df_faturamento = df_faturamento[df_faturamento["tipo_oper"].isin(operacoes_faturamento)]
    # DEVOLUÇÃO
    df_devolucao = pd.read_parquet('Datasets/ESFT0100_atual.parquet')
    df_devolucao = df_devolucao[df_devolucao["tipo_oper"] == "5 - Dev Venda"]
    df_devolucao = df_devolucao[df_devolucao["estado"] != "EX"]
    df_faturamento = df_faturamento[df_faturamento["marca"] != "YALE"]

    # Calcular faturamento por marca considerando devoluções
    faturamento_marca = df_faturamento.groupby("marca")["vl_net_livro"].sum()
    devolucao_marca = df_devolucao.groupby("marca")["vl_net_livro"].sum()

    faturamento_liquido = faturamento_marca - devolucao_marca
    faturamento_liquido = faturamento_liquido.fillna(0)  # Substitui NaN por 0

    cores_marca = {
        'PAPAIZ': 'blue',
        'YALE': 'yellow',
        'LA FONTE': 'darkred',
        'SILVANA CDSP': 'orange',
        'VAULT': 'gray',
        'Total': 'darkgreen',
    }

    # Garantir que todas as marcas existam, mesmo sem devolução
    devolucao_marca = devolucao_marca.reindex(faturamento_marca.index, fill_value=0)

    # Agora a subtração funciona corretamente
    faturamento_liquido = faturamento_marca - devolucao_marca

    # Exibir faturamento em cards no Streamlit
    st.subheader("Faturamento Líquido por Marca")
    colunas = st.columns(len(faturamento_liquido))

    for i, (marca, valor) in enumerate(faturamento_liquido.items()):
        with colunas[i]:
            st.markdown(f"### {marca}")
            st.markdown(f"**R$ {valor:,.2f}**")

    ####

    st.divider()  # Adiciona uma linha separadora

    st.subheader("Média de SKUs e Peças Faturadas por Funcionário (por Marca)")

    # Input para número de funcionários no dia anterior
    num_funcionarios = st.number_input("Quantidade de Funcionários no Dia Anterior:", min_value=1, step=1, value=11)

    # Filtrar dados do dia anterior
    dia_anterior = (pd.to_datetime("today") - pd.Timedelta(days=1)).date()
    df_faturamento_ontem = df_faturamento[df_faturamento["dt_emis_nf"].dt.date == dia_anterior]

    # Remover a marca "LA FONTE"
    df_faturamento_ontem = df_faturamento_ontem[df_faturamento_ontem["marca"] != "LA FONTE"]

    # Calcular métricas por marca
    if num_funcionarios > 0:
        skus_por_marca = df_faturamento_ontem.groupby("marca")["item"].nunique() / num_funcionarios
        pecas_por_marca = df_faturamento_ontem.groupby("marca")["quantidade"].sum() / num_funcionarios

        # Criar DataFrame formatado
        df_resultado = pd.DataFrame({
            "Marca": skus_por_marca.index,
            "SKUs": skus_por_marca.values.round(2),
            "Peças": pecas_por_marca.values.round(2)
        }).reset_index(drop=True)

        # Exibir DataFrame no Streamlit
        st.dataframe(df_resultado, use_container_width=True)
    else:
        st.warning("Defina um número válido de funcionários para calcular as médias.")

    ###
    st.divider()  # Adiciona uma linha separadora


    ####
    st.subheader("Selecione um Período para Análise")

    # Criar filtro de data no Streamlit
    col1, col2 = st.columns(2)
    with col1:
        data_inicial = st.date_input("Data Inicial", min(df_faturamento["dt_emis_nf"]))
    with col2:
        data_final = st.date_input("Data Final", max(df_faturamento["dt_emis_nf"]))

    # Converter para formato datetime
    data_inicial = pd.to_datetime(data_inicial)
    data_final = pd.to_datetime(data_final)

    # Filtrar dataframe pelo período selecionado
    df_filtrado = df_faturamento[(df_faturamento["dt_emis_nf"] >= data_inicial) & (df_faturamento["dt_emis_nf"] <= data_final)]

    # Criar DataFrame com as métricas por marca
    df_resumo = df_filtrado.groupby("marca").agg(
        Quantidade_NFs=("nota_fiscal", lambda x: x.nunique()),  # Considera apenas NFs únicas
        Quantidade_SKUs=("item", "nunique"),
        Quantidade_Pecas=("quantidade", "sum")
    ).reset_index()

    # Exibir DataFrame no Streamlit
    st.subheader("Resumo de Faturamento por Marca")
    st.dataframe(df_resumo)


    #######

    # Gráfico de faturamento geral diário (linha)
    st.subheader("Faturamento Geral Diário")

    # Criar DataFrame com agrupamento diário
    faturamento_diario = df_faturamento.groupby("dt_emis_nf", as_index=False)["vl_net_livro"].sum()

    # Criar figura
    fig, ax = plt.subplots(figsize=(12, 6))

    # Criar gráfico de linha com Seaborn
    sns.lineplot(
        data=faturamento_diario, 
        x="dt_emis_nf", 
        y="vl_net_livro", 
        marker="o", 
        linestyle="-", 
        color="blue", 
        ax=ax
    )

    # Exibir valores nos pontos
    for x, y in zip(faturamento_diario["dt_emis_nf"], faturamento_diario["vl_net_livro"]):
        ax.annotate(f"{y:,.2f}", 
                    xy=(x, y), 
                    xytext=(5, 5), 
                    textcoords="offset points", 
                    ha='left', va='bottom', 
                    fontsize=9, color='black', fontweight='bold')

    # Configurar eixos e título
    ax.set_title("Faturamento Geral Diário")
    ax.set_xlabel("Data")
    ax.set_ylabel("Faturamento (R$)")
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    # Melhorar a rotação dos rótulos do eixo X
    plt.xticks(rotation=45)

    # Exibir no Streamlit
    st.pyplot(fig)



    # Gráfico de faturamento diário por marca (barras)
    # Criar coluna de data sem hora
    df_faturamento["data_apenas"] = df_faturamento["dt_emis_nf"].dt.date

    # Selecionar marcas desejadas
    marcas_desejadas = ["PAPAIZ", "LA FONTE", "SILVANA CDSP", "VAULT"]
    df_filtrado = df_faturamento[df_faturamento["marca"].isin(marcas_desejadas)]

    # Criar figura
    st.subheader("Faturamento Diário por Marca")
    fig, ax = plt.subplots(figsize=(14, 6))

    sns.barplot(
        data=df_filtrado, 
        x="data_apenas", 
        y="vl_net_livro", 
        hue="marca", 
        palette=cores_marca, 
        ax=ax,
        errorbar=None  # Remove as barras de erro
    )

    # Adicionar valores sobre as barras
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)

    # Configurar layout
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    ax.set_title("Faturamento Diário por Marca")
    ax.set_xlabel("Data")
    ax.set_ylabel("Faturamento (R$)")
    ax.legend(title="Marca")
    ax.grid(axis='y', linestyle='-.', alpha=0.2)

    # Exibir no Streamlit
    st.pyplot(fig)
        
    # Lista para armazenar figuras para exportação
    figures = []




    st.divider()  # Adiciona uma linha separadora

    # Configuração do Seaborn
    sns.set_theme(style="whitegrid")

    # Criar DataFrames agregados para devoluções por marca e canal
    devolucao_marca = df_devolucao["marca"].value_counts().reset_index()
    devolucao_marca.columns = ["Marca", "Quantidade"]

    devolucao_canal = df_devolucao["canal_venda_cliente"].value_counts().reset_index()
    devolucao_canal.columns = ["Canal de Venda", "Quantidade"]

    # Criar gráficos de devolução
    st.title("📉 Quantidade de Devoluções por Marca e Canal")
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

    # Devoluções por Marca
    sns.barplot(x="Marca", y="Quantidade", data=devolucao_marca, ax=axes[0], palette="Blues_r")
    axes[0].set_title("Quantidade de Devoluções por Marca", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Quantidade")
    axes[0].set_xlabel("")
    axes[0].set_xticklabels(devolucao_marca["Marca"], rotation=45)

    # Exibir valores acima das barras
    for bar in axes[0].containers:
        axes[0].bar_label(bar, fmt="%d", fontsize=10, padding=3)

    # Devoluções por Canal de Venda
    sns.barplot(x="Canal de Venda", y="Quantidade", data=devolucao_canal, ax=axes[1], palette="Greens_r")
    axes[1].set_title("Quantidade de Devoluções por Canal de Venda", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Quantidade")
    axes[1].set_xlabel("")
    axes[1].set_xticklabels(devolucao_canal["Canal de Venda"], rotation=45)

    # Exibir valores acima das barras
    for bar in axes[1].containers:
        axes[1].bar_label(bar, fmt="%d", fontsize=10, padding=3)

    plt.tight_layout()
    st.pyplot(fig)
    figures.append(fig)  # Salva o gráfico de devoluções