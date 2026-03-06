import streamlit as st
import pandas as pd
import json

def transformar_para_hierarquia(df):
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        nome_portfolio = "BCO"
        resultado["perfis"][perfil] = {
            "portfolios": {
                nome_portfolio: { "nome": nome_portfolio, "canais": {} }
            }
        }
        
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"⚠️ **Perfil {perfil}**: Soma dos canais é **{soma_canais}%**.")

        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            if soma_asses != 100:
                erros_soma.append(f"❌ **Canal {canal}** ({perfil}): Soma das assessorias é **{soma_asses}%**.")

            resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal] = {
                "percentual": percentual_canal,
                "assessorias": {}
            }
            
            for _, linha in grupo_canal.iterrows():
                assessoria = str(linha['cDecisAssesMotorDecis'])
                perc_assessoria = int(linha['DISTRIBUIÇÃO'])
                resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal]["assessorias"][assessoria] = {
                    "percentual": perc_assessoria
                }
                
    return resultado, erros_soma, len(resultado["perfis"]), "BCO"

# --- Interface Estilizada Bradesco ---
st.set_page_config(page_title="Bradesco | Meritocracia", page_icon="🏦", layout="wide")

# CSS para Identidade Visual Bradesco
st.markdown("""
    <style>
    /* Cor de fundo e fontes */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Header estilizado */
    .main-header {
        background-color: #cc092f;
        padding: 20px;
        border-radius: 0px 0px 10px 10px;
        color: white;
        text-align: center;
        margin-bottom: 25px;
        font-family: sans-serif;
    }

    /* Customização das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #cc092f !important;
        color: white !important;
    }

    /* Área de Upload */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #cc092f;
        background-color: #fff5f6;
        border-radius: 10px;
    }

    /* Botão de Download */
    div.stDownloadButton > button {
        background-color: #cc092f;
        color: white;
        border-radius: 5px;
        border: none;
        height: 50px;
        width: 100%;
        font-weight: bold;
    }
    div.stDownloadButton > button:hover {
        background-color: #a30725;
        color: white;
    }

    /* Rodapé */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f8f9fa;
        color: #6c757d;
        text-align: center;
        padding: 10px;
        font-size: 12px;
        border-top: 1px solid #dee2e6;
    }
    </style>
    
    <div class="main-header">
        <h1>Banco Bradesco S.A.</h1>
        <p>Departamento de Meritocracia | Conversor de Configurações Motor de Decisão</p>
    </div>
    """, unsafe_allow_html=True)

# Criação das Abas
tab1, tab2 = st.tabs(["🚀 Conversor de Arquivos", "📖 Manual de Instruções"])

with tab1:
    st.markdown("### 📥 Upload de Planilha")
    st.caption("Arraste o arquivo .xlsx ou .csv para processamento")
    arquivo = st.file_uploader("", type=['xlsx', 'csv'])

    if arquivo:
        try:
            df = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
            json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
            
            st.info(f"📊 **Processamento Concluído:** {total_perfis} perfis identificados no portfólio **{portfolio_nome}**.")

            if avisos:
                st.markdown("#### 🚨 Alertas de Validação")
                for aviso in avisos: st.warning(aviso)
            else:
                st.success("✅ Todos os grupos de distribuição somam 100%.")

            st.divider()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Visualização da Estrutura")
                st.json(json_final)
            with col2:
                st.subheader("Exportar Dados")
                json_str = json.dumps(json_final, indent=2, ensure_ascii=False)
                st.download_button("GERAR ARQUIVO JSON 📥", json_str, f"config_motor_{portfolio_nome}.json", "application/json", use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar arquivo: {e}")

with tab2:
    st.markdown(f"""
    ## Guia de Operação Interna
    
    Este sistema é uma ferramenta de suporte para a equipe de **Meritocracia do Bradesco**, visando automatizar a geração de documentos JSON para o banco de dados.
    
    ### 1. Requisitos da Planilha
    A planilha de entrada deve conter obrigatoriamente as colunas:
    * `cGrpCobrMotorDecis`
    * `cCanalCobrMotorDecis`
    * `DISTRIBUIÇÃO cCanalCobrMotorDecis`
    * `cDecisAssesMotorDecis`
    * `DISTRIBUIÇÃO`
    
    ### 2. Validações Automáticas
    * O sistema verifica se a soma das distribuições por canal atinge **100%**.
    * O sistema verifica se a soma das distribuições por assessoria atinge **100%**.
    
    ### 3. Suporte Técnico
    Para dúvidas sobre o funcionamento ou erros de conversão, entre em contato:
    * **Responsável:** Gabriel Silva
    * **Email:** gabrielc.silva@bradesco.com.br
    """)

# Rodapé Fixo
st.markdown("""
    <div class="footer">
        © 2024 Banco Bradesco S.A. Todos os direitos reservados. Uso restrito e interno.
    </div>
    """, unsafe_allow_html=True)