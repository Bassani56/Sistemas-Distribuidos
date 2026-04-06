import sys
import os
import pika
import time 
import json

from server.server import connect, publish
import random


def iniciar_bindings():
    channel.exchange_declare(exchange='promocoes',
        exchange_type='direct')
    
    key = 'promocao.destaque'
    channel.queue_declare(
        queue='fila_notificacao',
        durable=True
    )
 
    channel.queue_bind(exchange='promocoes',
        queue='fila_notificacao',
        routing_key=key)

def minha_callback(channel, method, properties, body):
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    channel.basic_ack(delivery_tag = method.delivery_tag)

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

consume(channel, 'fila_notificacao', 'promocao.destaque')

