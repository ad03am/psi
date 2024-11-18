import socket
import sys

HOST = '127.0.0.1'
BUFSIZE = 65536

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
        port = 8000
    elif len(arguments) == 1:
        port = int(arguments[0])
    else:
        print("Usage: python server.py <port>")
        sys.exit(1)

    print(f"Connecting to {HOST}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, port))

        while True:
            data_address = s.recvfrom(BUFSIZE)
            data = data_address[0]
            address = data_address[1]
            print(f"Message from Client: {data}")
            print(f"Client IP Address: {address}")

            if not checkData(data):
                print("Error in datagram")
                break

            s.sendto(data, address)


if __name__ == "__main__":
    main(sys.argv[1:])
