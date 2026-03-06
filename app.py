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
        st.error(f"Erro: O arquivo {file_name} não foi encontrado.")

# --- LÓGICA DE CONVERSÃO ---

def transformar_para_hierarquia(df):
    """Converte o DataFrame para estrutura JSON e valida somas de 100%."""
    # Preenchimento de células vazias (ffill)
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        nome_portfolio = "BCO"
        resultado["perfis"][perfil] = {
            "portfolios": { nome_portfolio: { "nome": nome_portfolio, "canais": {} } }
        }
        
        # Validação Canais
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"⚠️ **Perfil {perfil}**: Soma dos canais {soma_canais}% (esperado 100%).")

        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            
            # Validação Assessorias
            if soma_asses != 100:
                erros_soma.append(f"❌ **Canal {canal}** (Perfil {perfil}): Soma das assessorias {soma_asses}%.")

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

# --- CONFIGURAÇÃO DA PÁGINA ---

st.set_page_config(page_title="Bradesco S.A. | Recuperação de Crédito", page_icon="🏦", layout="wide")
load_css("assets/style.css")

# Abertura do Layout Customizado
st.markdown("""
    <div class="nav-bar">
        <h2>Banco Bradesco S.A.</h2>
    </div>
    <div class="main-content-wrapper">
    """, unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 Conversor", "📖 Manual"])

with tab1:
    st.markdown("#### Carregue a Planilha de Distribuição")
    st.caption("Arraste o arquivo .xlsx ou .csv para processamento")
    
    arquivo = st.file_uploader("", type=['xlsx', 'csv'], label_visibility="collapsed")

    if arquivo:
        try:
            if arquivo.name.endswith('.csv'):
                try:
                    df = pd.read_csv(arquivo, encoding='utf-8')
                except:
                    df = pd.read_csv(arquivo, encoding='latin1')
            else:
                df = pd.read_excel(arquivo)

            json_final, avisos, total_perfis, portfolio_nome = transformar_para_hierarquia(df)
            
            st.info(f"**Processamento Concluído:** {total_perfis} perfis identificados.")

            if avisos:
                for aviso in avisos:
                    st.warning(aviso)
            else:
                st.success("✅ Validação concluída: Todas as distribuições somam 100%.")

            st.divider()
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
    ### 📖 Guia de Operação Interna
    
    <div class="manual-section">
        <strong>1. Colunas Obrigatórias:</strong><br>
        A planilha deve conter exatamente estas nomenclaturas:
        <ul>
            <li><span class="manual-tag">cGrpCobrMotorDecis</span> (Perfil)</li>
            <li><span class="manual-tag">cCanalCobrMotorDecis</span> (Canal)</li>
            <li><span class="manual-tag">DISTRIBUIÇÃO cCanalCobrMotorDecis</span> (% do Canal)</li>
            <li><span class="manual-tag">cDecisAssesMotorDecis</span> (Assessoria)</li>
            <li><span class="manual-tag">DISTRIBUIÇÃO</span> (% da Assessoria)</li>
        </ul>
    </div>

    <div class="manual-section">
        <strong>2. Regras de Negócio:</strong>
        <ul>
            <li>O sistema realiza o preenchimento automático de células mescladas (ffill).</li>
            <li>A soma de todos os canais de um Perfil deve totalizar <b>100%</b>.</li>
            <li>A soma de todas as assessorias de um Canal deve totalizar <b>100%</b>.</li>
        </ul>
    </div>

    <div class="manual-section">
        <strong>3. Suporte:</strong><br>
        Contato para ajustes no motor: <a href="mailto:gabrielc.silva@bradesco.com.br" style="color: #cc092f; font-weight: bold;">gabrielc.silva@bradesco.com.br</a>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Fechamento do Wrapper e Rodapé Fixo
st.markdown("""
    </div>
    <div class="footer-text">
        © 2026 Banco Bradesco S.A. | Inteligência de Dados | Uso Interno - Recuperação de Crédito
    </div>
    """, unsafe_allow_html=True)