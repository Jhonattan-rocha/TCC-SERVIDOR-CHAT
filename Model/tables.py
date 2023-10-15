from datetime import datetime

from Model.db import db


class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200))
    descricao = db.Column(db.String(200))
    status = db.Column(db.String(20), default='em aberto')
    chave = db.Column(db.String(255), nullable=True)
    mensagens = db.relationship('Mensagem', backref='chat', lazy=True)
    arquivos = db.relationship('Arquivo', backref='chat', lazy=True)
    users = db.relationship('User', backref='chat', lazy=True)


class Arquivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mimetype = db.Column(db.String(100))
    file_name = db.Column(db.String(255))
    original_name = db.Column(db.String(255))
    tag = db.Column(db.String(100))
    idchat = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String)
    idchat = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)


class Mensagem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    texto = db.Column(db.Text, nullable=False)
    idUser = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String, nullable=False)
    data_hora = db.Column(db.DateTime, default=lambda: datetime.now())
    salvo = db.Column(db.Boolean)
    mimetype = db.Column(db.String)
    file_name = db.Column(db.String)
    original_name = db.Column(db.String)
    chat_id = db.Column(db.Integer, db.ForeignKey('chat.id'), nullable=False)
