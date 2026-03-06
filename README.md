# 🚀 Conversor de Meritocracia

Este projeto foi desenvolvido pelo **ID** para auxiliar o **DRC** na automação e padronização da conversão de dados de meritocracia para o formato JSON esperado pelo DMPS.

## 📋 Sobre o Projeto
O objetivo principal é transformar a meritocracia (Excel/CSV) em uma estrutura JSON para o contextual profile, garantindo os percentuais e somas de distribuição de canais e assessorias.

## 🛠️ Tecnologias Utilizadas
* **Python 3.12+**
* **Flask** (Interface Web)
* **Pandas** (Processamento de Dados)

## 🚀 Como Usar

### 1. Preparação da Planilha
Certifique-se de que sua planilha possui as colunas obrigatórias:
* `cGrpCobrMotorDecis` (Perfil)
* `cCanalCobrMotorDecis` (Canal)
* `DISTRIBUIÇÃO cCanalCobrMotorDecis` (Percentual do Canal)
* `cDecisAssesMotorDecis` (Assessoria)
* `DISTRIBUIÇÃO` (Percentual da Assessoria)

### 2. Execução do Conversor
1. Execute o servidor Flask:
   ```bash
   python app.py