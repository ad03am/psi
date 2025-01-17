from src.crypto import Crypto

with open("key.bin", 'rb') as f:
    key = f.read()

data = 'aafb8bef198c08b6c2a4420c90efd04757e4ab1fd3d49fcaacb87e1ae9b022f9707d172d49e1161f99e2e77cccc12bab723047dc'
data = bytes.fromhex(data)

iv = data[:16]
ciphertext = data[16:]

crypto = Crypto(key)

decrypted_message = crypto.decrypt(ciphertext, iv)

print(decrypted_message.decode('utf-8'))
