import socket

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


def main() -> None:
    print(f"Server at {HOST}:{PORT}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        seq = 0

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
    main()
