import socket
import sys


HOST = '0.0.0.0'
PORT = 8000
BUFSIZE = 1024
DATA_SIZE = 100 * 1024  # 100 kB


def main(arguments: list[str]) -> None:
    if len(arguments) < 1:
        host = HOST
        port = PORT
    elif len(arguments) == 1:
        host = arguments[0]
        port = PORT
    elif len(arguments) == 2:
        host = arguments[0]
        port = int(arguments[1])
    else:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    data_to_send = b'a' * DATA_SIZE
    print(f"Connecting to {host}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data_to_send)

        print(f"Sent {len(data_to_send)} bytes")

        received_data = b''
        while len(received_data) < DATA_SIZE:
            data = s.recv(BUFSIZE)

            if not data:
                break
            received_data += data

        print(f"Received {len(received_data)} bytes")

    print('Client finished.')


if __name__ == "__main__":
    main(sys.argv[1:])
