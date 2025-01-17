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
