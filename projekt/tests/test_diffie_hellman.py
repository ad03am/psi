import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from diffie_hellman import diffie_hellman

class test_diffie_hellman(unittest.TestCase):
    def test_parameter_generation(self):
        dh = diffie_hellman()
        g, p, public_key = dh.generate_parameters()
        
        self.assertIn(p, dh.primes)
        self.assertIn(g, dh.generators)
        self.assertTrue(0 < g < p)
        self.assertTrue(0 < public_key < p)

    def test_key_exchange(self):
        alice = diffie_hellman()
        g, p, A = alice.generate_parameters()
        
        bob = diffie_hellman()
        B = bob.generate_from_parameters(p, g)
        
        alice_secret = alice.compute_shared_secret(B)
        bob_secret = bob.compute_shared_secret(A)
        
        self.assertEqual(alice_secret, bob_secret)

if __name__ == '__main__':
    unittest.main()
