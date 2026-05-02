# README Técnico — Pipeline Databricks: Conversor de Meritocracia

## 1. Por que este README é necessário?

Este README técnico existe para documentar o funcionamento do pipeline `pipeline_conversor_meritocracia` no Databricks.

A necessidade dele nasce de um ponto importante: um notebook que funciona não é, por si só, suficiente para ser entendido, mantido, executado por outra pessoa ou transformado em rotina de produção. Sem documentação, quem abrir o projeto no futuro precisará descobrir sozinho:

- qual arquivo deve ser usado como entrada;
- quais parâmetros precisam ser preenchidos;
- onde o JSON será salvo;
- quais tabelas são criadas;
- como validar se a execução funcionou;
- o que fazer quando ocorrer erro;
- como configurar o Job no Databricks.

Este README resolve esse problema. Ele transforma o notebook em um componente técnico documentado, rastreável e reutilizável.

Em um contexto profissional, a documentação é parte do pipeline. Ela reduz erros operacionais, facilita manutenção, melhora a transferência de conhecimento e torna o projeto mais confiável.

---

## 2. Objetivo do pipeline

O pipeline `pipeline_conversor_meritocracia` tem como objetivo automatizar a conversão de uma planilha Excel ou CSV de meritocracia em um arquivo JSON estruturado.

O fluxo principal é:

```text
Planilha Excel/CSV
        ↓
Leitura com Pandas
        ↓
Validação de colunas e percentuais
        ↓
Conversão para estrutura hierárquica JSON
        ↓
Salvamento do JSON em Volume
        ↓
Registro de log em tabela Delta
        ↓
Registro do histórico do resultado
```

---

## 3. Tecnologias utilizadas

O pipeline utiliza:

- Databricks Notebook
- Databricks Jobs
- Databricks Volumes
- Python
- Pandas
- Spark
- Delta Tables
- JSON
- openpyxl

---

## 4. Estrutura recomendada no GitHub

Estrutura sugerida para o repositório:

```text
Conversor-de-meritocracia/
│
├── app.py
├── logic.py
├── requirements.txt
├── README.md
│
├── notebooks/
│   └── pipeline_conversor_meritocracia_v3.ipynb
│
├── samples/
│   └── PLANILHA EXEMPLO.xlsx
│
└── docs/
    └── README_PIPELINE_DATABRICKS.md
```

Observação importante: não envie dados reais ou sensíveis para repositórios públicos. Use apenas arquivos de exemplo anonimizados.

---

## 5. Arquivo de entrada

O pipeline aceita arquivos nos formatos:

```text
.csv
.xlsx
.xls
```

A planilha deve conter obrigatoriamente as seguintes colunas:

```text
cGrpCobrMotorDecis
cCanalCobrMotorDecis
DISTRIBUIÇÃO cCanalCobrMotorDecis
cDecisAssesMotorDecis
DISTRIBUIÇÃO
```

Essas colunas são usadas para montar a hierarquia final do JSON.

---

## 6. Estrutura esperada do Volume

A versão atual do pipeline utiliza Databricks Volumes para armazenar arquivos de entrada, saída e erro.

Estrutura recomendada:

```text
/Volumes/workspace/default/planilha-exemplo/
│
├── PLANILHA EXEMPLO.xlsx
│
├── saida/
│   └── saida_meritocracia_YYYYMMDD_HHMMSS.json
│
└── erros/
    └── erro_conversor_YYYYMMDD_HHMMSS.txt
```

Exemplo de caminhos:

```text
Arquivo de entrada:
/Volumes/workspace/default/planilha-exemplo/PLANILHA EXEMPLO.xlsx

Diretório de saída:
/Volumes/workspace/default/planilha-exemplo/saida

Diretório de erro:
/Volumes/workspace/default/planilha-exemplo/erros
```

---

## 7. Parâmetros do notebook

O notebook utiliza `dbutils.widgets` para permitir execução parametrizada, tanto manualmente quanto por Job.

| Parâmetro | Descrição | Exemplo |
|---|---|---|
| `arquivo_entrada` | Caminho completo da planilha de entrada | `/Volumes/workspace/default/planilha-exemplo/PLANILHA EXEMPLO.xlsx` |
| `diretorio_saida` | Diretório onde o JSON será salvo | `/Volumes/workspace/default/planilha-exemplo/saida` |
| `diretorio_erro` | Diretório onde arquivos de erro serão salvos | `/Volumes/workspace/default/planilha-exemplo/erros` |
| `nome_saida` | Nome base do arquivo JSON | `saida_meritocracia.json` |
| `falhar_com_avisos` | Define se o pipeline deve falhar quando houver avisos | `false` |
| `tabela_log` | Nome da tabela Delta de log | `log_conversor_meritocracia` |
| `tabela_resultados` | Nome da tabela Delta de histórico dos resultados | `historico_conversor_meritocracia` |

---

## 8. Nome do arquivo JSON gerado

O pipeline adiciona data e hora ao nome do JSON para evitar sobrescrever arquivos anteriores.

Exemplo:

```text
Nome base:
saida_meritocracia.json

Nome gerado:
saida_meritocracia_20260502_143022.json
```

