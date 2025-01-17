import os
import hmac
import hashlib

class Crypto:
    def __init__(self, key: bytes):
        self.key = key
        
    def generate_mac(self, message: bytes) -> bytes:
        h = hmac.new(self.key, message, hashlib.sha256)
        return h.digest()
        
    def verify_mac(self, message: bytes, mac: bytes) -> bool:
        calculated_mac = self.generate_mac(message)
        return hmac.compare_digest(calculated_mac, mac)
        
    def generate_one_time_pad(self, iv: bytes, length: int) -> bytes:
        pad = b""
        block = iv
        while len(pad) < length:
            h = hmac.new(self.key, block, hashlib.sha256)
            pad += h.digest()
            block = h.digest()
        return pad[:length]
        
    def encrypt(self, message: bytes):
        mac = self.generate_mac(message)
        data = message + mac
        
        iv = os.urandom(16)
        pad = self.generate_one_time_pad(iv, len(data))
        encrypted = bytes(a ^ b for a, b in zip(data, pad))
        
        return encrypted, iv
        
    def decrypt(self, ciphertext: bytes, iv: bytes) -> bytes:
        pad = self.generate_one_time_pad(iv, len(ciphertext))
        decrypted = bytes(a ^ b for a, b in zip(ciphertext, pad))
        
        message = decrypted[:-32]
        received_mac = decrypted[-32:]

        if not self.verify_mac(message, received_mac):
            raise ValueError("MAC verification failed")

        return message

