import json
import os
import random
import socket
import threading
import random
import json

# diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# caminho_json = os.path.join(diretorio_atual, 'promocoes.json')


# with open(caminho_json, 'r', encoding='utf-8') as f:
#     dados = json.load(f)

# print(dados)


HOST = '0.0.0.0'  # aceita conexões externas
PORT = 5000

def carregar_clientes():
    with open('clientes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
        

def gerar_id():
    return ''.join(str(random.randint(0, 9)) for _ in range(8))

def manuzear_arquivo(caminho_json, type, dados):
    if type == 'r':
        with open(caminho_json, type, encoding= 'utf-8') as f:
            dados = json.load(f)
        return dados
    if type == 'w':
        with open(caminho_json, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

def handle_client(conn, addr, current_client):
    print(f"[NOVA CONEXÃO] {addr} conectado")

    # cliente = random.choice(clientes)
    conn.send(f"Você é: clientes \n".encode())

    try:
        conn.send("Conectado ao servidor!\n".encode())
    
        while True:
            menu = """\nEscolha uma opção:
                1 - Cadastrar Promoção
                2 - Votar
                3 - Notificações
                0 - Sair
                > """
            
            conn.send(menu.encode())

            data = conn.recv(1024)
            if not data:
                break
            
            resp = data.decode().strip()
            print(f"[{addr}] -> {resp}")

            if resp == '1':
                conn.send("Nome: ".encode())
                nome = conn.recv(1024).decode().strip()

                conn.send("Preço: ".encode())
                preco = conn.recv(1024).decode().strip()

                categorias_validas = ["eletronicos", "roupas", "comida", "livros", "viagem"]

                lista_cat = "\n".join([f"{i+1} - {c}" for i, c in enumerate(categorias_validas)])
                conn.send(f"Categorias:\n{lista_cat}\n> ".encode())

                categoria_input = conn.send('Escolha o número da categoria: \n'.encode())
                categoria_index = int(conn.recv(1024).decode().strip()) - 1
                categoria = categoria_input[categoria_index]

                novo_item = {
                    "nome": nome,
                    "preco": preco,
                    "id": gerar_id(),
                    "categoria": categoria
                }

                if not os.path.exists('promocoes.json'):
                    dados = []
                else:
                    dados = manuzear_arquivo('promocoes.json', 'r', '')

                dados[categoria].append(novo_item)

                manuzear_arquivo('promocoes.json', 'w', dados)

            if resp == '2':
                dados = manuzear_arquivo('promocoes.json', 'r', '')
                conn.send(f"{json.dumps(dados, indent=2)}\n".encode())

                conn.send("Digite o ID do produto:\n> ".encode())
                id_produto = conn.recv(1024).decode().strip()

                votos = manuzear_arquivo('votos.json', 'r', '')
                if not votos:
                    votos = []

                encontrado = False

                for item in votos:
                    if item["id"] == id_produto:
                        item["votos"] += 1
                        encontrado = True
                        break

                if not encontrado:
                    votos.append({"id": id_produto, "votos": 1})

                manuzear_arquivo('votos.json', 'w', votos)

                conn.send("Voto registrado!\n".encode())

            
            if resp == '3':
                dados = manuzear_arquivo('promocoes.json', 'r', '')
                for interesse in current_client["interesse"]:
                    print(f"\nInteresse: {interesse}")
                    conn.send(f"{interesse}\n".encode())
                    if interesse in dados:
                        for produto in dados[interesse]:
                            print(f"- {produto['nome']} | R$ {produto['preco']}")
                            conn.send(f"- {produto['nome']} | R$ {produto['preco']}\n".encode())
                    conn.send("\n".encode())


            if resp == '0':
                conn.send('exit'.encode())
                break
    
    except Exception as e:
        print(f"[ERRO] {addr}: {e}")

def start_server():
     # print('clientes: ', clientes[0])
    clientes = carregar_clientes()
    current_client = clientes[random.randint(0, 4)]

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind(('localhost', 5000))
        server.listen(5)
        print('Servidor iniciado')
    except:
        return print('\nNão foi possível iniciar o servidor!\n')

    print(f"[SERVIDOR RODANDO] {HOST}:{PORT}")


    while True:
        conn, addr = server.accept()
 
        thread = threading.Thread(target=handle_client, args=(conn, addr, current_client))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}\n\n")

start_server()