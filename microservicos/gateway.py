import sys
import os
import json

sys.path.append(os.path.abspath(".."))

from server.server import connect, publish
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(BASE_DIR, '..', 'votos.json')
caminho_promocoes = os.path.join(BASE_DIR, '..', 'promocoes.json') 

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

    publish(channel, "promocao.recebida", promocao) #MS_promocao
    print("[Gateway] Promoção enviada")

def listar_promocoes(current_client):
    with open(caminho_promocoes, 'r', encoding='utf-8') as f:
        promocoes = json.load(f)

        # print("\n=== RANKING ===")
        # for categoria, lista in promocoes.items():
        #     print(categoria)

        #     for produto in lista:
        #         print('    ', produto)

        dados = promocoes
        for interesse in current_client["interesse"]:
            print(f"\nInteresse: {interesse}")

            if interesse in dados:
                for produto in dados[interesse]:
                    print(f"- {produto['nome']} | R$ {produto['preco']}")
                        

def votar(channel, routingKey, message):
   publish(channel, routingKey, message)  #MS_ranking


def main():
    channel = connect()
    iniciar_bindings(channel)

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
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)

            listar_promocoes()

        # ordenar do maior para o menor
            dados.sort(key=lambda x: x['score'], reverse=True)

            id = input('id: ')
            vt = input('+1 ?  (1) \n -1 ? (-1) \n > ')
            if vt == '1':
                votar(channel, 'promocao.voto', {"voto": 1, "ident": id})
            else:
                votar(channel, 'promocao.voto', {"voto": -1, "ident": id})

        if resp == '3':
            listar_promocoes(current_client)

main()