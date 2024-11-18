import socket
import sys

HOST = '0.0.0.0'

def generateDatagram(size: int) -> bytes:
    message = bytes([(size & 0xFF00) >> 8, size & 0x00FF])

    for i in range(size - 2):
        message += bytes([ord('A') + (i % 26)])

    return message


def main(arguments: list[str]) -> None:
    if len(arguments) < 2:
        host = HOST
        port = 8000
    elif len(arguments) == 2:
        host = arguments[0]
        port = int(arguments[1])
    else:
        print("Usage: python client.py <host> <port>")
        sys.exit(1)

    print(f"Connecting to {host}:{port}")
    size = 65500

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            message = generateDatagram(size)
            print("Sending buffer size = ", size, ", data = ", message)

            s.sendto(message, (host, port))
            data = s.recv(size)
            print('Received', repr(data))
            print(f"Message Length: {len(data)}")

            if data != b"OK\x00":
                print("Error in datagram")
                break

            size += 1


if __name__ == "__main__":
    main(sys.argv[1:])
