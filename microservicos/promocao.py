import sys
import os
import pika
import time 
import json

from server.server import connect, publish
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_promocoes = os.path.join(BASE_DIR, '..', 'promocoes.json')


def connect():
    connection_parameters = pika.ConnectionParameters(
        host="localhost",
        port=5672,
        credentials=pika.PlainCredentials(
            username="guest",
            password="guest"
        )
    )

    channel = pika.BlockingConnection(connection_parameters).channel()

    return channel

def iniciar_bindings():
    channel.exchange_declare(exchange='promocoes',
        exchange_type='direct')
    
    key = 'promocao.recebida'

    channel.queue_declare(
        queue='fila_promocao',
        durable=True
    )
 
    channel.queue_bind(exchange='promocoes',
        queue='fila_promocao',
        routing_key=key)

def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode())  # 🔥 converte bytes → dict
    print(mensagem)

    with open(caminho_promocoes, 'r', encoding='utf-8') as f:
        promocoes = json.load(f)

    categoria = mensagem['categoria']

    # Se já existe a categoria
    if categoria in promocoes:
        # 🔥 garante que seja lista
        if not isinstance(promocoes[categoria], list):
            promocoes[categoria] = [promocoes[categoria]]

        promocoes[categoria].append(mensagem)

    else:
        # cria nova categoria como lista
        promocoes[categoria] = [mensagem]

    with open(caminho_promocoes, 'w', encoding='utf-8') as f:
        json.dump(promocoes, f, indent=4, ensure_ascii=False)

    print("Promoção salva!")

    publish(channel, 'promocao.publicada', mensagem)
    

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
        auto_ack=False,
        on_message_callback = minha_callback
    )

    print(f"[*] Consumindo {routingKey}")
    channel.start_consuming()

channel = connect()
iniciar_bindings()

consume(channel, 'fila_promocao', 'promocao.recebida')

