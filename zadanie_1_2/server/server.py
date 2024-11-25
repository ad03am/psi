import socket
import sys

HOST = '0.0.0.0'
PORT = 8000
BUFSIZE = 512

def checkData(data: bytes, seq: int) -> bool:
    if len(data) < 3:
        return False

    if data[0] != seq:
        return False

    size = (data[1] << 8) + data[2]
    if size != len(data):
        return False

    for i in range(3, len(data)):
        if data[i] != ord('A') + (i - 3) % 26:
            return False

    return True


def main(arguments: list[str]) -> None:
    print(f"Server at {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        seq = 0

        while True:
            data, address = s.recvfrom(BUFSIZE)
            print(f"Message from Client: {data}")
            print(f"Client IP Address: {address}")
            print(f"Message Length: {len(data)}")

            if checkData(data, seq):
                print("Datagram received correctly")
                s.sendto(b"ACK" + bytes([seq]), address)
                seq = 1 - seq
            else:
                print("Error in datagram")
                s.sendto(b"NACK" + bytes([seq]), address)

if __name__ == "__main__":
    main(sys.argv[1:])
