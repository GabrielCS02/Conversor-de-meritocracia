from flask import Flask, render_template, request
import pandas as pd
import json
from logic import transformar_para_hierarquia

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    json_str = None
    avisos = []
    nome_arquivo = None

    if request.method == 'POST':
        file = request.files.get('arquivo')
        if file and file.filename != '':
            nome_arquivo = file.filename
            df = pd.read_csv(file, encoding='latin1') if file.filename.endswith('.csv') else pd.read_excel(file)
            
            # Gera o dicionário ordenado
            json_data, avisos = transformar_para_hierarquia(df)
            
            # Converte para string formatada mantendo a ordem das chaves
            json_str = json.dumps(json_data, indent=2, ensure_ascii=False, sort_keys=False)

    return render_template('index.html', json_data=json_str, avisos=avisos, nome_arquivo=nome_arquivo)

if __name__ == '__main__':
    app.run(debug=True)