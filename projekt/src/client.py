import socket
import logging
import argparse

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
        
    def connect(self) -> bool:
        if self.connected:
            self.logger.warning("Already connected")
            return False
            
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
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
        self.connected = False
        
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
