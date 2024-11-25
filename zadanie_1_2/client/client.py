import socket
import sys

HOST = '0.0.0.0'
BUFSIZE = 512
TIMEOUT = 0.5

def generateDatagram(size: int) -> bytes:
    message = bytes([(size & 0xFF00) >> 8, size & 0x00FF])

    for i in range(size - 2):
        message += bytes([ord('A') + (i % 26)])

    return message


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
        sys.exit(1)

    print(f"Connecting to {host}:{port}")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(TIMEOUT)
        seq = 0

        while True:
            message = generateDatagram(BUFSIZE)
            print("Sending buffer sequence number = ", seq, ", data = ", message)

            while True:
                s.sendto(message, (host, port))
                try:
                    data, _ = s.recvfrom(BUFSIZE)

                    if data[:3] == b"ACK" and data[3] == seq:
                        print("Acknowledgment received")
                        seq = 1 - seq
                        break
                    else:
                        print("Incorrect acknowledgment, retransmitting...")
                except socket.timeout:
                    print("Timeout, retransmitting...")

if __name__ == "__main__":
    main(sys.argv[1:])
