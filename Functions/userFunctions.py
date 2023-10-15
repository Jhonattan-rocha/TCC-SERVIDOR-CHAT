from flask import jsonify

from Model.db import db
from Model.tables import User


def criar_usuario(dados):
    try:
        novo_usuario = User(nome=dados['nome'], idchat=dados['idchat'])
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({'message': 'Usuário criado com sucesso'}), 201
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao criar usuário'}), 400


def listar_usuarios():
    try:
        usuarios = User.query.all()
        usuarios_json = [{'id': user.id, 'nome': user.nome, 'idchat': user.idchat} for user in usuarios]
        return jsonify(usuarios_json), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao listar usuários'}), 400


def obter_usuario(user_id):
    try:
        usuario = User.query.get(user_id)
        if usuario:
            usuario_json = {'id': usuario.id, 'nome': usuario.nome, 'idchat': usuario.idchat}
            return jsonify(usuario_json), 200
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao obter usuário'}), 400


def atualizar_usuario(user_id, dados):
    try:
        usuario = User.query.get(user_id)
        if usuario:
            usuario.nome = dados['nome']
            usuario.idchat = dados['idchat']
            db.session.commit()
            return jsonify({'message': 'Usuário atualizado com sucesso'}), 200
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao atualizar usuário'}), 400


def excluir_usuario(user_id):
    try:
        usuario = User.query.get(user_id)
        if usuario:
            db.session.delete(usuario)
            db.session.commit()
            return jsonify({'message': 'Usuário excluído com sucesso'}), 200
        else:
            return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao excluir usuário'}), 400
