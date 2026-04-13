import pika
import json

class RabbitmpPublisher:
    def __init__(self):
        self.__host = "localhost",
        self.__port = 5672,
        self.__username = "guest",
        self.__password = "guest",
        self.__exchange = "data_exchange",
        self.__routine_key = "",
        self.__channel = self.__create_channel

    def __create_channel(self):
        connection_parameters = pika.ConnectionParameters(
            host= self.__host,
            port= self.__port,
            credentials=pika.PlainCredentials(
                username= self.__username,
                password= self.__password
            )
        )

        channel = pika.BlockingConnection(connection_parameters).channel()
        return channel
        
    def send_message(self, body):
        self.__channel.basic_publish(
            exchange= self.__exchange,
            routing_key=self.__routine_key,
            body= json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2
            )
        )

rabbitmq_publisher = RabbitmpPublisher()
rabbitmq_publisher.send_message({"Message": "Olá, Mundo!"})


