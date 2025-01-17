import unittest
import socket
import threading
import time
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from client import Client
from message import Message, MessageType, ClientHello, ServerHello, EndSession
from crypto import EncryptedMessage

class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client('localhost', 12345)
        self.received_messages = []

    def test_client_hello_generation(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            
            self.assertEqual(msg.type, MessageType.CLIENT_HELLO)
            client_hello = ClientHello.from_bytes(msg.payload)
            
            self.assertIsNotNone(client_hello.g)
            self.assertIsNotNone(client_hello.p)
            self.assertIsNotNone(client_hello.A)
            self.assertIn(client_hello.p, self.client.dh.primes)

    def test_server_hello_handling(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            server_hello = ServerHello(B=123)
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            
            self.client.handle_server_hello(msg)
            
            self.assertIsNotNone(self.client.crypto)

    def test_encrypted_message_handling(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            server_hello = ServerHello(B=123)
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            self.client.handle_server_hello(msg)
            
            test_message = "Test message"
            self.client.send_encrypted_message(
                MessageType.ENCRYPTED_MESSAGE, 
                test_message.encode('utf-8')
            )
            
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            self.assertEqual(msg.type, MessageType.ENCRYPTED_MESSAGE)
            
            enc_msg = EncryptedMessage.from_bytes(msg.payload)
            decrypted = self.client.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
            self.assertEqual(decrypted.decode('utf-8'), test_message)

    def test_end_session(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            server_hello = ServerHello(B=123)
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            self.client.handle_server_hello(msg)
            self.client.disconnect()
            
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            self.assertEqual(msg.type, MessageType.END_SESSION)
            self.assertFalse(self.client.connected)
            self.assertIsNone(self.client.crypto)
            self.assertIsNone(self.client.dh)

    def test_disconnect_sends_encrypted_end_session(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.send = Mock()
            self.client.socket = mock_socket.return_value
            self.client.connected = True
            self.client.crypto = Mock()
            
            # Symulujemy szyfrowanie
            test_iv = b"test_iv"
            test_encrypted = b"test_encrypted"
            self.client.crypto.encrypt.return_value = (test_encrypted, test_iv)
            
            self.client.disconnect()
            
            # Sprawdzamy czy wysłano zaszyfrowaną wiadomość EndSession
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            self.assertEqual(msg.type, MessageType.END_SESSION)
            
            enc_msg = EncryptedMessage.from_bytes(msg.payload)
            self.assertEqual(enc_msg.iv, test_iv)
            self.assertEqual(enc_msg.ciphertext, test_encrypted)

if __name__ == '__main__':
    unittest.main()