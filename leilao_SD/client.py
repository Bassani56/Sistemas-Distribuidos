import queue


class Leilao:
    def __init__(self, ID, description, data, start_time, end_time):
        self.ID = ID
        self.description = description
        self.data = data
        self.start_time = start_time
        self.end_time = end_time
    

class Client:
    def __init__(self, nome, leilao):
        self.leilao = leilao
        self.name = nome


class Publisher:
    def __init__(self):
        pass




leilao = Leilao(2, 'Leilão de teste', '13/08/2026', 9, 14)


client1 = Client("Daniel", leilao)
client2 = Client("Rafael", leilao)
client3 = Client("Gabriel", leilao)



print(client1.name, ': ', client1.leilao.description)



