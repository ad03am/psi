from enum import Enum
import struct


class MessageType(Enum):
    CLIENT_HELLO = 1
    SERVER_HELLO = 2
    ENCRYPTED_MESSAGE = 3
    END_SESSION = 4


class Message:
    def __init__(self, msg_type: MessageType, payload: bytes):
        self.type = msg_type
        self.length = len(payload)
        self.payload = payload

    def to_bytes(self) -> bytes:
        header = struct.pack('!BI', self.type.value, self.length)
        return header + self.payload

    @staticmethod
    def from_bytes(data: bytes) -> 'Message':
        msg_type, length = struct.unpack('!BI', data[:5])
        payload = data[5:5+length]

        return Message(MessageType(msg_type), payload)


class ClientHello:
    def __init__(self, g: int, p: int, A: int):
        self.g = g
        self.p = p
        self.A = A

    def to_bytes(self) -> bytes:
        return struct.pack('!QQQ', self.g, self.p, self.A)

    @staticmethod
    def from_bytes(data: bytes) -> 'ClientHello':
        g, p, A = struct.unpack('!QQQ', data)
        return ClientHello(g, p, A)


class ServerHello:
    def __init__(self, B: int):
        self.B = B

    def to_bytes(self) -> bytes:
        return struct.pack('!Q', self.B)

    @staticmethod
    def from_bytes(data: bytes) -> 'ServerHello':
        (B,) = struct.unpack('!Q', data)
        return ServerHello(B)


class EndSession:
    def __init__(self, reason: str):
        self.reason = reason

    def to_bytes(self) -> bytes:
        return self.reason.encode('utf-8')

    @staticmethod
    def from_bytes(data: bytes) -> 'EndSession':
        return EndSession(data.decode('utf-8'))
