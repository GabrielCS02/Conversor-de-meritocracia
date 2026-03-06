import streamlit as st
import pandas as pd
import json
import os

# --- FUNÇÃO DE CARREGAMENTO ---
def load_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- LÓGICA DE CONVERSÃO ---
def transformar_para_hierarquia(df):
    # Preenchimento de células mescladas
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
        
        # Validação de Canais
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"⚠️ **Perfil {perfil}**: Soma dos canais {soma_canais}% (esperado 100%).")

        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            
            # Validação de Assessorias
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
                
    return resultado, erros_soma, len(resultado["perfis"])

# --- INTERFACE ---
st.set_page_config(page_title="Bradesco S.A. | Conversor", page_icon="🏦", layout="wide")
load_css("assets/style.css")

# Elementos de topo (fora do wrapper para fixação correta)
st.markdown('<div class="nav-bar"><h2>Banco Bradesco S.A.</h2></div>', unsafe_allow_html=True)

# Abertura do Card Principal
st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🚀 Conversor", "📖 Manual"])

with tab1:
    st.markdown("### Conversão de Planilha")
    arquivo = st.file_uploader("Upload", type=['xlsx', 'csv'], label_visibility="collapsed")

    if arquivo:
        try:
            df = pd.read_csv(arquivo, encoding='latin1') if arquivo.name.endswith('.csv') else pd.read_excel(arquivo)
            json_final, avisos, total_perfis = transformar_para_hierarquia(df)
            
            if avisos:
                for aviso in avisos: st.warning(aviso)
            else:
                st.success(f"✅ Sucesso: {total_perfis} perfis processados.")

            st.divider()
            col_json, col_down = st.columns([3, 1])
            with col_json:
                st.json(json_final)
            with col_down:
                json_str = json.dumps(json_final, indent=2, ensure_ascii=False)
                st.download_button("BAIXAR JSON 📥", data=json_str, file_name="motor_distribuicao.json", use_container_width=True)
        except Exception as e:
            st.error(f"Erro no processamento: {e}")

with tab2:
    st.markdown(f"""
    <div class="manual-content">
        <h3 style="margin-top:0">Guia de Utilização</h3>
        <p>Utilize este conversor para gerar o ficheiro JSON de configuração do motor de decisão.</p>
        
        <h4 style="margin-top:20px">Estrutura Obrigatória:</h4>
        <ul style="list-style-type: none; padding-left: 0;">
            <li><span class="manual-tag">cGrpCobrMotorDecis</span> - Grupo de Perfil</li>
            <li><span class="manual-tag">cCanalCobrMotorDecis</span> - Canal de Cobrança</li>
            <li><span class="manual-tag">DISTRIBUIÇÃO cCanalCobrMotorDecis</span> - % do Canal</li>
            <li><span class="manual-tag">cDecisAssesMotorDecis</span> - ID da Assessoria</li>
            <li><span class="manual-tag">DISTRIBUIÇÃO</span> - % da Assessoria</li>
        </ul>

        <h4 style="margin-top:20px">Validações:</h4>
        <p>O sistema verifica se as somas dos canais por perfil e assessorias por canal totalizam <b>100%</b>.</p>
        
        <p style="margin-top:20px; font-size: 0.9em; color: #666;">
            Suporte Técnico: <b>gabrielc.silva@bradesco.com.br</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Fecho do Card e Rodapé
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="footer-text">© 2026 Banco Bradesco S.A. | Recuperação de Crédito</div>', unsafe_allow_html=True)