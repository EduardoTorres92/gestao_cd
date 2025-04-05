import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

if not st.runtime.exists():  # Isso evita conflitos no multipage
    st.set_page_config(...)

# -----------------------
# CARREGAR E TRATAR OS DADOS
# -----------------------
potencial = pd.read_excel('Datasets/esgr0050.xlsx', skiprows=1)
potencial = potencial[potencial['Estab'] == 206]
potencial.columns = potencial.columns.str.strip()


# SItuação REmover Checkout e Faturado 
# Remover Exportação
# Data do embarque = tudo
# canal de venda, desconsiderar intercompany, exportação,
# -----------------------
# MAPEAMENTO DE STATUS COM EMOJIS
# -----------------------
status_emojis = {
    'Embarque': '📦 Embarque',
    'Emb Impres': '🖨️ Impresso',
    'Checkout': '🛒 Checkout',
    'Faturado': '💰 Faturado'
}

# Aplicar o mapeamento
potencial['Situação Formatada'] = potencial['Situação'].map(status_emojis)

def exibir_potencial():
    st.title("🎯 Potencial de Vendas")
    st.subheader("Análise do Potencial de Vendas por Cliente")

    # Exibir tabela com os dados
    st.dataframe(potencial)

    # Gráfico de barras
    plt.figure(figsize=(12, 6))
    sns.countplot(data=potencial, x='Situação Formatada', order=potencial['Situação Formatada'].value_counts().index)
    plt.title('Distribuição do Potencial de Vendas por Situação')
    plt.xlabel('Situação')
    plt.ylabel('Contagem')
    plt.xticks(rotation=45)
    st.pyplot(plt)  # Exibir o gráfico no Streamlit