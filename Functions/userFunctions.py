from Model.db import db
from Model.tables import User


def create_user(dados):
    novo_usuario = User(iduser=dados['iduser'], nome=dados['nome'], idchat=dados['idchat'])
    db.session.add(novo_usuario)
    db.session.commit()
    return {'message': 'Usuário criado com sucesso'}

def list_users():
    usuarios = User.query.all()
    usuarios_json = [{'iduser': user.iduser, 'iduser': user.iduser, 'nome': user.nome, 'idchat': user.idchat} for user in usuarios]
    return usuarios_json


def get_user(user_id):
    usuario = User.query.get(user_id)
    if usuario:
        usuario_json = {'id': usuario.id, 'iduser': usuario.iduser, 'nome': usuario.nome, 'idchat': usuario.idchat}
        return usuario_json
    else:
        return {'error': 'Usuário não encontrado'}


def update_user(user_id, dados):
    usuario = User.query.get(user_id)
    if usuario:
        usuario.nome = dados['nome']
        usuario.idchat = dados['idchat']
        db.session.commit()
        return {'message': 'Usuário atualizado com sucesso'}
    else:
        return {'error': 'Usuário não encontrado'}


def delete_user(user_id):
    usuario = User.query.get(user_id)
    if usuario:
        db.session.delete(usuario)
        db.session.commit()
        return {'message': 'Usuário excluído com sucesso'}
    else:
        return {'error': 'Usuário não encontrado'}

