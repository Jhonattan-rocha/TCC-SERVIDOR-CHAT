import mimetypes
import os
import time

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_sqlalchemy import SQLAlchemy

from Functions.chatFunctions import create_chat, get_chat
from Functions.mensagensFunctions import create_mensagem, update_mensagem, search_messages_by_id, delete_mensagem
from Model.db import db

clients = []
mimetypes.init()


def create_app(db: SQLAlchemy) -> Flask:
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "oiahsfoiwqhfndskandsnaposialsdailsd~lashdaposjds"
    app.config['UPLOAD_FOLDER'] = os.path.abspath("./Functions/uploads")
    db.init_app(app)

    CORS(app, origins=['http://localhost:3000/', "*"])

    from Routes.chatRoutes import app as app_chat
    app.register_blueprint(app_chat)

    from Routes.arquivosRoutes import app as app_arquivos
    app.register_blueprint(app_arquivos)

    return app


app = create_app(db=db)

with app.app_context():
    db.create_all()

socketio = SocketIO(app, cors_allowed_origins=['http://localhost:3000', "*"],
                    max_http_buffer_size=50*1024*1024)


@socketio.on('connect')
def connect():
    print('Connect')


@socketio.on('disconnect')
def on_disconnect():
    try:
        for client in clients:
            if client['id'] == request.sid:
                leave_room(client['room'])
                clients.remove(client)
                disconnect()
                print("User left chat room:", client['room'])
                break
    except Exception as e:
        print("Error while disconnecting:", e)


@socketio.on("chat")
def cad_chat(message):
    try:
        chat = get_chat(message['id'])
        if chat:
            join_room(chat.get('id'))
            clients.append({'id': request.sid, 'room': chat.get('id')})  # Store client's room information
            emit("success", chat, room=chat.get('id'), broadcast=True, include_self=True)
            return
        else:
            response = create_chat(message)
            join_room(response.get('id'))
            clients.append({'id': request.sid, 'room': response.get('id')})  # Store client's room information
            emit("success", response, room=response.get('id'), broadcast=True, include_self=True)
            return
    except Exception as e:
        emit("error", {"Error": f"Erro ao criar um chat: {e}"}, room=message['id'], broadcast=True, include_self=True)


@socketio.on('re')
def recharge_chat(chat):
    try:
        print(chat)
        mens = search_messages_by_id(chat)

        for me in mens:
            time.sleep(0.2)
            try:
                emit('reChat', me, room=chat['id'], broadcast=True, include_self=True)
            except Exception as e:
                print(e)

    except Exception as e:
        print(e)
        emit("error", {"Error": "Não foi possível buscar as mensagens"}, room=chat['id'], broadcast=True,
             include_self=True)


@socketio.on('message')
def handle_chat(dados):
    mes = create_mensagem(dados)
    try:
        print(mes)
        # message_semaphore.acquire()
        if dados['type'] == 'text':
            emit('message', mes, room=mes['chat_id'], broadcast=True, include_self=True)
        else:
            if dados['type'] == 'audio':
                emit('audio_data', mes, room=mes['chat_id'], broadcast=True, include_self=True)
            if dados['type'] == 'file':
                emit('file_data', mes, room=mes['chat_id'], broadcast=True, include_self=True)
    except AttributeError as at:
        print(at)
        return {'Error': "mensagem duplicada"}, 409


@socketio.on('edit')
def edit_message(message):
    try:
        print(message)
        mes = update_mensagem(message['id'], message)
        if mes:
            handle_chat(mes)
            return mes, 200
        return {'erro': 'mensagem não encontrado'}, 404
    except Exception as e:
        print(e)
        return {'Error': "Erro ao editar a mensagem"}, 400


@socketio.on("deletemes")
def delmes(message):
    try:
        mes = delete_mensagem(message['id'])
        if mes:
            emit('delmes', mes, room=mes['chat_id'], broadcast=True, include_self=True)
            return mes, 200
        return {'erro': 'mensagem não encontrado'}, 404
    except Exception as e:
        print(e)
        return {'Error': "Erro ao deletar a mensagem"}, 400


@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    print(room, "join")
    emit('join', data, room=room, broadcast=True, include_self=True)  # Inclua o parâmetro 'room'


@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    print(room, "leave")
    emit('leave', data, room=room, broadcast=True, include_self=True)  # Inclua o parâmetro 'room'


socketio.run(app, debug=True, host="10.0.0.100", port=5000, allow_unsafe_werkzeug=True, use_reloader=True, )
