import pandas as pd
import streamlit as st

# Configuração da Página
st.set_page_config(page_title="Ficha Metodológica: Bahia", layout="centered")

# Título com tamanho reduzido (Usando Markdown H3)
st.markdown("### Sazonalidade dos Focos de Calor e Urgências Oftalmológicas (2022-2026)")

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
    
    # 4. Excluir 2021
    df_final = df_final[df_final['Data_Processamento'] >= '2022-01-01']
    
    # Como removemos o gráfico, não precisamos mais criar os meses de 2027 vazios!
    return df_final

dados = carregar_dados_integrados()

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
    * **Local:** Estado da Bahia
    * **Grupo:** 03 - Procedimentos Clínicos
    * **Profissional (CBO):** 223144 e 225265 (Oftalmologista)
    * **Conteúdo:** Quantidade Aprovada
    """)

with col2:
    st.warning("""
    **Dados Ambientais (BDQueimadas / INPE)**
    * **Local:** Estado da Bahia (Todos os biomas)
    * **Satélite:** AQUA_M-T (Aqua Tarde)
    * **Dado Extraído:** Soma mensal de focos.
    """)

# A Tabela agora fica aberta por padrão
st.subheader("📊 Tabela de Dados Integrados (INPE x SUS)")

# Prepara a tabela para exibição
tabela_bonita = dados.copy()

# Nomes das colunas ajustados
tabela_bonita.columns = ['Mês/Ano', 'Focos de Calor', 'Atendimentos Oftalmológicos (SUS)']
tabela_bonita['Mês/Ano'] = tabela_bonita['Mês/Ano'].dt.strftime('%m/%Y')

# Troca valores vazios (meses de atraso do SUS) por um traço
tabela_bonita = tabela_bonita.fillna('-')

# Tabela configurada para não gerar rolagem horizontal no celular
st.dataframe(
    tabela_bonita, 
    use_container_width=True, 
    hide_index=True,
    column_config={
        "Mês/Ano": st.column_config.Column(width="small"),
        "Focos de Calor": st.column_config.Column(width="small"),
        "Atendimentos Oftalmológicos (SUS)": st.column_config.Column(width="medium")
    }
)