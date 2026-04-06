import pika
import sys
import time 
import json


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

def publish(channel, routingKey,  message):
    channel.basic_publish(
        exchange='promocoes',
        routing_key=routingKey,
        body=json.dumps(message),
        properties=pika.BasicProperties(
          delivery_mode= pika.DeliveryMode.Persistent
    ))
    

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
    
