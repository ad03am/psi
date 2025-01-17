import os
import hmac
import hashlib
import struct

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

class EncryptedMessage:
    def __init__(self, iv: bytes, ciphertext: bytes):
        self.iv = iv
        self.ciphertext = ciphertext
        
    def to_bytes(self) -> bytes:
        iv_len = len(self.iv)
        cipher_len = len(self.ciphertext)
        return struct.pack('!II', iv_len, cipher_len) + self.iv + self.ciphertext
        
    @staticmethod
    def from_bytes(data: bytes) -> 'EncryptedMessage':
        iv_len, cipher_len = struct.unpack('!II', data[:8])
        iv = data[8:8+iv_len]
        ciphertext = data[8+iv_len:8+iv_len+cipher_len]
        return EncryptedMessage(iv, ciphertext)