Esse padrão permite versionamento simples dos arquivos gerados.

---

## 9. Estrutura do JSON gerado

O JSON final segue uma estrutura hierárquica:

```json
{
  "perfis": {
    "NOME_DO_PERFIL": {
      "portfolios": {
        "BCO": {
          "nome": "BCO",
          "canais": {
            "NOME_DO_CANAL": {
              "percentual": 100,
              "assessorias": {
                "NOME_DA_ASSESSORIA": {
                  "percentual": 50
                }
              }
            }
          }
        }
      }
    }
  }
}
```

A hierarquia principal é:

```text
perfil
  └── portfolio
        └── canal
              └── assessoria
```

---

## 10. Validações realizadas

A versão V3 do pipeline realiza validações antes da conversão.

### 10.1 Validação de existência do arquivo

O pipeline verifica se o arquivo informado em `arquivo_entrada` existe.

Se o arquivo não existir, a execução falha com erro.

### 10.2 Validação de colunas obrigatórias

O pipeline verifica se todas as colunas obrigatórias estão presentes na planilha.

Se alguma coluna estiver ausente, a execução falha.

### 10.3 Validação de valores nulos

Após o preenchimento de células mescladas com `ffill`, o pipeline verifica se ainda existem valores nulos nas colunas obrigatórias.

Se existirem valores nulos, a execução falha.

### 10.4 Validação de percentuais numéricos

As colunas de distribuição precisam conter valores numéricos.

Se houver texto ou valores inválidos, a execução falha.

### 10.5 Validação de intervalo percentual

Os percentuais devem estar entre 0 e 100.

Se houver valores abaixo de 0 ou acima de 100, a execução falha.

### 10.6 Validação de soma de percentuais

O pipeline verifica:

- se a soma dos canais por perfil é igual a 100%;
- se a soma das assessorias por canal é igual a 100%.

Esses casos geram avisos. Dependendo do parâmetro `falhar_com_avisos`, o pipeline pode apenas registrar o aviso ou falhar a execução.

---

## 11. Status possíveis da execução

O pipeline pode registrar três status principais:

| Status | Significado |
|---|---|
| `SUCESSO` | O pipeline executou sem erros e sem avisos |
| `SUCESSO_COM_AVISO` | O pipeline executou, gerou o JSON, mas encontrou avisos de soma percentual |
| `ERRO` | O pipeline falhou e registrou o erro |

---

## 12. Tabela de log

A tabela de log registra cada execução do pipeline.

Nome padrão:

```text
log_conversor_meritocracia
```

Schema da tabela:

| Coluna | Tipo | Descrição |
|---|---|---|
| `run_id` | string | Identificador único da execução |
| `arquivo_entrada` | string | Caminho do arquivo processado |
| `arquivo_saida` | string | Caminho do JSON gerado |
| `arquivo_erro` | string | Caminho do arquivo de erro, se existir |
| `linhas_processadas` | long | Quantidade de linhas processadas |
| `quantidade_avisos` | int | Quantidade de avisos identificados |
| `status` | string | Status da execução |
| `mensagem_erro` | string | Mensagem de erro, quando houver |
| `data_execucao` | timestamp | Data e hora da execução |

Consulta recomendada:

```sql
SELECT *
FROM log_conversor_meritocracia
ORDER BY data_execucao DESC;
```

---

## 13. Tabela de histórico dos resultados

A tabela de histórico armazena metadados dos JSONs gerados e o conteúdo JSON produzido.

Nome padrão:

```text
historico_conversor_meritocracia
```

Schema da tabela:

| Coluna | Tipo | Descrição |
|---|---|---|
| `run_id` | string | Identificador único da execução |
| `arquivo_entrada` | string | Caminho da planilha de entrada |
| `arquivo_saida` | string | Caminho do JSON gerado |
| `nome_arquivo_saida` | string | Nome do arquivo JSON |
| `linhas_processadas` | long | Quantidade de linhas processadas |
| `perfis_processados` | int | Quantidade de perfis no JSON |
| `quantidade_avisos` | int | Quantidade de avisos identificados |
| `json_conteudo` | string | Conteúdo completo do JSON |
| `data_execucao` | timestamp | Data e hora da execução |

Consulta recomendada:

```sql
SELECT
    run_id,
    arquivo_entrada,
    arquivo_saida,
    nome_arquivo_saida,
    linhas_processadas,
    perfis_processados,
    quantidade_avisos,
    data_execucao
FROM historico_conversor_meritocracia
ORDER BY data_execucao DESC;
```

---

## 14. Tratamento de erros

O pipeline utiliza bloco `try/except` para capturar erros durante a execução.

Quando ocorre erro:

1. a mensagem de erro é capturada;
2. o stacktrace é salvo em arquivo `.txt`;
3. o erro é registrado na tabela de log;
4. a execução é interrompida para que o Job marque falha.

Os arquivos de erro são salvos em:

```text
/Volumes/workspace/default/planilha-exemplo/erros
```

Exemplo de nome:

```text
erro_conversor_20260502_143022.txt
```

---

## 15. Execução manual

