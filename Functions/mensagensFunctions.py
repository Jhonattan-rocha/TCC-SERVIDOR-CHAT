import base64
import mimetypes
import os
import random
import string
from datetime import datetime

from flask_socketio import emit
from sqlalchemy.exc import NoResultFound

from Model.db import db
from Model.tables import Mensagem, Arquivo

mimetypes.init()


def generate_random_string(length):
    letters = string.ascii_letters + string.digits + string.hexdigits
    return ''.join(random.choice(letters) for _ in range(length))


def create_mensagem(dados):
    try:
        print(dados)
        mensagem = Mensagem.query.get(dados['idMes'])
        if mensagem:
            return {'id': mensagem.id, 'texto': mensagem.texto, 'idUser': mensagem.idUser,
                    'username': mensagem.username,
                    "data": mensagem.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': mensagem.original_name,
                    "file_name": mensagem.file_name, "salvo": mensagem.salvo, "mimetype": mensagem.mimetype,
                    "chat_id": mensagem.chat_id, 'type': mensagem.type}
        if dados['type'] == 'file' or dados['type'] == 'audio':
            ext = os.path.splitext(dados['original_name'])
            file_name = generate_random_string(15) + ext[1]
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Construir o caminho para a pasta "uploads"
            uploads_dir = os.path.join(current_dir, "uploads")

            # Criar o diretório "uploads" se não existir
            os.makedirs(uploads_dir, exist_ok=True)

            # Construir o caminho completo para o arquivo
            file_path = os.path.join(uploads_dir, file_name)
            print(file_path)
            with open(file_path, 'wb') as arq:
                if type(dados['file']) is not bytes:
                    dados['file'] = base64.b64decode(dados['file'])
                arq.write(dados['file'])

            mimetype = ""
            if dados['original_name']:
                mimetype = mimetypes.guess_type(dados['original_name'])[0]

            mensagem = Mensagem(id=dados['idMes'], texto=dados['texto'], chat_id=dados['id'], idUser=dados['idUser'],
                                username=dados['username'],
                                data_hora=datetime.now(),
                                original_name=dados['original_name'], file_name=file_name, mimetype=mimetype,
                                salvo=True, type=dados['type'])
            db.session.add(mensagem)
            db.session.commit()
            return {'id': mensagem.id, 'texto': mensagem.texto, 'idUser': mensagem.idUser,
                    'username': mensagem.username,
                    "data": mensagem.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': mensagem.original_name,
                    "file_name": mensagem.file_name, "salvo": mensagem.salvo, "mimetype": mensagem.mimetype,
                    "chat_id": mensagem.chat_id, 'type': mensagem.type}
        if dados['type'] == 'text':
            mensagem = Mensagem(id=dados['idMes'], texto=dados['texto'], chat_id=dados['id'], idUser=dados['idUser'],
                                username=dados['username'],
                                data_hora=datetime.now(), salvo=True, type=dados['type'])
            db.session.add(mensagem)
            db.session.commit()
            return {'id': mensagem.id, 'texto': mensagem.texto, 'idUser': mensagem.idUser,
                    'username': mensagem.username,
                    "data": mensagem.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': mensagem.original_name,
                    "file_name": mensagem.file_name, "salvo": mensagem.salvo, "mimetype": mensagem.mimetype,
                    "chat_id": mensagem.chat_id, 'type': mensagem.type}
    except Exception as e:
        print(e)


def get_mensagens(id: int):
    try:
        chat = Mensagem.query.filter(Mensagem.chat_id == id).order_by(Mensagem.data_hora).all()
        if chat:
            return [{'id': m.id, 'texto': m.texto, 'idUser': m.idUser, 'username': m.username,
                     "data": m.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': m.original_name,
                     "file_name": m.file_name, "salvo": m.salvo,
                     "mimetype": m.mimetype, 'type': m.type, "chat_id": m.chat_id} for m in
                    chat]
        else:
            return {'message': 'chat não encontrado'}
    except Exception as e:
        print(e)
        return


