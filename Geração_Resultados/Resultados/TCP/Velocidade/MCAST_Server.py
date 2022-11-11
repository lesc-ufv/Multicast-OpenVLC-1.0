from logging import exception
from math import ceil
from random import randint
import socket
import _thread
import pickle
import os
import hashlib
from time import sleep

HOST = '192.168.0.1'              # Endereco IP do Servidor
PORT = 5060           # Porta que o Servidor esta

ListaClientes = []

try:
    ListaClientes = pickle.load(open('Clientes.pkl', 'rb'))
except:
    ListaClientes.append([])
    ListaClientes.append([])

#print(ListaClientes)
#mcastIpGroup = "224.1.1.5"
mcastPort = "50001"
#mcastAddress = mcastIpGroup+":"+mcastPort

buffer = 1024


def RecebePedidos(ListClients, host, port):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    orig = (host, port)

    tcp.bind(orig)
    tcp.listen(1)

    while True:
        con, cliente = tcp.accept()
        acao = con.recv(1024).decode()
        if (acao == 'E'):
            #print("Recebido E!")
            _thread.start_new_thread(
                ConectaRequisicaoEntrar, tuple([con, cliente, ListClients]))
        elif (acao == 'Q'):
            _thread.start_new_thread(
                ConectaRequisicaoSair, tuple([con, cliente, ListClients]))

        #print("ListaClientes: ", ListaClientes)

    tcp.close()


def ConectaRequisicaoEntrar(con, cliente, ListClients):
    print("Conectado por", cliente)

    clientid = str(randint(1, 1024))
    jaCadastrado = False

    if (cliente[0] in ListClients[0]):
        print("Cliente já presente em lista de clientes, atribuindo mesmo ID!")
        clientid = ListClients[1][ListClients[0].index(cliente[0])]
        jaCadastrado = True
    else:
        while (clientid in ListClients[1]):
            clientid = str(randint(1, 1024))

    con.send(clientid.encode())

    if (con.recv(1024).decode() != "OK"):
        print("Erro ao receber ack de clientId!")
        con.close()
        _thread.exit()
    else:
        print("Cliente ", cliente[0], " / ", clientid, " -> OK!")
        if (not jaCadastrado):
            ListClients[0].append(cliente[0])
            ListClients[1].append(clientid)

    con.close()
    _thread.exit()


def ConectaRequisicaoSair(con, cliente, ListClients):
    print("Conectado por", cliente)

    try:
        indexIP = ListClients[0].index(cliente[0])

    except:
        print("Erro ao localizar index de cliente em lista!")
        con.send("RFail!".encode())
        con.close()
        _thread.exit()

    IpClient = ListClients[0].pop(indexIP)
    identClient = ListClients[1].pop(indexIP)

    print("O cliente", IpClient, "- ID:", identClient,
          "removido da lista de clientes. ")
    con.send("RSucess!".encode())
    #print("Lista: ",ListaClientes)
    con.close()
    _thread.exit()

def MCAST_Server_TCP(port=50001):
    archive = "message.txt"
    iteracoes = 30
    input("Pressione enter para iniciar o teste...")
    while (iteracoes>0):
        #archive = input("Entre com o nome do arquivo:")
        print("Iteracao:", abs(iteracoes-30)+1)
        try:
            tamBytes = os.path.getsize(archive)
        except:
            print("Erro! File not found.")
            continue
        print("Tamanho do arquivo:", tamBytes," -> quantidade de envios necessarios: ", ceil(tamBytes/buffer))
        f = open(archive, "rb")
        for i in ListaClientes[0]:
            sha1 = hashlib.sha1()
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dest = (i, port)
            print("Conectando a cliente", i)
            try:
                tcp.settimeout(15)
                tcp.connect(dest)
            except Exception as e:
                print(e)
                continue
            tcp.settimeout(None)
            f_bin = f.read()
            sha1.update(f_bin)
            digest = sha1.hexdigest()
            nome = archive.split('.')[0]+'_Recebido.'+archive.split('.')[1]
            print("SHA1 hash: ", digest)
            
            data = {'name': nome, 'file': f_bin, 'sha1hash': digest}
            tcp.sendall(pickle.dumps(data))
            #tcp.recv(1024)
            f.seek(0)
           
            tcp.close()
            sleep(15)
            
        f.close()
        iteracoes-=1

if __name__ == '__main__':
    
    identificadorRecPed = _thread.start_new_thread(RecebePedidos,tuple([ListaClientes,HOST,PORT]))
    print("Thread recebedora de pedidos iniciada! Identificador: ",identificadorRecPed)

    identificadorMCastServer = _thread.start_new_thread(MCAST_Server_TCP,tuple([int(mcastPort)]))
    print("Thread servidor de grupo Mcast iniciado! Identificador: ", identificadorMCastServer)

    lenInicial = 0
    while True:
        if(len(ListaClientes[0])!=lenInicial):
            pickle.dump(ListaClientes,open('Clientes.pkl','wb'))
            lenInicial = len(ListaClientes[0])
            if(len(ListaClientes[0]) > 0):
                print("Lista de clientes:")
                for i in range(len(ListaClientes[0])):
                    print("IP:", ListaClientes[0][i],"- ID: ", ListaClientes[1][i])

