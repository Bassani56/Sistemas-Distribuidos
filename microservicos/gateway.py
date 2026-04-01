import sys
import os

sys.path.append(os.path.abspath(".."))


from server.server import connect, publish, consume
import random


def iniciar_bindings():
    channel.exchange_declare(exchange='promocoes',
        exchange_type='direct')
    
    list_routingKeys = ['promocao.categoria1', 'promocao.categoria2', 'promocao.destaque', 'promocao.publicada', 'promocao.recebida', 'promocao.voto']

    channel.queue_declare(
            queue='queue_gateway',
            durable=True
        )

    for key in list_routingKeys:
        channel.queue_bind(exchange='promocoes',
                   queue='queue_gateway',
                   routing_key=key)

channel = connect()
iniciar_bindings()

def gerar_id():
    return ''.join(str(random.randint(0, 9)) for _ in range(8))

def cadastrar_promocao(nome, categoria, preco):
    id = gerar_id()

    promocao = {
        "id": id,
        "nome": nome,
        "categoria": categoria,
        "preco": preco
    }

    publish(channel, "promocao.recebida", promocao)
    print("[Gateway] Promoção enviada")

def listar_promocoes(channel, queue, routingKey, callback):
    consume(channel, queue, routingKey, callback)

def votar(channel, queue, routingKey, callback):
    consume(channel, queue, routingKey, callback)


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

        cadastrar_promocao(nome, categoria, preco)

    if resp == '2':
        consume(channel, 'queue_gateway', 'promocao.recebida')

    if resp == '3':
         consume(channel, 'queue_gateway', 'promocao.recebida')

       