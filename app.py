import streamlit as st
import pandas as pd
import json
import os

# --- FUNÇÕES DE LÓGICA ---

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
        # Alerta silencioso no console caso você esqueça de subir a pasta assets
        print(f"Aviso: O arquivo {file_name} não foi encontrado.")

st.set_page_config(page_title="Bradesco | Recuperação de Crédito", page_icon="🏦", layout="wide")
load_css("assets/style.css")
st.set_page_config(page_title="Bradesco | Recuperação de Crédito", page_icon="🏦", layout="wide")
# Carregar estilização externa
load_css("assets/style.css")
# Header customizado (HTML para estrutura de classes do CSS)
st.markdown("""
    <div class="nav-bar">
        <div><h2>Bradesco | Inteligência de Dados</h2></div>
        <div><p>Recuperação de Crédito</p></div>
    </div>
    """, unsafe_allow_html=True)
# Definição das Abas
tab1, tab2 = st.tabs(["🚀 Conversor", "📖 Manual"])
with tab1:
    st.markdown("#### Carregue a Planilha de Distribuição")
    arquivo = st.file_uploader("", type=['xlsx', 'csv'])

    if arquivo:
        try:
            # Leitura do arquivo (suporte a Excel e CSV com diferentes encodings)
            if arquivo.name.endswith('.csv'):
                try:
                    df = pd.read_csv(arquivo, encoding='utf-8')
                except:
                    df = pd.read_csv(arquivo, encoding='latin1')
            else:
                df = pd.read_excel(arquivo)

            # Processamento
            json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
            
            # Resumo do Processamento
            st.info(f"**Processamento:** {total_perfis} perfis identificados no Portfólio **{portfolio_nome}**.")

            # Exibição de Alertas de Erro
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

# Rodapé institucional
st.markdown("""
    <div class="footer-text">
        © 2026 Banco Bradesco S.A. | Uso Interno - Recuperação de Crédito
    </div>
    """, unsafe_allow_html=True)