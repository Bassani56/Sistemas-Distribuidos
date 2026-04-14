import pika
import sys
import time
import json
import copy

import chave  

def sign_payload(payload, service_name):
    if service_name is None:
        return payload

    signed_payload = copy.deepcopy(payload)

    if isinstance(signed_payload, dict) and 'Signature' in signed_payload:
        signed_payload.pop('Signature')

    canonical = json.dumps(signed_payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    signature_b64 = chave.sign_message(canonical.encode('utf-8'), service_name)

    if isinstance(signed_payload, dict):
        signed_payload['Signature'] = signature_b64
    else:
        signed_payload = {
            'Payload': signed_payload,
            'Signature': signature_b64
        }

    return signed_payload

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

def publish(channel, routingKey, message, service_name=None):
    signed_message = sign_payload(message, service_name)
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
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    channel.basic_ack(delivery_tag = method.delivery_tag)

