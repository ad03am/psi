import socket
import sys

HOST = '127.0.0.1'

def generateDatagram(size: int) -> bytes:
    message = bytes([(size & 0xFF00) >> 8, size & 0x00FF])

    for i in range(size - 2):
        message += bytes([ord('A') + (i % 26)])

    return message


def main(arguments: list[str]) -> None:
    if len(arguments) < 1:
        port = 8000
    elif len(arguments) == 1:
        port = int(arguments[0])
    else:
        print("Usage: python client.py <port>")
        sys.exit(1)

    print(f"Connecting to {HOST}:{port}")
    size = 65500

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            message = generateDatagram(size)
            print("Sending buffer size = ", size, ", data = ", message)

            s.sendto(message, (HOST, port))
            data = s.recv(size)
            print('Received', repr(data))

            if data != message:
                print("Error in datagram")
                break

            size += 1


if __name__ == "__main__":
    main(sys.argv[1:])
