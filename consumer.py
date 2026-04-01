import pika
import sys
import os
import time


class RabbitMqConsumer:
    def __init__(self, name_queue, callback):
        self.__host = "localhost"
        self.__port = 5672
        self.__username = "guest"
        self.__password = "guest"
        self.__queue = name_queue
        self.__routing_key = name_queue
        self.__callback = callback
        self.__channel = self.__create_channel()

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host=self.__host,
            port=self.__port,
            credentials=pika.PlainCredentials(
                username=self.__username,
                password=self.__password
            )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()

        # channel.queue_bind(exchange=exchange_name,
        #                 queue=queue_name,
        #                 routing_key='black')

        channel.queue_declare(
            queue=self.__queue,
            durable=True
        )

        channel.basic_consume(
            queue=self.__queue,
            auto_ack=False,
            on_message_callback=self.__callback
        )

        return channel
    
    def start(self):
        # print(f'Listen RabbitMQ on Port 5672')
        print(' [*] Waiting for messages. To exit press CTRL+C')
        self.__channel.start_consuming()



def minha_callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    time.sleep(body.count(b'.'))
    print(" [x] Done")
    ch.basic_ack(delivery_tag = method.delivery_tag)
    
def main():
    
    escolha = int(input('Qual queue? : 1  /  2'))
    if escolha == 1:
        rabitmq_consumer = RabbitMqConsumer("outra_queue", minha_callback)
    if escolha ==2:
        rabitmq_consumer = RabbitMqConsumer("current_queue", minha_callback)

    rabitmq_consumer.start()


if __name__ == '__main__':
    try:
        main()
    
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


# channel.exchange_declare(exchange='direct_logs',
#                          exchange_type='direct')

# channel.basic_publish(exchange='direct_logs',
#                       routing_key=severity,
#                       body=message)

# channel.queue_bind(exchange=exchange_name,
#                    queue=queue_name,
#                    routing_key='black')