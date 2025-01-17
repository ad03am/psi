from typing import Dict
import argparse
import logging
import socket
import select


class ClientSession:
    def __init__(self, socket_: socket.socket, address: str):
        self.socket = socket_
        self.address = address
        self.buffer = b""

    def __str__(self):
        return f"Client({self.address})"


class Server:
    def __init__(self, host: str, port: int, max_clients: int):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.clients: Dict[socket.socket, ClientSession] = {}
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
            client_socket.close()

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
