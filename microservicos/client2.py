import sys
import os
import pika
import time 
import json

from server.server import connect, publish


def iniciar_bindings():
    channel.exchange_declare(exchange='promocoes',
        exchange_type='direct')
    
    key = 'promocao.voto'
    channel.queue_declare(
        queue='fila_ranking',
        durable=True
    )
 
    channel.queue_bind(exchange='promocoes',
        queue='fila_ranking',
        routing_key=key)

def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode())
    print('Nova promoção publicada: ', mensagem)


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

consume(channel, 'fila_cliente_b', 'promocao.categoria2')
consume(channel, 'fila_cliente_b', 'promocao_destaque')
