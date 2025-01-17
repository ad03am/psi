import socket
import logging
import argparse
import threading
from message import Message, MessageType, ClientHello, ServerHello, EndSession
from diffie_hellman import DiffieHellman, generate_session_key
from crypto import Crypto, EncryptedMessage

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.dh = None
        self.crypto = None

        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger('Client')
        self.buffer = b""
        self.receive_thread = None

    def connect(self) -> bool:
        if self.connected:
            self.logger.warning("Already connected")
            return False

        try:
            try:
                socket.gethostbyname(self.host)
            except socket.gaierror as e:
                self.logger.error(f"Cannot resolve hostname '{self.host}': {e}")
                return False

            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(1)

            try:
                self.socket.connect((self.host, self.port))
            except Exception as e:
                self.logger.error(f"Connection failed: {e}")
                self.socket.close()
                self.socket = None
                return False
            
            self.socket.settimeout(None)
            self.dh = DiffieHellman()
            g, p, A = self.dh.generate_parameters()
            client_hello = ClientHello(g, p, A)
            msg = Message(MessageType.CLIENT_HELLO, client_hello.to_bytes())
            self.socket.send(msg.to_bytes())

            self.receive_thread = threading.Thread(target=self.receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            self.connected = True
            self.logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        if not self.connected:
            self.logger.warning("Not connected")
            return
        self.connected = False
        if self.socket and self.crypto:
            try:
                end_session = EndSession("Client initiated disconnect")
                self.send_encrypted_message(MessageType.END_SESSION, end_session.to_bytes())
            except Exception as e:
                self.logger.error(f"Error sending EndSession: {e}")

        if self.socket:
            self.socket.close()
            self.socket = None
        current_thread = threading.current_thread()
        if self.receive_thread and current_thread != self.receive_thread:
            self.receive_thread.join(timeout=1.0)
        self.receive_thread = None
        self.crypto = None
        self.dh = None
        self.logger.info("Client disconnected")

    def send(self, cmd: list):
        if len(cmd) < 2:
            print("Usage: send <message>")
            return
        if not self.connected:
            print("Not connected")
            return
        if not self.crypto:
            print("Key exchange not completed")
            return
        message = " ".join(cmd[1:])
        self.send_encrypted_message(MessageType.ENCRYPTED_MESSAGE, message.encode('utf-8'))

    def send_encrypted_message(self, msg_type: MessageType, content: bytes):
        if not self.crypto:
            raise ValueError("Cannot send encrypted message before key exchange")
            
        encrypted, iv = self.crypto.encrypt(content)
        enc_msg = EncryptedMessage(iv, encrypted)
        msg = Message(msg_type, enc_msg.to_bytes())
        self.socket.send(msg.to_bytes())

    def receive_loop(self):
        while self.socket:
            try:
                data = self.socket.recv(4096)
                if not data:
                    self.logger.error("Connection closed by server")
                    self.disconnect()
                    break
                    
                self.buffer += data
                
                while len(self.buffer) >= 5:
                    try:
                        msg = Message.from_bytes(self.buffer)
                        self.buffer = self.buffer[5+msg.length:]
                        self.handle_message(msg)
                    except (ValueError, IndexError):
                        break 

            except (ConnectionError, OSError) as e:
                if self.connected:
                    self.logger.error(f"Connection error: {e}")
                    self.disconnect()
                break
        print("client receive loop ended")

    def handle_message(self, msg: Message):
        if msg.type == MessageType.SERVER_HELLO:
            self.handle_server_hello(msg)
        elif msg.type == MessageType.END_SESSION:
            self.handle_end_session(msg)
        elif msg.type == MessageType.ENCRYPTED_MESSAGE:
            self.handle_encrypted_message(msg)
            
    def handle_server_hello(self, msg: Message):
        server_hello = ServerHello.from_bytes(msg.payload)
        shared_secret = self.dh.compute_shared_secret(server_hello.B)
        session_key = generate_session_key(shared_secret)
        self.crypto = Crypto(session_key)
        self.logger.info("Key exchange completed")
        
    def handle_end_session(self, msg: Message):
        if self.crypto:
            try:
                enc_msg = EncryptedMessage.from_bytes(msg.payload)
                decrypted = self.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
                end_session = EndSession.from_bytes(decrypted)
                self.logger.info(f"Server ended session: {end_session.reason}")
            except ValueError as e:
                self.logger.error(f"Failed to decrypt EndSession: {e}")
        self.disconnect()
        
    def handle_encrypted_message(self, msg: Message):
        if not self.crypto:
            self.logger.error("Received encrypted message before key exchange")
            return

        try:
            enc_msg = EncryptedMessage.from_bytes(msg.payload)
            decrypted = self.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
            print(f"Received message: {decrypted.decode('utf-8')}")
        except ValueError as e:
            self.logger.error(f"Failed to decrypt message: {e}")

    def start(self):
        print(f"Client {self.host}:{self.port} started")
        try:
            while True:
                cmd = input("Client> ").strip().split()
                if not cmd:
                    continue

                if cmd[0] == "exit":
                    break
                elif cmd[0] == "connect":
                    self.connect()
                elif cmd[0] == "disconnect":
                    self.disconnect()
                elif cmd[0] == "send":
                    self.send(cmd)
                elif cmd[0] == "help":
                    self.print_help()
                else:
                    print("Unknown command. Type 'help' for available commands.")
        except KeyboardInterrupt:
            self.logger.info("Shutting down...")
        finally:
            self.disconnect()

    def print_help(self):
        print("Available commands:")
        print("  connect - Connect to server")
        print("  disconnect - Disconnect from server")
        print("  send <message> - Send encrypted message")
        print("  help - Show this help")
        print("  exit - Exit client")

def main():
    parser = argparse.ArgumentParser(description='Mini TLS Client')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=12345, help='Server port')
    
    args = parser.parse_args()
    client = Client(args.host, args.port)
    client.start()

if __name__ == '__main__':
    main()
