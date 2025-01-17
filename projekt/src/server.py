import threading
import argparse
import logging
import socket
import select

from message import Message, MessageType, ClientHello, ServerHello, EndSession
from diffie_hellman import DiffieHellman, generate_session_key
from crypto import Crypto, EncryptedMessage


class ClientSession:
    def __init__(self, client_socket: socket.socket, address: str):
        self.socket = client_socket
        self.address = address
        self.dh: DiffieHellman | None = None
        self.crypto: Crypto | None = None
        self.buffer = b""

    def __str__(self):
        return f"Client({self.address})"


class Server:
    def __init__(self, host: str, port: int, max_clients: int):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.clients: dict[socket.socket, ClientSession] = {}
        self.running = False
        self.server_socket = None

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger('Server')

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_clients)
        self.running = True

        self.logger.info(f"Server started on {self.host}:{self.port}")

        cmd_thread = threading.Thread(target=self.handle_commands)
        cmd_thread.daemon = True
        cmd_thread.start()

        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.logger.info("Shutting down server...")
        finally:
            self.stop()

    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        for client_socket in list(self.clients.keys()):
            self.disconnect_client(client_socket)

    def handle_client_hello(self, client_socket: socket.socket, msg: Message):
        client = self.clients[client_socket]
        client_hello = ClientHello.from_bytes(msg.payload)

        client.dh = DiffieHellman()
        B = client.dh.generate_from_parameters(client_hello.p, client_hello.g)

        shared_secret = client.dh.compute_shared_secret(client_hello.A)
        session_key = generate_session_key(shared_secret)
        client.crypto = Crypto(session_key)

        server_hello = ServerHello(B)
        response = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
        client_socket.send(response.to_bytes())

        self.logger.info(f"Key exchange completed with {client}")

    def send_encrypted_message(self, client_socket: socket.socket, content: bytes):
        client = self.clients[client_socket]
        if not client.crypto:
            raise ValueError("Cannot send encrypted message before key exchange")

        encrypted, iv = client.crypto.encrypt(content)
        enc_msg = EncryptedMessage(iv, encrypted)
        msg = Message(MessageType.ENCRYPTED_MESSAGE, enc_msg.to_bytes())
        client_socket.send(msg.to_bytes())

    def disconnect_client(self, client_socket: socket.socket):
        if client_socket in self.clients:
            client = self.clients[client_socket]
            self.logger.info(f"Disconnecting {client}")
            client_socket.close()
            del self.clients[client_socket]

    def handle_commands(self):
        while self.running:
            cmd = input("Server> ").strip().split()
            if not cmd:
                continue

            if cmd[0] == "list":
                if not self.clients:
                    print("No connected clients")
                else:
                    for i, client in enumerate(self.clients.values(), 1):
                        print(f"{i}. {client}")

            elif cmd[0] == "disconnect":
                try:
                    idx = int(cmd[1]) - 1
                    client_socket = list(self.clients.keys())[idx]

                    if self.clients[client_socket].crypto:
                        end_session = EndSession("Server initiated disconnect")
                        self.send_encrypted_message(client_socket, end_session.to_bytes())

                    self.disconnect_client(client_socket)
                except (IndexError, ValueError):
                    print("Usage: disconnect <client_number>")

            elif cmd[0] == "help":
                print("Available commands:")
                print("  list - List connected clients")
                print("  disconnect <client_number> - Disconnect a client")
                print("  help - Show this help")
                print("  exit - Stop the server")

            elif cmd[0] == "exit":
                self.running = False
                break

    def handle_message(self, client_socket: socket.socket, msg: Message):
        client = self.clients[client_socket]

        if msg.type == MessageType.CLIENT_HELLO:
            self.handle_client_hello(client_socket, msg)

        elif msg.type == MessageType.END_SESSION:
            if client.crypto:
                try:
                    # Decrypt EndSession message
                    enc_msg = EncryptedMessage.from_bytes(msg.payload)
                    decrypted = client.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
                    end_session = EndSession.from_bytes(decrypted)
                    self.logger.info(f"Received EndSession from {client}: {end_session.reason}")
                except ValueError as e:
                    self.logger.error(f"Failed to decrypt EndSession from {client}: {e}")
            self.disconnect_client(client_socket)

        elif msg.type == MessageType.ENCRYPTED_MESSAGE:
            if not client.crypto:
                self.logger.error(f"Received encrypted message from {client} before key exchange")
                return

            try:
                enc_msg = EncryptedMessage.from_bytes(msg.payload)
                decrypted = client.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
                self.logger.info(f"Message from {client}: {decrypted.decode('utf-8')}")
            except ValueError as e:
                self.logger.error(f"Failed to decrypt message from {client}: {e}")

    def main_loop(self):
        while self.running:
            read_sockets = [self.server_socket] + list(self.clients.keys())

            try:
                readable, _, _ = select.select(read_sockets, [], [], 1.0)
            except select.error:
                continue

            for sock in readable:
                if sock is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    if len(self.clients) >= self.max_clients:
                        self.logger.warning(f"Rejecting connection from {address} - max clients reached")
                        client_socket.close()
                        continue

                    self.logger.info(f"New connection from {address}")
                    self.clients[client_socket] = ClientSession(client_socket, address)
                else:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            self.disconnect_client(sock)
                            continue

                        client = self.clients[sock]
                        client.buffer += data

                        while len(client.buffer) >= 5:
                            try:
                                msg = Message.from_bytes(client.buffer)
                                client.buffer = client.buffer[5 + msg.length:]
                                self.handle_message(sock, msg)
                            except (ValueError, IndexError):
                                break

                    except ConnectionError:
                        self.disconnect_client(sock)


def main():
    parser = argparse.ArgumentParser(description='Mini TLS Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=12345, help='Port to bind to')
    parser.add_argument('--max-clients', type=int, default=5, help='Maximum number of clients')

    args = parser.parse_args()
    server = Server(args.host, args.port, args.max_clients)
    server.start()


if __name__ == '__main__':
    main()
