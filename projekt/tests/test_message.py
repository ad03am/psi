import unittest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from message import Message, MessageType, ClientHello, ServerHello, EndSession


class TestMessage(unittest.TestCase):
    def test_message_serialization(self):
        payload = b"test payload"
        msg = Message(MessageType.ENCRYPTED_MESSAGE, payload)
        serialized = msg.to_bytes()
        deserialized = Message.from_bytes(serialized)

        self.assertEqual(deserialized.type, MessageType.ENCRYPTED_MESSAGE)
        self.assertEqual(deserialized.length, len(payload))
        self.assertEqual(deserialized.payload, payload)

    def test_client_hello_serialization(self):
        client_hello = ClientHello(g=5, p=23, A=19)
        serialized = client_hello.to_bytes()
        deserialized = ClientHello.from_bytes(serialized)

        self.assertEqual(deserialized.g, 5)
        self.assertEqual(deserialized.p, 23)
        self.assertEqual(deserialized.A, 19)

    def test_server_hello_serialization(self):
        server_hello = ServerHello(B=15)
        serialized = server_hello.to_bytes()
        deserialized = ServerHello.from_bytes(serialized)

        self.assertEqual(deserialized.B, 15)

    def test_end_session_serialization(self):
        end_session = EndSession("Test disconnect reason")
        serialized = end_session.to_bytes()
        deserialized = EndSession.from_bytes(serialized)

        self.assertEqual(deserialized.reason, "Test disconnect reason")


if __name__ == '__main__':
    unittest.main()