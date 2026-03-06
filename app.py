import streamlit as st
import pandas as pd
import json
import os

# --- FUNÇÃO DE CARREGAMENTO ---

def load_css(file_name):
    """Carrega o arquivo CSS externo da pasta assets"""
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        print(f"Aviso: O arquivo {file_name} não foi encontrado.")

# --- LÓGICA DE CONVERSÃO ---

def transformar_para_hierarquia(df):
    """
    Converte o DataFrame da planilha para a estrutura JSON aninhada.
    Realiza o preenchimento de células vazias (ffill) e valida somas de 100%.
    """
    # Preenchimento automático para células mescladas/vazias
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    # Agrupamento por Perfil
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        nome_portfolio = "BCO"
        resultado["perfis"][perfil] = {
            "portfolios": {
                nome_portfolio: { "nome": nome_portfolio, "canais": {} }
            }
        }
        
        # Validação: Soma dos canais do Perfil
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"⚠️ **Perfil {perfil}**: A soma dos canais é **{soma_canais}%** (esperado 100%).")

        # Agrupamento por Canal
        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            
            # Validação: Soma das assessorias do Canal
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            if soma_asses != 100:
                erros_soma.append(f"❌ **Canal {canal}** (Perfil {perfil}): A soma das assessorias é **{soma_asses}%**.")

            resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal] = {
                "percentual": percentual_canal,
                "assessorias": {}
            }
            
            # Adição das Assessorias
            for _, linha in grupo_canal.iterrows():
                assessoria = str(linha['cDecisAssesMotorDecis'])
                perc_assessoria = int(linha['DISTRIBUIÇÃO'])
                resultado["perfis"][perfil]["portfolios"][nome_portfolio]["canais"][canal]["assessorias"][assessoria] = {
                    "percentual": perc_assessoria
                }
                
    return resultado, erros_soma, len(resultado["perfis"]), "BCO"

# --- CONFIGURAÇÃO E INTERFACE ---

# Configuração da página para evitar conflitos de tema
st.set_page_config(page_title="Bradesco S.A. | Recuperação de Crédito", page_icon="🏦", layout="wide")

# Carregar estilização externa
load_css("assets/style.css")

# Estrutura de Cabeçalho Corporativo
st.markdown("""
    <div class="nav-bar">
        <h2>Banco Bradesco S.A.</h2>
    </div>
    <div class="main-content-wrapper">
    """, unsafe_allow_html=True)

# Definição das Abas
tab1, tab2 = st.tabs(["🚀 Conversor", "📖 Manual"])

with tab1:
    st.markdown("#### Carregue a Planilha de Distribuição")
    st.caption("Arraste o arquivo .xlsx ou .csv para processamento")
    
    # O componente de upload agora herdará o estilo do CSS
    arquivo = st.file_uploader("", type=['xlsx', 'csv'], label_visibility="collapsed")

    if arquivo:
        try:
            # Leitura do arquivo com suporte a encodings comuns
            if arquivo.name.endswith('.csv'):
                try:
                    df = pd.read_csv(arquivo, encoding='utf-8')
                except:
                    df = pd.read_csv(arquivo, encoding='latin1')
            else:
                df = pd.read_excel(arquivo)

            # Processamento dos dados
            json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
            
            # Resumo do Processamento
            st.info(f"**Processamento Concluído:** {total_perfis} perfis identificados no Portfólio **{portfolio_nome}**.")

            # Exibição de Alertas de Erro ou Sucesso
            if avisos:
                for aviso in avisos:
                    st.warning(aviso)
            else:
                st.success("✅ Validação concluída: Todas as distribuições somam 100%.")

            st.divider()
            
            # Layout de Resultados
            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Prévia da Estrutura JSON")
                st.json(json_final)
            with col2:
                st.subheader("Exportação")
                json_str = json.dumps(json_final, indent=2, ensure_ascii=False)
                st.download_button(
                    label="BAIXAR ARQUIVO JSON 📥",
                    data=json_str,
                    file_name=f"import_motor_{portfolio_nome}.json",
                    mime="application/json",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

with tab2:
    st.markdown('<div class="manual-content">', unsafe_allow_html=True)
    st.markdown(f"""
    ### Guia de Operação Interna
    
    Esta ferramenta automatiza a conversão de planilhas de metas para o formato JSON do MongoDB.
    
    **1. Colunas Obrigatórias:**
    A planilha deve conter exatamente as colunas:
    - `cGrpCobrMotorDecis` (Perfil)
    - `cCanalCobrMotorDecis` (Canal)
    - `DISTRIBUIÇÃO cCanalCobrMotorDecis` (% do Canal)
    - `cDecisAssesMotorDecis` (Assessoria)
    - `DISTRIBUIÇÃO` (% da Assessoria)
    
    **2. Validação de Dados:**
    O sistema bloqueia a validação positiva caso a soma de qualquer grupo seja diferente de **100**.
    
    **3. Suporte:**
    Em caso de dúvidas, contate: **gabrielc.silva@bradesco.com.br**
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Fechamento do wrapper principal
st.markdown("</div>", unsafe_allow_html=True)

# Rodapé institucional fixo
st.markdown("""
    <div class="footer-text">
        © 2026 Banco Bradesco S.A. | Inteligência de Dados | Uso Interno - Recuperação de Crédito
    </div>
    """, unsafe_allow_html=True)