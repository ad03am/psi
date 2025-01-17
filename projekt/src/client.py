import socket
import logging
import argparse
import threading
from message import Message, MessageType

class Client:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False

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
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            self.receive_thread = threading.Thread(target=self.receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()

            self.connected = True
            self.logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except ConnectionError as e:
            self.logger.error(f"Connection failed: {e}")
            return False

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
            self.receive_thread = None
        self.connected = False

    def receive_loop(self):
        while self.connected and self.socket:
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
                
    def handle_message(self, msg: Message):
        if msg.type == MessageType.SERVER_HELLO:
            self.handle_server_hello(msg)
        elif msg.type == MessageType.END_SESSION:
            self.handle_end_session(msg)
        elif msg.type == MessageType.ENCRYPTED_MESSAGE:
            self.handle_encrypted_message(msg)
            
    def handle_server_hello(self, msg: Message):
        print("server hello:")
        print(msg)
        
    def handle_end_session(self, msg: Message):
        self.logger.info("Server ended session")
        self.disconnect()
        
    def handle_encrypted_message(self, msg: Message):
        print("encrypted message: ")
        print(msg)

    def start(self):
        try:
            while True:
                cmd = input("Client> ").strip()
                if cmd == "exit":
                    break
                elif cmd == "connect":
                    self.connect()
                elif cmd == "disconnect":
                    self.disconnect()
                elif cmd == "help":
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
