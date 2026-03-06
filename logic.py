import pandas as pd
from collections import OrderedDict

def transformar_para_hierarquia(df):
    """Lógica com OrderedDict em todos os níveis para forçar a ordem do JSON EXEMPLO"""
    # Preenchimento de células mescladas
    df['cGrpCobrMotorDecis'] = df['cGrpCobrMotorDecis'].ffill()
    df['cCanalCobrMotorDecis'] = df['cCanalCobrMotorDecis'].ffill()
    df['DISTRIBUIÇÃO cCanalCobrMotorDecis'] = df['DISTRIBUIÇÃO cCanalCobrMotorDecis'].ffill()

    resultado = {"perfis": {}}
    erros_soma = []
    
    for perfil, grupo_perfil in df.groupby('cGrpCobrMotorDecis'):
        id_portfolio = "BCO"
        
        # 1. ORDEM DO PORTFOLIO: 'nome' deve ser a PRIMEIRA chave
        dados_portfolio = OrderedDict()
        dados_portfolio["nome"] = id_portfolio
        dados_portfolio["canais"] = OrderedDict()
        
        resultado["perfis"][perfil] = {
            "portfolios": { id_portfolio: dados_portfolio }
        }
        
        # Validação de Canais
        df_canais_unicos = grupo_perfil.drop_duplicates('cCanalCobrMotorDecis')
        soma_canais = df_canais_unicos['DISTRIBUIÇÃO cCanalCobrMotorDecis'].sum()
        if soma_canais != 100:
            erros_soma.append(f"PERFIL: {perfil} | SOMA CANAIS: {soma_canais}%")

        for canal, grupo_canal in grupo_perfil.groupby('cCanalCobrMotorDecis'):
            percentual_canal = int(grupo_canal['DISTRIBUIÇÃO cCanalCobrMotorDecis'].iloc[0])
            soma_asses = grupo_canal['DISTRIBUIÇÃO'].sum()
            
            if soma_asses != 100:
                erros_soma.append(f"CANAL: {canal} | SOMA ASSESSORIAS: {soma_asses}%")

            # 2. ORDEM DO CANAL: 'percentual' deve vir ANTES de 'assessorias'
            dados_canal = OrderedDict()
            dados_canal["percentual"] = percentual_canal
            dados_canal["assessorias"] = OrderedDict()
            
            dados_portfolio["canais"][canal] = dados_canal
            
            for _, linha in grupo_canal.iterrows():
                assessoria = str(linha['cDecisAssesMotorDecis'])
                perc_assessoria = int(linha['DISTRIBUIÇÃO'])
                
                # Assessorias também como OrderedDict para garantir consistência
                dados_canal["assessorias"][assessoria] = {"percentual": perc_assessoria}
                
    return resultado, erros_soma