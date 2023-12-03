from flask import Blueprint, request, jsonify

from Functions.userFunctions import *

app = Blueprint('user', __name__)

@app.post('/user/')
def cad_user():
    try:
        dados = request.json  # Ou request.get_json()
        user = create_user(dados)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'bad request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400



@app.patch('/user/<id>')
def editar_user(id):
    try:
        dados = request.json  # Ou request.get_json()
        user = update_user(id, dados)
        if user:
            return jsonify(user), 200
        else:
            return jsonify({'error': 'bad request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.delete('/user/<id>')
def deletar_user(id):
    try:
        delete_user(id)
        return '', 200  # Retorna JSON vazio com status 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.get('/user/')
def listar_users():
    try:     
        users = list_users()
        return jsonify(users), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400
