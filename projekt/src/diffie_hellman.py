import random

class diffie_hellman:
    def __init__(self):
        self.primes = [5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        self.generators = [2, 3]
        
    def generate_parameters(self):
        self.p = random.choice(self.primes)
        self.g = random.choice(self.generators)
        self.private_key = random.randint(2, self.p - 1)
        self.public_key = pow(self.g, self.private_key, self.p)
        return self.g, self.p, self.public_key
    
    def generate_from_parameters(self, p: int, g: int):
        self.p = p
        self.g = g
        self.private_key = random.randint(2, self.p - 1)
        self.public_key = pow(self.g, self.private_key, self.p)
        return self.public_key
    
    def compute_shared_secret(self, other_public_key: int) -> int:
        return pow(other_public_key, self.private_key, self.p)

def generate_session_key(shared_secret: int) -> bytes:
    key = shared_secret.to_bytes(32, byteorder='big')
    return key
