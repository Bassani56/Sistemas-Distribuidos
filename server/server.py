import pika

import json
import copy
import chave  

from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import base64

def verify_signature(message):
    signature = message.get("Signature")
    payload = message.get("Payload")

    if not signature or not payload:
        return False

    canonical = json.dumps(payload[1], sort_keys=True, separators=(',', ':'), ensure_ascii=False)

    service_name = payload[0].split('.')[0]  # ex: promocao.recebida → promocao

    key = RSA.import_key(open(f'./keys/{service_name}_public.der', 'rb').read())

    canonical = json.dumps(
        payload[1],
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
    ).encode('utf-8')

    h = SHA256.new(canonical)

    signature_bytes = base64.b64decode(signature)

    try:
        pkcs1_15.new(key).verify(h, signature_bytes)
        return True
    except (ValueError, TypeError):
        return False

def sign_payload(message, service_name):
    if service_name is None:
        return message

    message_copy = copy.deepcopy(message) #copia profunda

    key = RSA.import_key(open(f'./keys/{service_name}_private.der', 'rb').read())

    if service_name == 'notificacao':
        message_copy = message_copy[1]

    canonical = json.dumps(
        message_copy,
            sort_keys=True,
            separators=(',', ':'),
            ensure_ascii=False
    ).encode('utf-8')

    h = SHA256.new(canonical)

    signature = pkcs1_15.new(key).sign(h) # Cria um objeto de assinatura usando a chave privada  .sign(h) Assina o hash da mensagem

    signature = pkcs1_15.new(key).sign(h)
    signature_b64 = base64.b64encode(signature).decode()

    message_copy = {
        'Payload': [service_name, message_copy],
        'Signature': signature_b64
    }

    return message_copy

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

def publish(channel, routingKey, message, service_name):
    # print('\n', routingKey, service_name, '\n', 'SERVER: ', message, '\n \n')

    if service_name != 'notificacao':
        signed_message = sign_payload(message, service_name)
        # print('MENSAGEM   ASSINADA')

    else:
       signed_message = message
       signed_message['Payload'][0] = 'destaque'
    #    print('N  Ã   O   ASSINADA')
       
    channel.basic_publish(
        exchange='promocoes',
        routing_key=routingKey,
        body=json.dumps(signed_message),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )
    )
    
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

def minha_callback(channel, method, properties, body):
    print(f" [x] Received {body.decode()}")
    print(" [x] Done")
    channel.basic_ack(delivery_tag = method.delivery_tag)

