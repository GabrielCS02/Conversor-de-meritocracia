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

# --- Interface ---
st.set_page_config(page_title="Motor de Decisão", page_icon="⚙️", layout="wide")

# CSS para customizar a área de upload (Borda Verde Excel)
st.markdown("""
    <style>
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #10B981;
        background-color: #F0FDFA;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ Sistema de Configuração - Meritocracia")

# Criação das Abas
tab1, tab2 = st.tabs(["🚀 Conversor", "📖 Manual de Uso"])

with tab1:
    st.markdown("### 📥 Carregue sua Planilha")
    arquivo = st.file_uploader("", type=['xlsx', 'csv'])

    if arquivo:
        try:
            df = pd.read_csv(arquivo) if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
            json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
            
            st.info(f"📊 **Resumo:** {total_perfis} perfis convertidos para o portfólio **{portfolio_nome}**.")

            if avisos:
                st.markdown("### 🚨 Alertas de Distribuição")
                for aviso in avisos: st.warning(aviso)
            else:
                st.success("✅ Validação concluída: Todos os grupos somam 100%!")

            st.divider()
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Visualização do JSON")
                st.json(json_final)
            with col2:
                st.subheader("Ações")
                json_str = json.dumps(json_final, indent=2, ensure_ascii=False)
                st.download_button("BAIXAR JSON FINAL 📥", json_str, f"conversao_{portfolio_nome}.json", "application/json", use_container_width=True)
        except Exception as e:
            st.error(f"Erro ao processar: {e}")

with tab2:
    st.markdown("""
    ## 📖 Guia de Utilização do Conversor
    
    Este sistema foi criado para transformar as planilhas de distribuição de metas em arquivos JSON compatíveis com o MongoDB.
    
    ### 1. Formato da Planilha
    Para que a conversão funcione, sua planilha **deve** conter estas colunas exatamente com estes nomes:
    * **cGrpCobrMotorDecis**: Nome do Perfil (ex: PJBCODIGAM).
    * **cCanalCobrMotorDecis**: Nome do Canal (ex: CALLCENTER).
    * **DISTRIBUIÇÃO cCanalCobrMotorDecis**: % do Canal dentro do Perfil.
    * **cDecisAssesMotorDecis**: Nome da Assessoria.
    * **DISTRIBUIÇÃO**: % da Assessoria dentro do Canal.
    
    > **Dica:** Você não precisa repetir o nome do Perfil ou Canal em todas as linhas. O sistema preenche automaticamente as células vazias abaixo de um nome.

    ### 2. Regras de Negócio (Validação)
    O sistema verifica automaticamente se os percentuais estão corretos:
    * A soma de todos os **Canais** de um Perfil deve ser **100%**.
    * A soma de todas as **Assessorias** de um Canal deve ser **100%**.
    * Se os valores forem diferentes de 100, um aviso amarelo aparecerá na aba 'Conversor'.
    
    ### 3. Como Exportar
    1. Suba o arquivo na aba **Conversor**.
    2. Verifique se não há mensagens de erro (Warnings).
    3. Clique no botão azul **Baixar JSON Final**.
    4. O arquivo gerado pode ser importado diretamente no MongoDB.
    """)
    st.info("Em caso de erros técnicos, contate o administrador do sistema.")