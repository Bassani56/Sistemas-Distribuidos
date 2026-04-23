import sys
import os
import pika
import time 
import json
import threading

from server.server import connect, publish
import random

def iniciar_bindings(channel):
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
        routing_key='promocao.calcados'
    )
    
def minha_callback(channel, method, properties, body):
    mensagem = json.loads(body.decode()) 
    # print(mensagem)

    payload = mensagem.get("Payload")
    signature = mensagem.get("Signature")

    if payload[0] == 'ranking':
        print('<< promocao destaque >>')
        print('id: ', payload[1]['ident'])
        print('categoria: ', payload[1]['categoria'])

    else:
        print("<< promocao publicada >>")
        print(payload[1])

def consume(channel, queue):
    channel.basic_consume(
        queue=queue,
        auto_ack=True,
        on_message_callback=minha_callback
    )

    # print("[*] Consumindo promocao.destaque / promocao.calcados ")
    channel.start_consuming()


def main():
    channel = connect()
    iniciar_bindings(channel)

    t = threading.Thread(
        target=consume,
        args=(channel, 'fila_client2'),
        daemon=True
    )

    t.start()

    while True:
        print("\nDigite uma categoria para se inscrever (ou ENTER para ignorar):")
        resp = input("> ").strip()

        if resp:
            routing_key = f'promocao.{resp}'

            channel.queue_bind(
                exchange='promocoes',
                queue='fila_client2',
                routing_key=routing_key
            )

            print(f"[+] Inscrito em {routing_key}")

main()