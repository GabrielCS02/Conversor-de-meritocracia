import pandas as pd
from collections import OrderedDict

def transformar_para_hierarquia(df):
    """Lógica com OrderedDict e alertas detalhados com Perfil em todas as mensagens"""
    # Preenchimento de células mescladas
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        id_portfolio = "BCO"
        
        # Estrutura do Portfolio
        dados_portfolio = OrderedDict()
        dados_portfolio["nome"] = id_portfolio
        dados_portfolio["canais"] = OrderedDict()
        
        resultado["perfis"][perfil] = {
            "portfolios": { id_portfolio: dados_portfolio }
        }
        
        # 1. Validação de Canais do Perfil Atual
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            # Incluindo o perfil explicitamente
            erros_soma.append(f"PERFIL: {perfil} | SOMA CANAIS: {soma_canais}%")

        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            
            # 2. Validação de Assessorias do Perfil/Canal Atual
            if soma_asses != 100:
                # Agora mostramos o PERFIL e o CANAL em cada erro subsequente
                erros_soma.append(f"PERFIL: {perfil} | CANAL: {canal} | SOMA ASSESSORIAS: {soma_asses}%")

            # Estrutura do Canal
            dados_canal = OrderedDict()
            dados_canal["percentual"] = percentual_canal
            dados_canal["assessorias"] = OrderedDict()
            
            dados_portfolio["canais"][canal] = dados_canal
            
            for _, linha in grupo_canal.iterrows():
                assessoria = str(linha['cDecisAssesMotorDecis'])
                perc_assessoria = int(linha['DISTRIBUIÇÃO'])
                dados_canal["assessorias"][assessoria] = {"percentual": perc_assessoria}
                
    return resultado, erros_soma