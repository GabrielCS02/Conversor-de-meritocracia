import streamlit as st
import pandas as pd
import json

def transformar_para_hierarquia(df):
    # Preenchimento automático para células vazias (vinda de células mescladas)
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    # 1. Agrupamento por Perfil
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        nome_portfolio = "BCO"
        resultado["perfis"][perfil] = {
            "portfolios": {
                nome_portfolio: {
                    "nome": nome_portfolio,
                    "canais": {}
                }
            }
        }
        
        # VALIDAÇÃO: Soma dos canais dentro do Perfil
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"⚠️ **Perfil {perfil}**: A soma dos canais está em **{soma_canais}%**.")

        # 2. Agrupamento por Canal
        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            
            # VALIDAÇÃO: Soma das assessorias dentro do Canal
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            if soma_asses != 100:
                erros_soma.append(f"❌ **Canal {canal}** (Perfil {perfil}): A soma das assessorias está em **{soma_asses}%**.")

            resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal] = {
                "percentual": percentual_canal,
                "assessorias": {}
            }
            
            # 3. Adicionando Assessorias
            for _, linha in grupo_canal.iterrows():
                assessoria = str(linha['cDecisAssesMotorDecis'])
                perc_assessoria = int(linha['DISTRIBUIÇÃO'])
                resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal]["assessorias"][assessoria] = {
                    "percentual": perc_assessoria
                }
                
    return resultado, erros_soma, len(resultado["perfis"]), "BCO"

# --- Interface Visual Customizada ---
st.set_page_config(page_title="Conversor de Meritocracia", page_icon="⚙️")

# CSS para customizar a aparência geral e destacar a área de upload
st.markdown("""
    <style>
    /* Estilo para o título principal */
    .css-10trblm { color: #1E3A8A; } /* Azul corporativo */
    
    /* Envelopa o componente de upload para destacar */
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #10B981; /* Verde Excel */
        background-color: #F0FDFA; /* Fundo esverdeado claro */
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Estilo para o botão de download */
    .stDownloadButton>button {
        background-color: #2563EB; /* Azul vibrante */
        color: white;
        border-radius: 8px;
        width: 100%;
        height: 3em;
        font-weight: bold;
    }
    .stDownloadButton>button:hover {
        background-color: #1D4ED8;
        border-color: #1D4ED8;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("⚙️ Conversor de Perfis")

# Mensagem clara em português ANTES do componente de upload
st.markdown("### 📥 Passo 1: Carregue sua Planilha")
st.write("Arraste o arquivo Excel/CSV para a área pontilhada abaixo ou clique em 'Browse files'.")

arquivo = st.file_uploader("", type=['xlsx', 'csv']) # Label vazio

if arquivo:
    try:
        # Carregar dados
        if arquivo.name.endswith('.csv'):
            # Tenta ler CSV tratando possíveis problemas de encoding
            try:
                df = pd.read_csv(arquivo, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(arquivo, encoding='latin1')
        else:
            df = pd.read_excel(arquivo)
            
        # Processar lógica
        json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
        
        # --- Resumo e Validações ---
        st.divider()
        st.info(f"📊 **Resumo da Conversão:**\n\nForam convertidos **{total_perfis}** perfis para o portfólio **{portfolio_nome}**.")

        if avisos:
            st.markdown("### 🚨 Verificação de Percentuais")
            for aviso in avisos:
                st.warning(aviso)
        else:
            st.success("✅ Tudo pronto! Os cálculos estão corretos.")

        # --- Ações e Prévia ---
        st.divider()
        col1, col2 = st.columns([2, 1])
        with col1:
            st.subheader("Prévia do JSON")
            st.json(json_final)
        with col2:
            st.subheader("Passo 2: Obter Arquivo")
            json_str = json.dumps(json_final, indent=2, ensure_ascii=False)
            st.download_button(
                label="BAIXAR JSON FINAL 📥",
                data=json_str,
                file_name=f"conversao_{portfolio_nome}.json",
                mime="application/json",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Erro crítico ao processar o arquivo: {e}. Certifique-se de que a planilha segue o padrão original.")