import socket
import threading
import sys
from cryptography.fernet import Fernet
import struct
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

HOST = "127.0.0.1"
PORT = 8081


class Server(threading.Thread):
    def __init__(self, HOST, PORT, id_chat) -> None:
        threading.Thread.__init__(self)
        self.HOST = HOST
        self.PORT = PORT
        self.BYTES = 2048
        self.clients = []
        self.end = True
        self.key = Fernet.generate_key()
        self.fernet = Fernet(self.key)
        self.private_assimetric_key = None
        self.public_assimetric_key = None
        self.id_chat = id_chat

    def encrypt_large_message(self, message):
        encrypted_blocks = []

        # Dividir a mensagem em blocos de 128 bits (16 bytes)
        blocks = [message[i:i + 16] for i in range(0, len(message), 16)]

        # Criptografar cada bloco individualmente
        for block in blocks:
            # Adicionar padding ao bloco, se necessário
            if len(block) < 16:
                block += b"\0" * (16 - len(block))

            # Criptografar o bloco e adicionar à lista de blocos criptografados
            encrypted_blocks.append(self.fernet.encrypt(block))

        return b" ".join(encrypted_blocks)

    def decrypt_large_message(self, encrypted_blocks: bytes):
        encrypted_blocks = encrypted_blocks.split(b" ")

        decrypted_blocks = []

        # Descriptografar cada bloco individualmente
        for block in encrypted_blocks:
            decrypted_blocks.append(self.fernet.decrypt(block).strip(b"\0"))

        # Concatenar os blocos descriptografados para obter a mensagem original
        message = b"".join(decrypted_blocks)

        return message.rstrip(b"\0")

    def receive_message(self, sock):
        # primeiro, receba o tamanho da mensagem
        raw_msglen = sock.recv(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # em seguida, receba a mensagem em blocos
        chunks = []
        bytes_received = 0
        while bytes_received < msglen:
            chunk = sock.recv(min(msglen - bytes_received, 2048))
            if not chunk:
                raise RuntimeError('Conexão interrompida')
            chunks.append(chunk)
            bytes_received += len(chunk)
        # junte os blocos e retorne a mensagem
        return b" ".join(chunks)

    def send_message(self, sock, message):
        # primeiro, envie o tamanho da mensagem
        msglen = len(message)
        sock.sendall(struct.pack('>I', msglen))
        # em seguida, envie a mensagem em blocos
        offset = 0
        while offset < msglen:
            sent = sock.send(message[offset:offset + 2048])
            if not sent:
                raise RuntimeError('Conexão interrompida')
            offset += sent

    def send_file(self, sock, file_path):
        with open(file_path, 'rb') as f:
            file_data = f.read()
            encrypted_data = self.encrypt_large_message(file_data)
            self.send_message(sock, encrypted_data)

    def receive_file(self, sock, file_path):
        encrypted_data = self.receive_message(sock)
        decrypted_data = self.decrypt_large_message(encrypted_data)
        with open(file_path, 'wb') as f:
            f.write(decrypted_data)

    def send_messages(self, message):
        message_bytes = self.encrypt_large_message(message=message)
        for client in self.clients:
            self.send_message(client[1], message_bytes)

    def save_clients(self, client):
        if client not in self.clients:
            self.clients.append(client)

    def send_encrypted_key(self, client):
        self.private_assimetric_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_assimetric_key = self.private_assimetric_key.public_key()

        public_key_client = client.recv(2048)

        public_key_client_serialized = serialization.load_pem_public_key(
            public_key_client,
            backend=default_backend()
        )

        key_fernet = public_key_client_serialized.encrypt(
            self.key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        client.sendall(key_fernet)

    def client_handle(self, client, address):

        self.send_encrypted_key(client)

        try:
            while 1:
                username = self.decrypt_large_message(self.receive_message(client))
                if not username:
                    self.send_message(client, "Nome inválido".encode())
                self.save_clients((username, client))
                self.send_messages(str("SERVER:" + f"{username} entrou no chat").encode())
                threading.Thread(target=self.listen_message, args=(client, username)).start()
                break
        except Exception as E:
            print("caiu aqui")
            print(E)
            sys.exit(1)

    def run(self) -> None:
        global server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:

            server.bind((self.HOST, self.PORT))
            server.listen()

            print("Servidor rodando")

            while self.end:

                _ = input("Press ENTER for accept new client")

                (client, address) = server.accept()

                print(f"Conexão com o cliente do address {address}")
                try:
                    threading.Thread(target=self.client_handle, args=(client, address)).start()
                except KeyboardInterrupt:
                    sys.exit(1)
                except Exception as e:
                    print(e)
                    sys.exit(1)

    def listen_message(self, client, username):
        with client:
            while True:
                message = self.receive_message(client)
                if not message:
                    self.send_message(client, "Mensagem invalida".encode())
                    break

                if b"exit" in self.decrypt_large_message(message):
                    self.end = False
                    server.close()
                    sys.exit(0)

                self.send_messages(f"[{username}]:[{self.decrypt_large_message(message).decode()}]".encode())


if __name__ == "__main__":
    server2 = Server(HOST=HOST, PORT=PORT, id_chat=2)
    server2.start()
