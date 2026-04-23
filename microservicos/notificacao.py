import sys
import os
import pika
import time 
import json

from server.server import connect, publish, verify_signature
import random


def iniciar_bindings():
    channel.exchange_declare(
        exchange='promocoes',
        exchange_type='direct'
    )
    
    channel.queue_declare(
        queue='fila_notificacao',
        durable=True
    )

    channel.queue_bind(
        exchange='promocoes',
        queue='fila_notificacao',
        routing_key='promocao.publicada'
    )

    channel.queue_bind(
        exchange='promocoes',
        queue='fila_notificacao',
        routing_key='promocao.destaque'
    )

def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode()) 
    payload = mensagem.get("Payload")

    if payload[0] == 'destaque':
        return

    if not verify_signature(mensagem):
        print(" Assinatura inválida. Mensagem descartada.")
        return
    
    if payload[0] == 'ranking':
        routing_key = 'promocao.destaque'
    
    else:
        routing_key = f'promocao.{payload[1]['categoria']}'

    publish(channel, routing_key, mensagem, service_name='notificacao')
    print('<< promocao publicada >>')
    print(mensagem)

def consume(channel, queue):
    channel.basic_consume(
        queue=queue,
        auto_ack=True,
        on_message_callback=minha_callback
    )

    print("[*] Consumindo promocao.destaque / promocao.publicada ")
    channel.start_consuming()


channel = connect()
iniciar_bindings()

consume(channel, 'fila_notificacao')