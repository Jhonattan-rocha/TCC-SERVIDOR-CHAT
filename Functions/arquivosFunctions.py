import base64
import mimetypes
import os
import random
import string

from sqlalchemy.exc import NoResultFound

from Model.db import db
from Model.tables import Arquivo

mimetypes.init()


def generate_random_string(length):
    letters = string.ascii_letters + string.digits + string.hexdigits
    return ''.join(random.choice(letters) for _ in range(length))


def create_arquivo(dados):
    try:

        arquivo = Arquivo(
            mimetype=dados['mimetype'],
            file_name=dados['file_name'],
            original_name=dados['original_name'],
            idchat=dados['idchat'],
            tag=dados['tag']
        )

        exits = Arquivo.query.filter(Arquivo.original_name.like(f'%{arquivo.tag}%')).first()
        if exits:
            os.remove(os.path.join('.', 'uploads', exits.file_name))
            db.session.delete(exits)
            db.session.commit()
        db.session.add(arquivo)
        db.session.commit()

        return {'id': arquivo.id, 'mimetype': arquivo.mimetype, 'file_name': arquivo.file_name, 'original_name': arquivo.original_name}
    except Exception as e:
        print(e)
        return None


# Função para excluir um arquivo e removê-lo da pasta ./uploads
def delete_arquivo(arquivo_id):
    try:
        arquivo = Arquivo.query.get(arquivo_id)
        if arquivo:
            # Remover o arquivo da pasta ./uploads
            current_dir = os.path.dirname(os.path.abspath(__file__))

            # Construir o caminho para a pasta "uploads"
            uploads_dir = os.path.join(current_dir, "uploads")

            # Criar o diretório "uploads" se não existir
            os.makedirs(uploads_dir, exist_ok=True)

            # Construir o caminho completo para o arquivo
            file_path = os.path.join(uploads_dir, arquivo.file_name)
            if os.path.exists(file_path):
                os.remove(file_path)

            db.session.delete(arquivo)
            db.session.commit()
            return {'message': 'Arquivo deletado com sucesso'}, arquivo
        else:
            return {'message': 'Arquivo não encontrado'}
    except Exception as e:
        print(e)
        return None


# Função para obter informações de um arquivo
def get_arquivo(arquivo_id):
    arquivo = Arquivo.query.get(arquivo_id)
    if arquivo:
        return {'id': arquivo.id, 'mimetype': arquivo.mimetype, 'file_name': arquivo.file_name,
                'original_name': arquivo.original_name}
    else:
        return {'message': 'Arquivo não encontrado'}


# Função para atualizar informações de um arquivo
def update_arquivo(arquivo_id, data):
    arquivo = Arquivo.query.get(arquivo_id)
    if arquivo:
        try:
            arquivo.mimetype = data.get('mimetype', arquivo.mimetype)
            arquivo.file_name = data.get('file_name', arquivo.file_name)
            arquivo.original_name = data.get('original_name', arquivo.original_name)
            db.session.commit()
            return {'message': 'Arquivo atualizado com sucesso'}
        except Exception as e:
            print(e)
            return None
    else:
        return {'message': 'Arquivo não encontrado'}


def search_files_by_filename(search_file_name):
    try:
        matching = Arquivo.query.filter(Arquivo.file_name.like(f'%{search_file_name}%')).first()
        return matching
    except NoResultFound:
        return []


def search_files_by_originalname(search_file_name):
    try:
        matching = Arquivo.query.filter(Arquivo.original_name.like(f'%{search_file_name}%')).first()
        return matching
    except NoResultFound:
        return []
