from Model.db import db
from Model.tables import Chat, User


# Métodos para criar, ler, atualizar e deletar chamados

def create_chat(dados):
    try:
        chat = Chat(id=dados.get('id'), titulo=dados.get('titulo'), descricao=dados.get('descricao'), id_foto=dados.get('id_foto'))
        db.session.add(chat)
        db.session.commit()
        
        if dados.get("iduser"):
            print("passou aqui")
            user = User(iduser=dados.get('iduser'), nome=dados.get('username'), idchat=chat.id)
            db.session.add(user)
            db.session.commit()
        return {'id': chat.id, 'titulo': chat.titulo}
    except Exception as e:
        print(e)
        return dados


def get_chats():
    chats = Chat.query.all()
    return [{'id': c.id, 'titulo': c.titulo, 'descricao': c.descricao, 'status': c.status, 'id_foto': c.id_foto, 'arquivos': [
        {'id': arquivo.id, 'file_name': arquivo.file_name, "original_name": arquivo.original_name,
         'mimetype': arquivo.mimetype, 'tag': arquivo.tag} for arquivo in c.arquivos], 'users': [{'iduser': user.iduser, 'nome': user.nome} for user in c.users]} for c in chats]


def get_chat(id):
    chat = Chat.query.get(id)
    if chat:
        return {'id': chat.id, 'titulo': chat.titulo, 'descricao': chat.descricao, 'id_foto': chat.id_foto, 'status': chat.status,
                'mensagens': [{'id': m.id, 'texto': m.texto, 'idUser': m.idUser, 'username': m.username,
                               "data": m.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': m.original_name,
                               "file_name": m.file_name, "salvo": m.salvo} for m in
                              chat.mensagens], 'users': [{'iduser': user.iduser, 'nome': user.nome} for user in chat.users]}
    else:
        return False


def update_chat(id, dados):
    chat = Chat.query.get(id)
    if chat:
        data = dados
        chat.titulo = data.get('titulo', chat.titulo)
        chat.descricao = data.get('descricao', chat.descricao)
        chat.status = data.get('status', chat.status)
        chat.id_foto = data.get('id_foto', chat.id_foto)
        db.session.commit()
        return {'message': 'Chamado atualizado com sucesso'}
    else:
        return {'message': 'Chamado não encontrado'}


def delete_chat(id):
    chat = Chat.query.get(id)
    if chat:
        db.session.delete(chat)
        db.session.commit()
        return {'message': 'Chamado deletado com sucesso'}
    else:
        return {'message': 'Chamado não encontrado'}

def search_by_user(id):
    user_specific_chats = Chat.query.join(Chat.users).filter(User.id == id).group_by(Chat.id).all()
    
    return [{'id': c.id, 'titulo': c.titulo, 'descricao': c.descricao, 'status': c.status, 'id_foto': c.id_foto, 'arquivos': [
    {'id': arquivo.id, 'file_name': arquivo.file_name, "original_name": arquivo.original_name,
        'mimetype': arquivo.mimetype, 'tag': arquivo.tag} for arquivo in c.arquivos], 'users': [{'iduser': user.iduser, 'nome': user.nome} for user in c.users]} for c in user_specific_chats]