Para executar manualmente:

1. Abra o notebook `pipeline_conversor_meritocracia_v3.ipynb`.
2. Preencha os widgets/parâmetros no topo do notebook.
3. Execute as células em ordem.
4. Valide a saída no Volume.
5. Consulte as tabelas de log e histórico.

---

## 16. Execução via Databricks Job

Para executar como Job:

1. Acesse `Jobs & Pipelines` ou `Workflows`.
2. Crie um novo Job.
3. Adicione uma task do tipo `Notebook`.
4. Selecione o notebook `pipeline_conversor_meritocracia_v3`.
5. Configure os parâmetros da task.
6. Execute com `Run now`.

Parâmetros sugeridos:

```text
arquivo_entrada:
/Volumes/workspace/default/planilha-exemplo/PLANILHA EXEMPLO.xlsx

diretorio_saida:
/Volumes/workspace/default/planilha-exemplo/saida

diretorio_erro:
/Volumes/workspace/default/planilha-exemplo/erros

nome_saida:
saida_meritocracia.json

falhar_com_avisos:
false

tabela_log:
log_conversor_meritocracia

tabela_resultados:
historico_conversor_meritocracia
```

Importante: no valor do parâmetro, informe apenas o valor. Não escreva `nome_do_parametro = valor`.

Exemplo correto:

```text
/Volumes/workspace/default/planilha-exemplo/PLANILHA EXEMPLO.xlsx
```

Exemplo incorreto:

```text
arquivo_entrada = /Volumes/workspace/default/planilha-exemplo/PLANILHA EXEMPLO.xlsx
```

---

## 17. Validação após execução

Após o Job finalizar com `Succeeded`, valide:

### 17.1 Log da última execução

```sql
SELECT *
FROM log_conversor_meritocracia
ORDER BY data_execucao DESC
LIMIT 1;
```

### 17.2 Histórico do resultado

```sql
SELECT
    run_id,
    arquivo_saida,
    linhas_processadas,
    perfis_processados,
    quantidade_avisos,
    data_execucao
FROM historico_conversor_meritocracia
ORDER BY data_execucao DESC
LIMIT 1;
```

### 17.3 Validação física do arquivo

```python
import os

ultimo_log = spark.sql("""
    SELECT *
    FROM log_conversor_meritocracia
    ORDER BY data_execucao DESC
    LIMIT 1
""").collect()[0]

arquivo_saida = ultimo_log["arquivo_saida"]

print("Status:", ultimo_log["status"])
print("Arquivo de saída:", arquivo_saida)
print("Arquivo existe?", os.path.exists(arquivo_saida))
```

### 17.4 Validação do JSON

```python
import json

with open(arquivo_saida, "r", encoding="utf-8") as f:
    dados_json = json.load(f)

print("JSON válido!")
print("Quantidade de perfis:", len(dados_json["perfis"]))
print("Perfis:", list(dados_json["perfis"].keys()))
```

---

## 18. Boas práticas

- Não versionar arquivos reais de produção no GitHub.
- Não versionar JSONs gerados automaticamente.
- Não versionar arquivos de erro com dados sensíveis.
- Usar `samples/` apenas para dados fictícios.
- Usar `docs/` para documentação técnica.
- Usar `notebooks/` para notebooks Databricks.
- Usar nomes versionados para notebooks, como `pipeline_conversor_meritocracia_v3.ipynb`.
- Manter logs e históricos em tabelas Delta.
- Validar o Job após qualquer alteração no notebook.
- Usar `run_id` para rastrear cada execução.

---

## 19. Arquivos que não devem ser enviados ao GitHub

Evite enviar:

```text
saida_meritocracia_*.json
erro_conversor_*.txt
arquivos reais de clientes
planilhas sensíveis
credenciais
tokens
arquivos com CPF, CNPJ, telefone ou e-mail reais
```

Sugestão para `.gitignore`:

```gitignore
# Saídas geradas
saida_meritocracia_*.json
erro_conversor_*.txt

# Arquivos temporários
*.tmp
*.log

# Dados sensíveis
data/
real_data/
producao/
```

---

## 20. Próximas evoluções recomendadas

Possíveis melhorias futuras:

1. Criar agendamento automático do Job.
2. Adicionar notificação em caso de erro.
3. Separar ambiente de desenvolvimento e produção.
4. Criar testes automatizados para a função de conversão.
5. Criar dashboard para acompanhar execuções.
6. Criar política de retenção para arquivos antigos.
7. Integrar o pipeline com repositório Git usando Databricks Git Folder.
8. Criar uma versão em Python package para reaproveitamento fora do notebook.

---

## 21. Resumo final

Este pipeline transforma uma planilha de meritocracia em JSON de forma automatizada, validada e rastreável.

A versão atual já possui:

```text
Entrada parametrizada
Validação de dados
Conversão para JSON
Saída versionada por data/hora
Armazenamento em Volume
Log técnico em Delta Table
Histórico dos resultados
Tratamento de erro
Execução via Job
```

Com isso, o projeto deixa de ser apenas um script Python e passa a ser uma esteira de dados executável, auditável e preparada para evolução.
