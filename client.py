import threading
import socket
import hashlib
import time
import os
from threading import Thread

def sendMessages(client, username, stop_event):
    while not stop_event.is_set():
        try:
            msg = input('\n')
            if msg == '0':
                client.send(f'EXIT:<{username}> saiu do chat'.encode())
                stop_event.set()
                break

            else:
                client.send(msg.encode())
                
        except Exception as e:
            print('Erro: ', e)
            stop_event.set()
            break

def receiveMessages(client, stop_event):
    while not stop_event.is_set():
        try:
            data = client.recv(1024)

            if not data:
                break  
            
            print(data.decode())

        except Exception as e:
            print('Erro: ', e)
            stop_event.set()
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(('localhost', 5000))
    except:
        return print('\nNão foi possível se conectar ao servidor!\n')
    
    print('\nConectado\n')

    username = input('Usuário> ')

    stop_event = threading.Event()

    recv_thread = threading.Thread(target=receiveMessages, args=(client, stop_event))
    recv_thread.start()

    send_thread = threading.Thread(target=sendMessages, args=[client, username, stop_event])
    send_thread.start()

main()