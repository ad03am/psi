import socket
import sys

HOST = '0.0.0.0'
PORT = 8000
BUFSIZE = 512

def checkData(data: bytes) -> bool:
    if len(data) < 2:
        return False

    size = (data[0] << 8) + data[1]
    if size != len(data):
        return False

    for i in range(2, len(data)):
        if data[i] != ord('A') + (i - 2) % 26:
            return False

    return True


def main(arguments: list[str]) -> None:
    if len(arguments) < 1:
        host = HOST
        port = 8000
    elif len(arguments) == 1:
        host = arguments[0]
        port = 8000
    elif len(arguments) == 2:
        host = arguments[0]
        port = int(arguments[1])
    else:
        print("Usage: python client.py <host> <port>")
        return 1
    print(f"Server at {host}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))
        seq = 0
        print(f"socket: {s}")

        while True:
            data, address = s.recvfrom(BUFSIZE)
            print(f"Message from Client: {data}")
            print(f"Client IP Address: {address}")
            print(f"Message Length: {len(data)}")

            if checkData(data):
                print("Datagram received correctly")
                s.sendto(b"ACK" + bytes([seq]), address)
                seq = 1 - seq
            else:
                print("Error in datagram")
                s.sendto(b"NACK" + bytes([seq]), address)

if __name__ == "__main__":
    main(sys.argv[1:])
