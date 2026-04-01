from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA


# Envio
message = b'To be signed'
key = RSA.import_key(open('private_key.der').read())
h = SHA256.new(message)
signature = pkcs1_15.new(key).sign(h)

print('h: ', h )
print(h.hexdigest())



# Recebimento

key = RSA.import_key(open('public_key.der').read())
h = SHA256.new(message)
try:
    pkcs1_15.new(key).verify(h, signature)
    print("The signature is valid.")
except (ValueError, TypeError):
   print("The signature is not valid.")

