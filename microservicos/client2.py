import sys
import os
import pika
import time 
import json

from server.server import connect, publish
import random

def iniciar_bindings():
    channel.exchange_declare(
        exchange='promocoes',
        exchange_type='direct'
    )
    
    channel.queue_declare(
        queue='fila_client2',
        durable=True
    )

    channel.queue_bind(
        exchange='promocoes',
        queue='fila_client2',
        routing_key='promocao.destaque'
    )

    channel.queue_bind(
        exchange='promocoes',
        queue='fila_client2',
        routing_key='promocao.categoria2'
    )
def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode())
    print('Nova promoção publicada: ', mensagem)



def consume(channel, queue):
    channel.basic_consume(
        queue=queue,
        auto_ack=True,
        on_message_callback=minha_callback
    )

    print("[*] Consumindo promocao.destaque / promocao.client2 ")
    channel.start_consuming()

channel = connect()
iniciar_bindings()

consume(channel, 'fila_client2')