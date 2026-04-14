import os
import json
import base64
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

KEY_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'keys')

def ensure_key_dir():
    if not os.path.isdir(KEY_DIR):
        os.makedirs(KEY_DIR, exist_ok=True)

def generate_keys(service_name):
    ensure_key_dir()
    private_path = os.path.join(KEY_DIR, f"{service_name}_private.der")
    public_path = os.path.join(KEY_DIR, f"{service_name}_public.der")

    if not os.path.isfile(private_path):
        key = RSA.generate(2048)
        with open(private_path, 'wb') as f:
            f.write(key.export_key('DER'))
        with open(public_path, 'wb') as f:
            f.write(key.publickey().export_key('DER'))
        print(f"Chaves geradas para {service_name}")

def load_private_key(service_name):
    private_path = os.path.join(KEY_DIR, f"{service_name}_private.der")
    if not os.path.isfile(private_path):
        generate_keys(service_name)
    with open(private_path, 'rb') as f:
        return RSA.import_key(f.read())

def load_public_key(service_name):
    public_path = os.path.join(KEY_DIR, f"{service_name}_public.der")
    if not os.path.isfile(public_path):
        generate_keys(service_name)
    with open(public_path, 'rb') as f:
        return RSA.import_key(f.read())

def sign_message(message, service_name):
    key = load_private_key(service_name)
    h = SHA256.new(message)
    signature = pkcs1_15.new(key).sign(h)
    return base64.b64encode(signature).decode('utf-8')

def verify_signature(message, signature_b64, service_name):
    key = load_public_key(service_name)
    h = SHA256.new(message)
    signature = base64.b64decode(signature_b64)
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False

# Exemplo de uso (pode ser removido ou comentado)
if __name__ == "__main__":
    message = b'To be signed'
    service = 'test'
    generate_keys(service)
    sig = sign_message(message, service)
    print("Assinatura:", sig)
    valid = verify_signature(message, sig, service)
    print("Válida:", valid)

