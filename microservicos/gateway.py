import sys
import os
import json

import threading

sys.path.append(os.path.abspath(".."))

from server.server import connect, publish, verify_signature
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(BASE_DIR, '..', 'votos.json')
caminho_promocoes = os.path.join(BASE_DIR, '..', 'promocoes.json') 


def consume(channel, queue, routingKey):
    channel.queue_declare(
        queue=queue,
        durable=True
    )

    channel.queue_bind(
        exchange='promocoes',
        queue=queue,
        routing_key=routingKey
    )

    channel.basic_consume(
        queue=queue,
        auto_ack=True,
        on_message_callback = minha_callback
    )

    print(f"[*] Consumindo {routingKey}")
    channel.start_consuming()

def iniciar_bindings(channel):
    channel.exchange_declare(exchange='promocoes',
        exchange_type='direct')
    
    key = 'promocao.publicada'

    channel.queue_declare(
        queue='fila_gateway',
        durable=True
    )
 
    channel.queue_bind(exchange='promocoes',
        queue='fila_gateway',
        routing_key=key)

def gerar_id():
    return ''.join(str(random.randint(0, 9)) for _ in range(8))

def cadastrar_promocao(channel, nome, categoria, preco):
    id = gerar_id()

    promocao = {
        "id": id,
        "nome": nome,
        "categoria": categoria,
        "preco": preco
    }

    publish(channel, "promocao.recebida", promocao, service_name='gateway') #MS_promocao
    print("[Gateway] Promoção enviada ao promocao ")

def listar_promocoes():
    with open(caminho_promocoes, 'r', encoding='utf-8') as f:
        promocoes = json.load(f)

        print("\n=== RANKING ===")
        for categoria, lista in promocoes.items():
            print(categoria)

            for produto in lista:
                print('    ', produto)
 

def votar(channel, routingKey, message):
    print('voto enviado ao ranking')
    publish(channel, routingKey, message, service_name='gateway')  #MS_ranking
    
def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode()) 
    print(mensagem)

    payload = mensagem.get("Payload")

    if not verify_signature(mensagem):
        print("Assinatura inválida. Mensagem descartada.")
        return
    
    with open(caminho_promocoes, 'r', encoding='utf-8') as f:
        promocoes = json.load(f)

    categoria = payload[1]['categoria']

    if categoria in promocoes:
        if not isinstance(promocoes[categoria], list):
            promocoes[categoria] = [promocoes[categoria]]
        promocoes[categoria].append(payload[1])
    else:
        promocoes[categoria] = [payload[1]]

    with open(caminho_promocoes, 'w', encoding='utf-8') as f:
        json.dump(promocoes, f, indent=4, ensure_ascii=False)

    print("Promoção salva!")


def main():
    channel = connect()
    iniciar_bindings(channel)

    t = threading.Thread(
        target=consume,
        args=(channel, 'fila_gateway', 'promocao.publicada'),
        daemon=True
    )

    t.start()

    while True:
        menu = """\nEscolha uma opção:
                    1 - Cadastrar Promoção
                    2 - Votar
                    3 - Listar Promoções
                    0 - Sair
                    > """
        print(menu)
        resp = input('')
        
        if resp == '1':
            nome = input('nome: ')
            categoria = input('categoria: ')
            preco = input('preco: ')

            cadastrar_promocao(channel, nome, categoria, preco)

        if resp == '2':
            # with open(caminho, 'r', encoding='utf-8') as f:
            #     dados = json.load(f)

            listar_promocoes()

            # ordenar do maior para o menor
            # dados.sort(key=lambda x: x['score'], reverse=True)
            # print('dados: ', dados)

            id = input('id: ')
            categoria = input('categoria: ')
            vt = input("Vote: +1 positivo | -1 negativo: ")
            if vt == '1':
                votar(channel, 'promocao.voto', {"voto": 1, "ident": id, "categoria": categoria})
            else:
                votar(channel, 'promocao.voto', {"voto": -1, "ident": id})

        if resp == '3':
            listar_promocoes()

main()