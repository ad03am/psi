import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from diffie_hellman import DiffieHellman, generate_session_key

class TestDiffieHellman(unittest.TestCase):
    def test_parameter_generation(self):
        dh = DiffieHellman()
        g, p, public_key = dh.generate_parameters()
        
        self.assertIn(p, dh.primes)
        self.assertIn(g, dh.generators)
        self.assertTrue(0 < g < p)
        self.assertTrue(0 < public_key < p)

    def test_key_exchange(self):
        alice = DiffieHellman()
        g, p, A = alice.generate_parameters()
        
        bob = DiffieHellman()
        B = bob.generate_from_parameters(p, g)
        
        alice_secret = alice.compute_shared_secret(B)
        bob_secret = bob.compute_shared_secret(A)
        
        self.assertEqual(alice_secret, bob_secret)
    
    def test_session_key_generation(self):
        shared_secret = 12345
        key = generate_session_key(shared_secret)
        
        self.assertEqual(len(key), 32)
        self.assertEqual(int.from_bytes(key, byteorder='big'), shared_secret)

if __name__ == '__main__':
    unittest.main()
