import mimetypes
import os

from flask import Blueprint, request, jsonify, Response

from Functions.arquivosFunctions import search_files_by_filename, search_files_by_originalname, create_arquivo
from Functions.chatFunctions import create_chat, update_chat, delete_chat, get_chats, search_by_user
from Functions.mensagensFunctions import get_mensagens, search_messages_by_filename, \
    search_messages_by_original_name, generate_random_string
from middlewares.filter import handle_custom_filter

mimetypes.init()

app = Blueprint('chat', __name__)


@app.get('/download/<filename>')
def download_file(filename):
    try:
        arquivo = search_messages_by_filename(filename) or search_messages_by_original_name(
            filename) or search_files_by_filename(filename) or search_files_by_originalname(filename)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, "..", 'Functions', "uploads")

        if not os.path.exists(f"{path}\\{arquivo.file_name}"):
            return {"error": 'not found'}, 404

        if arquivo and os.path.exists(f"{path}\\{arquivo.file_name}"):
            # Leitura do arquivo em bytes
            with open(f"{path}\\{arquivo.file_name}", 'rb') as file:
                file_data = file.read()

            response = Response(
                file_data,
                content_type=arquivo.mimetype,
                headers={
                    "Content-Disposition": f'attachment; filename="{arquivo.original_name}"'
                }
            )
            return response
    except Exception as e:
        print(e)
        return {"error": 'bad request'}, 400


@app.patch('/chat_foto/<int:idchat>')
def receive_file(idchat):
    try:
        # Verifique se um arquivo foi enviado na solicitação
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']

        # Verifique se o nome do arquivo não está vazio
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400

        # Obtenha a extensão do arquivo e gere um nome de arquivo seguro
        ext = os.path.splitext(file.filename)[-1].lower()
        filename = generate_random_string(20) + ext

        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Construir o caminho para a pasta "uploads"
        uploads_dir = os.path.join(current_dir, "..", 'Functions', "uploads")

        # Criar o diretório "uploads" se não existir
        os.makedirs(uploads_dir, exist_ok=True)

        # Salve o arquivo no caminho especificado
        file.save(os.path.join(uploads_dir, filename))

        # Determine o mimetype do arquivo
        mimetype = mimetypes.guess_type(filename)[0]

        # Crie um registro de arquivo no banco de dados
        dados = {
            'mimetype': mimetype,
            'file_name': filename,
            'original_name': file.filename,
            'idchat': idchat,
            'tag': request.form['tag']
        }
        arquivo = create_arquivo(dados)

        return jsonify({'message': 'Arquivo recebido com sucesso', 'arquivo': arquivo}), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Erro ao receber arquivo'}), 400


@app.get('/chat/<idchat>')
def get_chat_data(idchat):
    try:
        chat = get_mensagens(idchat)
        if chat:
            return jsonify(chat), 200
        else:
            return jsonify([{"Error": 'Mensagens não encontradas'}]), 404
    except Exception as e:
        print(e)
        return jsonify([{"Error": 'Erro ao buscar o chat'}]), 400


@app.post('/chat/')
def cadastrar_chat():
    try:
        dados = request.json  # Ou request.get_json()
        chat = create_chat(dados)
        if chat:
            return jsonify(chat), 200
        else:
            return jsonify({'error': 'bad request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.patch('/chat/<id>')
def editar_chat(id):
    try:
        dados = request.json  # Ou request.get_json()
        chat = update_chat(id, dados)
        if chat:
            return jsonify(chat), 200
        else:
            return jsonify({'error': 'bad request'}), 400
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.delete('/chat/<id>')
def deletar_chat(id):
    try:
        delete_chat(id)
        return '', 200  # Retorna JSON vazio com status 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400


@app.get('/chat/')
def listar_chats():
    try:
        user = request.args.get('user')
        if user:
            return search_by_user(int(user))
        else:        
            chats = get_chats()
            return jsonify(chats), 200
    except Exception as e:
        print(e)
        return jsonify({'error': 'Bad request'}), 400
