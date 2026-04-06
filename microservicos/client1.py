import sys
import os
import json

sys.path.append(os.path.abspath(".."))

import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_clients = os.path.join(BASE_DIR, '..', 'clientes.json') 

def carregar_clientes():
    with open(caminho_clients, 'r', encoding='utf-8') as f:
        return json.load(f)

clientes = carregar_clientes()
current_client = clientes[random.randint(0, 4)]
    