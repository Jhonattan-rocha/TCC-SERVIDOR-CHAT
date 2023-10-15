from flask import Blueprint, request, jsonify
from Functions.arquivosFunctions import delete_arquivo, update_arquivo

app = Blueprint('arquivos', __name__)


@app.patch('/arquivo/<id>')
def editar_arquivo(id):
    try:
        dados = request.json  # Ou request.get_json()
        chat = update_arquivo(id, dados)
        if chat:
            return jsonify(chat), 200
        else:
            return jsonify({'error': 'bad request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.delete('/arquivo/<id>')
def deletar_arquivo(id):
    try:
        [message, arquivo] = delete_arquivo(id)

        return '', 200  # Retorna JSON vazio com status 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400
