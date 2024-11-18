import socket
import sys

HOST = '0.0.0.0'
PORT = 8000
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


def main() -> None:

    print(f"Server at {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))

        while True:
            data_address = s.recvfrom(BUFSIZE)
            data = data_address[0]
            address = data_address[1]
            print(f"Message from Client: {data}")
            print(f"Client IP Address: {address}")
            print(f"Message Length: {len(data)}")

            if not checkData(data):
                print("Error in datagram")
                break

            s.sendto(b"OK\x00", address)


if __name__ == "__main__":
    main()
