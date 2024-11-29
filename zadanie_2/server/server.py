import threading
import socket


HOST = '0.0.0.0'
PORT = 8000
BUFSIZE = 1024
DATA_SIZE = 100 * 1024  # 100 kB


def do_client(conn, addr) -> None:
    with conn:
        print("Connected by client at", addr)
        received_data = b''
        while len(received_data) < DATA_SIZE:
            data = conn.recv(BUFSIZE)
            if not data:
                break
            received_data += data
        print(f"Received {len(received_data)} bytes")
        conn.sendall(received_data)
        print("Data sent back to client")

    conn.close()
    print("Connection closed by client at", addr)


def main() -> None:
    print(f"Server at {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)

        while True:
            conn, addr = s.accept()

            client = threading.Thread(target=do_client, args=(conn, addr))
            client.start()


if __name__ == "__main__":
    main()
