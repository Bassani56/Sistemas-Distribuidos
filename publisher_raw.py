import pika
import sys

connection_parameters = pika.ConnectionParameters(
    host="localhost",
    port=5672,
    credentials=pika.PlainCredentials(
        username="guest",
        password="guest"
    )
)

channel = pika.BlockingConnection(connection_parameters).channel()

while True:
    try:
        message = input("> ")
        escolha = int(input('Para quem? : 1  /  2'))
        if escolha == 1:
            queue = "outra_queue"
        if escolha == 2:
            queue = "current_queue"

        if not message.strip():
            continue  

        channel.exchange_declare(exchange='direct_logs',
                         exchange_type='direct',
                         durable=True)

        channel.queue_bind(exchange="direct_logs",
           queue="my_queue",
           routing_key='minha_chave')

        channel.basic_publish(
                      exchange='direct_logs',
                      routing_key="minha_chave",
                      body=message,
                      properties=pika.BasicProperties(
                        delivery_mode= pika.DeliveryMode.Persistent
                      ))



        # channel.basic_publish(
        #     exchange="",
        #     routing_key= queue,
        #     body=message,
        #     properties=pika.BasicProperties(
        #         delivery_mode= pika.DeliveryMode.Persistent
        #     )
        # )

        print(f"[x] Enviado: {message}")

    except KeyboardInterrupt:
        print("\nSaindo...")
        break

connection_parameters.close()