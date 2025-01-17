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
        # Mockujemy socket, żeby przechwycić wysyłane dane
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            # Sprawdzamy czy wysłano ClientHello
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            
            self.assertEqual(msg.type, MessageType.CLIENT_HELLO)
            client_hello = ClientHello.from_bytes(msg.payload)
            
            # Sprawdzamy czy parametry DH są poprawne
            self.assertIsNotNone(client_hello.g)
            self.assertIsNotNone(client_hello.p)
            self.assertIsNotNone(client_hello.A)
            self.assertIn(client_hello.p, self.client.dh.primes)

    def test_server_hello_handling(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            # Symulujemy odpowiedź ServerHello
            server_hello = ServerHello(B=123)  # przykładowa wartość B
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            
            # Sprawdzamy czy klient poprawnie przetwarza ServerHello
            self.client.handle_server_hello(msg)
            
            # Po ServerHello powinien być ustanowiony obiekt crypto
            self.assertIsNotNone(self.client.crypto)

    def test_encrypted_message_handling(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            # Symulujemy wymianę kluczy
            server_hello = ServerHello(B=123)
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            self.client.handle_server_hello(msg)
            
            # Testujemy wysyłanie zaszyfrowanej wiadomości
            test_message = "Test message"
            self.client.send_encrypted_message(
                MessageType.ENCRYPTED_MESSAGE, 
                test_message.encode('utf-8')
            )
            
            # Sprawdzamy czy wiadomość została zaszyfrowana i wysłana
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            self.assertEqual(msg.type, MessageType.ENCRYPTED_MESSAGE)
            
            # Próbujemy odszyfrować wiadomość
            enc_msg = EncryptedMessage.from_bytes(msg.payload)
            decrypted = self.client.crypto.decrypt(enc_msg.ciphertext, enc_msg.iv)
            self.assertEqual(decrypted.decode('utf-8'), test_message)

    def test_end_session(self):
        with patch('socket.socket') as mock_socket:
            mock_socket.return_value.connect = Mock()
            mock_socket.return_value.send = Mock()
            
            self.client.connect()
            
            # Symulujemy wymianę kluczy
            server_hello = ServerHello(B=123)
            msg = Message(MessageType.SERVER_HELLO, server_hello.to_bytes())
            self.client.handle_server_hello(msg)
            
            # Testujemy wysyłanie zaszyfrowanego EndSession
            self.client.disconnect()
            
            # Sprawdzamy czy wysłano zaszyfrowaną wiadomość EndSession
            sent_data = mock_socket.return_value.send.call_args[0][0]
            msg = Message.from_bytes(sent_data)
            self.assertEqual(msg.type, MessageType.END_SESSION)
            
            # Sprawdzamy czy klient jest rozłączony
            self.assertFalse(self.client.connected)
            self.assertIsNone(self.client.crypto)
            self.assertIsNone(self.client.dh)

if __name__ == '__main__':
    unittest.main()