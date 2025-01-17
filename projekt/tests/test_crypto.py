import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from crypto import Crypto

class TestCrypto(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32)
        self.crypto = Crypto(self.key)
        
    def test_mac_generation_and_verification(self):
        message = b"test message"
        mac = self.crypto.generate_mac(message)
        
        self.assertTrue(self.crypto.verify_mac(message, mac))
        self.assertFalse(self.crypto.verify_mac(b"wrong message", mac))
        
    def test_encryption_decryption(self):
        message = b"secret message"
        encrypted, iv = self.crypto.encrypt(message)
        decrypted = self.crypto.decrypt(encrypted, iv)
        self.assertEqual(message, decrypted)
        
    def test_mac_verification_failure(self):
        message = b"secret message"
        encrypted, iv = self.crypto.encrypt(message)
        
        tampered = bytearray(encrypted)
        tampered[0] ^= 1
        
        with self.assertRaises(ValueError):
            self.crypto.decrypt(bytes(tampered), iv)


if __name__ == '__main__':
    unittest.main()