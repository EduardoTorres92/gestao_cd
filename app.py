import streamlit as st
import leadtime  # Importando o módulo de Lead Time
import Faturamento  # Importando o módulo de Faturamento
import Transporte  # Importando o módulo de Transporte
import Potencial  # Importando o módulo de Transporte

# Configuração inicial da página
st.set_page_config(
    page_title="DashBoard CD",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.sidebar.title("Navegação")
pagina = st.sidebar.radio("Selecione a Página:", ["📈 Faturamento", "📊 Lead Time", '🚛 Transportes', '🎯 Potencial'])

if pagina == "📈 Faturamento":
    Faturamento.exibir_graficos()  # Agora a função existe no módulo Faturamento

if pagina == '🚛 Transportes':
    Transporte.exibir_graficos()  # Chama os gráficos de transporte
    
if pagina == '🎯 Potencial':
    Potencial.exibir_potencial()  # Chama os gráficos de transporte

elif pagina == "📊 Lead Time":
    leadtime.exibir_graficos()  # Chama os gráficos de lead time