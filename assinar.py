from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

message = b'To be signed'
key = RSA.import_key(open('./keys/gateway_private.der', 'rb').read())
h = SHA256.new(message)
signature = pkcs1_15.new(key).sign(h) # Cria um objeto de assinatura usando a chave privada  .sign(h) Assina o hash da mensagem

#envia 'signature'

#recebe 'signature'
key2 = RSA.import_key(open('./keys/gateway_public.der', 'rb').read())
h = SHA256.new(message)
try:
    pkcs1_15.new(key2).verify(h, signature)

    print("The signature is valid.")
    print('assinatura: ', signature)
except (ValueError, TypeError):
   print("The signature is not valid.")
   print('assinatura: ', signature)

