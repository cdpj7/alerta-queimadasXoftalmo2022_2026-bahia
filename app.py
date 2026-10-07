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
    # 1. Processar INPE
    df_inpe = pd.read_csv('inpe_focos.csv') 
    df_inpe['Data_Processamento'] = pd.to_datetime(df_inpe['DataHora']).dt.to_period('M').dt.to_timestamp()
    df_inpe_mensal = df_inpe.groupby('Data_Processamento').size().reset_index(name='Focos_INPE')
    
    # 2. Processar DATASUS
    df_sus = pd.read_csv('datasus.csv', sep=',')
    df_sus['Data_Processamento'] = pd.to_datetime(df_sus['Data'])
    df_sus = df_sus[['Data_Processamento', 'Urgencias_SUS']]
    
    # 3. Mesclar as tabelas
    df_final = pd.merge(df_inpe_mensal, df_sus, on='Data_Processamento', how='left')
    
    # 4. EXCLUIR 2021
    df_final = df_final[df_final['Data_Processamento'] >= '2022-01-01']
    
    # 5. Criar eixo temporal (Reduzido para acabar em Abril de 2027 e evitar espaços em branco)
    datas_futuras = pd.date_range(start="2026-10-01", end="2027-04-01", freq="MS")
    df_futuro = pd.DataFrame({'Data_Processamento': datas_futuras})
    df_final = pd.concat([df_final, df_futuro], ignore_index=True)
    
    return df_final

dados = carregar_dados_integrados()

# Construção do Gráfico
figura = make_subplots(specs=[[{"secondary_y": True}]])

# Colunas Laranjas (INPE)
figura.add_trace(
    go.Bar(
        x=dados['Data_Processamento'], 
        y=dados['Focos_INPE'], 
        name="Focos de Calor (INPE)",
        marker_color="rgba(215, 60, 20, 0.85)", 
    ),
    secondary_y=False,
)

# Linha Azul (SUS)
figura.add_trace(
    go.Scatter(
        x=dados['Data_Processamento'], 
        y=dados['Urgencias_SUS'], 
        name="Atendimentos Oftalmológicos",
        mode="lines+markers",
        connectgaps=False, 
        line=dict(color="rgba(0, 70, 180, 1.0)", width=3.5),
        marker=dict(size=7)
    ),
    secondary_y=True,
)

# Zona de Alerta (Super El Niño) - Somente a faixa, sem o texto
figura.add_vrect(
    x0="2026-12-01", 
    x1="2027-03-31", 
    fillcolor="red", 
    opacity=0.20, 
    line_width=1,
    line_dash="dot",
    line_color="darkred"
)

# Ajustes de Layout
figura.update_layout(
    title_text="<b>Correlação Histórica e Projeção do Impacto do Ar Particulado</b>",
    hovermode="x unified",
    plot_bgcolor='rgb(250,250,250)',
    height=500, 
    legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40)
)

# Eixo X (Datas): Sem título, com texto preto e fonte em negrito
figura.update_xaxes(
    title_text="", 
    showgrid=True, 
    gridcolor='lightgray',
    tickfont=dict(color='black', family='Arial Black') # Escurece e engrossa a fonte
)

# Eixo Y Esquerdo (Focos): Título e números pretos em negrito
figura.update_yaxes(
    title_text="<b>Focos de Calor</b>", 
    secondary_y=False, 
    showgrid=False,
    tickfont=dict(color='black', family='Arial Black')
)

# Eixo Y Direito (Atendimentos): Título e números pretos em negrito
figura.update_yaxes(
    title_text="<b>Atendimentos Médicos</b>", 
    secondary_y=True, 
    showgrid=True, 
    gridcolor='lightgray',
    tickfont=dict(color='black', family='Arial Black')
)

st.plotly_chart(figura, use_container_width=True)