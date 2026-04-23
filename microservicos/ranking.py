import sys
import os
import pika
import time 
import json

from server.server import connect, publish, verify_signature
import random

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
caminho_promocoes = os.path.join(BASE_DIR, '..', 'promocoes.json')
caminho_votos = os.path.join(BASE_DIR, '..', 'votos.json')

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
    print(mensagem)

    payload = mensagem.get("Payload")

    voto = payload[1]['voto']
    ident = payload[1]['ident']
    categoria = payload[1]['categoria']

    print(f"Recebido voto {voto} para ID {ident}")

    with open(caminho_votos, 'r', encoding='utf-8') as f:
        votos_lista = json.load(f)

    encontrou = False
    item_destaque = False

    for item in votos_lista:
        if item['id'] == ident:
            if voto > 0:
                item['voto_positivo'] += 1
                item['score'] = item['voto_positivo'] - item['voto_negativo']

                encontrou = True
            else:
                item['voto_negativo'] += 1
                item['score'] = item['voto_positivo'] - item['voto_negativo']

                encontrou = True

            if item['score'] > 5:
                item_destaque = True

            break

    if not encontrou:
        if voto > 0:
            votos_lista.append({
                "id": ident,
                "voto_positivo": 1,
                "voto_negativo": 0,
                "score": 1,
                "categoria": categoria
            })

        else:
            votos_lista.append({
                "id": ident,
                "voto_positivo": 0,
                "voto_negativo": 1,
                "score": -1,
                "categoria": categoria
            })

    with open(caminho_votos, 'w', encoding='utf-8') as f:
        json.dump(votos_lista, f, indent=4, ensure_ascii=False)

    print("Voto atualizado!")

    if item_destaque: #se o item tem score maior que 5, vira destaque
        publish(channel, 'promocao.destaque', {"ident": ident, "categoria": categoria}, service_name='ranking')
        print('enviou ao notificacao')

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

channel = connect()
iniciar_bindings()

consume(channel, 'fila_ranking', 'promocao.voto')