def get_mensagen(id: int):
    try:
        m = Mensagem.query.get(id)
        if m:
            return {'id': m.id, 'texto': m.texto, 'idUser': m.idUser, 'username': m.username,
                    "data": m.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': m.original_name,
                    "file_name": m.file_name, "salvo": m.salvo,
                    "mimetype": m.mimetype, 'type': m.type}
        else:
            return {'message': 'chat não encontrado'}
    except Exception as e:
        print(e)
        return


def search_messages_by_filename(search_filename):
    try:
        matching_messages = Mensagem.query.filter(Mensagem.file_name.like(f'%{search_filename}%')).first()
        return matching_messages
    except NoResultFound:
        return []


def search_messages_by_original_name(search_filename):
    try:
        matching_messages = Mensagem.query.filter(Mensagem.original_name.like(f'%{search_filename}%')).first()
        return matching_messages
    except NoResultFound:
        return []


def search_messages_by_id(chat):
    try:
        idmes = chat["idMes"]
        mes = Mensagem.query.get(idmes)
        date = datetime.strptime(str(mes.data_hora), '%Y-%m-%d %H:%M:%S.%f')
        mensagens = Mensagem.query.filter(Mensagem.data_hora > date, Mensagem.chat_id == chat['id']).order_by(
            Mensagem.data_hora).all()
        return [{'id': m.id, 'texto': m.texto, 'idUser': m.idUser, 'username': m.username,
                 "data": m.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': m.original_name,
                 "file_name": m.file_name, "salvo": m.salvo,
                 "mimetype": m.mimetype, 'type': m.type, "chat_id": m.chat_id} for m in mensagens]
    except Exception as e:
        print(e)
        mensagens = Mensagem.query.filter(Mensagem.chat_id == chat['id']).order_by(
            Mensagem.data_hora).all()
        return [{'id': m.id, 'texto': m.texto, 'idUser': m.idUser, 'username': m.username,
                 "data": m.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': m.original_name,
                 "file_name": m.file_name, "salvo": m.salvo,
                 "mimetype": m.mimetype, 'type': m.type, "chat_id": m.chat_id} for m in mensagens]


def update_mensagem(id, campos_atualizados):
    mensagem = Mensagem.query.get(id)
    if mensagem:
        for campo, valor in campos_atualizados.items():
            if hasattr(mensagem, campo):
                setattr(mensagem, campo, valor)
        db.session.commit()
        return {
            'id': mensagem.id,
            'idMes': mensagem.id,
            'texto': mensagem.texto,
            'idUser': mensagem.idUser,
            'username': mensagem.username,
            "data": mensagem.data_hora.strftime('%Y-%m-%d %H:%M:%S'),
            'original_name': mensagem.original_name,
            "file_name": mensagem.file_name,
            "salvo": mensagem.salvo,
            "mimetype": mensagem.mimetype,
            "chat_id": mensagem.chat_id,
            'type': mensagem.type
        }
    else:
        return False


def delete_mensagem(id):
    mensagem = Mensagem.query.get(id)
    if mensagem:
        db.session.delete(mensagem)
        db.session.commit()
        return {'id': mensagem.id, 'texto': mensagem.texto, 'idUser': mensagem.idUser,
                'username': mensagem.username,
                "data": mensagem.data_hora.strftime('%Y-%m-%d %H:%M:%S'), 'original_name': mensagem.original_name,
                "file_name": mensagem.file_name, "salvo": mensagem.salvo, "mimetype": mensagem.mimetype,
                "chat_id": mensagem.chat_id, 'type': mensagem.type}
    else:
        return {'message': 'Mensagem não encontrada'}


def enviar_mensagens(mensagens, room):
    for mensagen in mensagens:
        emit('messageant', mensagen, room=room)
