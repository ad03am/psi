from src.crypto import Crypto

with open("key.bin", 'rb') as f:
    key = f.read()

data = input("Enter data: ")
data = bytes.fromhex(data)

iv = data[:16]
ciphertext = data[16:]

crypto = Crypto(key)

decrypted_message = crypto.decrypt(ciphertext, iv)

print(decrypted_message.decode('utf-8'))
