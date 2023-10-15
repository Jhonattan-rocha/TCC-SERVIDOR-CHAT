import socket
import struct
import sys
import threading

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding

HOST = "127.0.0.1"
PORT = 8080
BYTES = 2048


class Client(threading.Thread):
    def __init__(self, HOST, PORT, BYTES) -> None:
        threading.Thread.__init__(self)
        self.private_assimetric_key = None
        self.public_assimetric_key = None
        self.HOST = HOST
        self.PORT = PORT
        self.BYTES = BYTES
        self.key = None
        self.fernet = None

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
        # caso de problema, substituir para encrypted_blocks.split(b" ")
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
            # testa se o que falta é menor que 2048, pois é o máximo, se não for menor, ele sempre lerá 20248 até acabar
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
        print(decrypted_data)
        with open(file_path, 'wb') as f:
            f.write(decrypted_data)

    def receive_encrypted_key(self, client):
        self.private_assimetric_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        self.public_assimetric_key = self.private_assimetric_key.public_key()

        client.sendall(self.public_assimetric_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

        key_fernet = client.recv(2048)

        key_fernet_decrypted = self.private_assimetric_key.decrypt(
            key_fernet,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        self.key = key_fernet_decrypted
        self.fernet = Fernet(self.key)

    def run(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            try:
                client.connect((HOST, PORT))
                self.receive_encrypted_key(client)

                terminar = True
                print("Digite exit para terminar")
                while terminar:
                    messageStr = input("Digite algo: ").encode()

                    if messageStr == b"exit":
                        terminar = False
                        continue

                    self.send_message(client, self.encrypt_large_message(messageStr))

                    if b'arquivo' in messageStr:
                        # arquivo 'C:\Users\FATEC ZONA LESTE\Desktop\SENHAS.txt'
                        print(self.decrypt_large_message(self.receive_message(client)))
                        continue

                    message = self.receive_message(client)

                    print(self.decrypt_large_message(message))

            except KeyboardInterrupt:
                sys.exit(1)
            except Exception as e:
                print(e)
                sys.exit(1)
            finally:
                client.close()


if __name__ == "__main__":
    client = Client(HOST, PORT, BYTES)
    client.start()
