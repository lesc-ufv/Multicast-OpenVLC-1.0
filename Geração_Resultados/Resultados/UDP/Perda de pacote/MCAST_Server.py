from random import randint
import socket
import _thread
from time import sleep
import pickle

HOST = '192.168.0.1'              # Endereco IP do Servidor
PORT = 5060           # Porta que o Servidor esta

ListaClientes =[]

try:
    ListaClientes = pickle.load(open('Clientes.pkl','rb'))
except:
    ListaClientes.append([])
    ListaClientes.append([])

#print(ListaClientes)
mcastIpGroup = "224.1.1.5"
mcastPort = "50001"
mcastAddress = mcastIpGroup+":"+mcastPort

quantMensagens = 30

def RecebePedidos(ListClients,mcAddress,host,port):
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    orig = (host,port)

    tcp.bind(orig)
    tcp.listen(1)


    while True:
        con, cliente = tcp.accept()
        acao = con.recv(1024).decode()
        if(acao == 'E'):
            #print("Recebido E!")
            _thread.start_new_thread(ConectaRequisicaoEntrar, tuple([con, cliente, ListClients, mcAddress]))
        elif(acao == 'Q'):
            _thread.start_new_thread(ConectaRequisicaoSair, tuple([con, cliente, ListClients]))

        #print("ListaClientes: ", ListaClientes)
        

    tcp.close()


def ConectaRequisicaoEntrar(con, cliente,ListClients,mcAddress):
    print("Conectado por", cliente)

    clientid = str(randint(1, 1024))
    jaCadastrado = False
    
    if(cliente[0] in ListClients[0]):
        print("Cliente já presente em lista de clientes, atribuindo mesmo ID!")
        clientid = ListClients[1][ListClients[0].index(cliente[0])]
        jaCadastrado = True
    else:
        while(clientid in ListClients[1]):
            clientid = str(randint(1,1024))
    
    con.send(clientid.encode())

    if(con.recv(1024).decode() != "OK"):
        print("Erro ao receber ack de clientId!")
        con.close()
        _thread.exit()

    con.send(mcAddress.encode())

    while True:
        msg = con.recv(1024).decode()
        if (msg == "OK"):
            print("Cliente ",cliente[0]," / ",clientid," -> ", msg,"!")
            if(not jaCadastrado):
                ListClients[0].append(cliente[0])
                ListClients[1].append(clientid)
            break
        else:
            print("Ocorreu um erro ao atribuir MCAST com o cliente ", cliente,"!")
            break

    con.close()
    _thread.exit()

def ConectaRequisicaoSair(con,cliente,ListClients):
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


    print("O cliente",IpClient, "- ID:", identClient, "removido da lista de clientes. ")
    con.send("RSucess!".encode())
    #print("Lista: ",ListaClientes)
    con.close()
    _thread.exit()

def MCAST_Server(hostip, mcgrpip="224.1.1.5", mcport=50001):
    # This creates a UDP socket
    sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                           proto=socket.IPPROTO_UDP, fileno=None)

    mcgrp = (mcgrpip, mcport)


    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

    sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                      socket.inet_aton(hostip))
    while(True):
        EnviaMensagensTeste(sender, mcgrp, 0.09375, quantMensagens)

    sender.close()


def EnviaMensagensTeste(socketSender, mcgrp, sleepTime, quant=30):
    prefixo = 'Realizando teste de recebimento! Mensagem numero: '
    input("Pressione enter para comecar a enviar.")
    for j in range(1, quant + 1):
        for i in range(1,quant + 1):
            msg = prefixo + str(i)
            sleep(sleepTime)
            print("Enviando mensagem: ", msg)
            socketSender.sendto(msg.encode(), mcgrp)
        input("Pressione enter para comecar a proxima iteracao.")

if __name__ == '__main__':
    
    identificadorRecPed = _thread.start_new_thread(RecebePedidos,tuple([ListaClientes,mcastAddress,HOST,PORT]))
    print("Thread recebedora de pedidos iniciada! Identificador: ",identificadorRecPed)

    identificadorMCastServer = _thread.start_new_thread(MCAST_Server,tuple([HOST,mcastIpGroup,int(mcastPort)]))
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

