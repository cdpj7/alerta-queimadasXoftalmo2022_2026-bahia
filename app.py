import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configuração da Página
st.set_page_config(page_title="Alerta Epidemiológico: Bahia", layout="wide")
st.title("Sazonalidade dos Focos de Calor e Urgências Oftalmológicas (2022-2026)")

# Lendo e processando os dados reais
@st.cache_data
def carregar_dados_integrados():
    df_inpe = pd.read_csv('inpe_focos.csv') 
    df_inpe['Data_Processamento'] = pd.to_datetime(df_inpe['DataHora']).dt.to_period('M').dt.to_timestamp()
    df_inpe_mensal = df_inpe.groupby('Data_Processamento').size().reset_index(name='Focos_INPE')
    
    df_sus = pd.read_csv('datasus.csv', sep=',')
    df_sus['Data_Processamento'] = pd.to_datetime(df_sus['Data'])
    df_sus = df_sus[['Data_Processamento', 'Urgencias_SUS']]
    
    df_final = pd.merge(df_inpe_mensal, df_sus, on='Data_Processamento', how='left')
    df_final = df_final[df_final['Data_Processamento'] >= '2022-01-01']
    
    # Criando meses futuros APENAS para desenhar a área vermelha no gráfico
    datas_futuras = pd.date_range(start="2026-10-01", end="2027-04-01", freq="MS")
    df_futuro = pd.DataFrame({'Data_Processamento': datas_futuras})
    df_final = pd.concat([df_final, df_futuro], ignore_index=True)
    
    return df_final

dados = carregar_dados_integrados()

# Construção do Gráfico
figura = make_subplots(specs=[[{"secondary_y": True}]])

figura.add_trace(go.Bar(x=dados['Data_Processamento'], y=dados['Focos_INPE'], name="Focos de Calor (INPE)", marker_color="rgba(215, 60, 20, 0.85)"), secondary_y=False)
figura.add_trace(go.Scatter(x=dados['Data_Processamento'], y=dados['Urgencias_SUS'], name="Atendimentos Oftalmológicos", mode="lines+markers", connectgaps=False, line=dict(color="rgba(0, 70, 180, 1.0)", width=3.5), marker=dict(size=7)), secondary_y=True)

# Zona de Alerta
figura.add_vrect(x0="2026-12-01", x1="2027-03-31", fillcolor="red", opacity=0.20, line_width=1, line_dash="dot", line_color="darkred")

# ==========================================
# TRAVA CONTRA ZOOM NO CELULAR (dragmode=False)
# ==========================================
figura.update_layout(
    title_text="<b>Correlação Histórica e Projeção do Impacto do Ar Particulado</b>",
    hovermode="x unified",
    plot_bgcolor='rgb(250,250,250)',
    height=500, 
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    dragmode=False # Desativa arrastar a tela no gráfico
)

# Trava (fixedrange=True) em cada um dos eixos
figura.update_xaxes(title_text="", showgrid=True, gridcolor='lightgray', tickfont=dict(color='black', family='Arial Black'), fixedrange=True)
figura.update_yaxes(title_text="<b>Focos de Calor</b>", secondary_y=False, showgrid=False, tickfont=dict(color='black', family='Arial Black'), fixedrange=True)
figura.update_yaxes(title_text="<b>Atendimentos Médicos</b>", secondary_y=True, showgrid=True, gridcolor='lightgray', tickfont=dict(color='black', family='Arial Black'), fixedrange=True)

st.plotly_chart(figura, use_container_width=True, config={'displayModeBar': False})

# ==========================================
# MATERIAL SUPLEMENTAR E METODOLOGIA
# ==========================================
st.markdown("---")
st.header("📄 Ficha Metodológica e Dados Brutos")
st.write("Para garantir a transparência e reprodutibilidade do estudo apresentado no e-pôster, abaixo constam os parâmetros exatos utilizados na extração de dados públicos.")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **Dados Clínicos (SIA / DATASUS)**
    * **Filtro de Local:** Estado da Bahia
    * **Grupo de Procedimento:** 03 - Procedimentos Clínicos
    * **Profissional (CBO):** 223144 e 225265 (Médico Oftalmologista)
    * **Conteúdo Avaliado:** Quantidade Aprovada
    """)

with col2:
    st.warning("""
    **Dados Ambientais (BDQueimadas / INPE)**
    * **Filtro de Local:** Estado da Bahia (Todos os biomas)
    * **Satélite de Referência:** AQUA_M-T (Aqua Tarde)
    * **Dado Extraído:** Soma mensal absoluta de focos de calor.
    """)

with st.expander("📊 Clique aqui para visualizar a Tabela de Dados Integrados (INPE x SUS)"):
    # Prepara a tabela para exibição
    tabela_bonita = dados.copy()
    tabela_bonita.columns = ['Mês/Ano', 'Focos de Calor (INPE)', 'Atendimentos Médicos (SUS)']
    tabela_bonita['Mês/Ano'] = tabela_bonita['Mês/Ano'].dt.strftime('%m/%Y')
    
    # SOLUÇÃO DOS "NONE":
    # 1. Exclui da tabela os meses futuros (onde tanto INPE quanto SUS estão vazios)
    tabela_bonita = tabela_bonita.dropna(how='all', subset=['Focos de Calor (INPE)', 'Atendimentos Médicos (SUS)'])
    # 2. Nos meses recentes (ex: atraso de 1 mês do SUS), troca o None por um traço '-'
    tabela_bonita = tabela_bonita.fillna('-')
    
    st.dataframe(tabela_bonita, use_container_width=True, hide_index=True)