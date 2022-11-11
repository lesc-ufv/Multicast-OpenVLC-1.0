from email import iterators
import socket
import sys
import struct
import pickle
import time


HOST = '192.168.0.1'     # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta

McastAddress = ""
identifier = ""

quantMensagens = 30
quantIterac = 30

try:
    MCastServer = pickle.load(open('MCastServer.pkl', 'rb'))
    McastAddress = MCastServer[0]
    identifier = MCastServer[1]
    print("Identificador Recuperado: ", identifier)
    (mcastGpAddress, mcastPort) = McastAddress.split(":")
    print("Endereco MCAST Recuperado: ", mcastGpAddress, mcastPort)
except Exception as e:
    print(e)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest = (HOST, PORT)
    tcp.connect(dest)
    #print('Para sair use CTRL+X\n')
    tcp.send('E'.encode())

    identifier = tcp.recv(1024).decode()
    print("Identificador recebido: ", identifier)
    if(identifier):
        tcp.send("OK".encode())
    McastAddress = tcp.recv(1024).decode()
    if(McastAddress):
        tcp.send("OK".encode())

    (mcastGpAddress, mcastPort) = McastAddress.split(":")
    print("Endereco MCAST Recebido: ", mcastGpAddress, mcastPort)
    MCastServer = [McastAddress, identifier]
    pickle.dump(MCastServer, open('MCastServer.pkl', 'wb'))
    tcp.close()

#cliente MCAST:


def mc_recv(fromnicip, mcgrpip="224.1.1.5", mcport=50001):
    bufsize = 1024

    receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                             proto=socket.IPPROTO_UDP, fileno=None)

    bindaddr = (mcgrpip, mcport)
    receiver.bind(bindaddr)

    if fromnicip == '0.0.0.0':
        mreq = struct.pack("=4sl", socket.inet_aton(
            mcgrpip), socket.INADDR_ANY)
    else:
        mreq = struct.pack("=4s4s",
                           socket.inet_aton(mcgrpip), socket.inet_aton(fromnicip))
    receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


    recebido = []

    buf, senderaddr = receiver.recvfrom(1024)
    momentoRecebido = time.time()
    cont = 1
    msg = buf.decode() + ": Momento de Recebimento :" + str(momentoRecebido)
    recebido.append(msg)
    print(str(cont)+"-" + msg)
    try:
        for i in range(quantIterac):
            #receiver.settimeout(0.5)
            buf, senderaddr = receiver.recvfrom(1024)
            momentoRecebido = time.time()
            cont += 1
            msg = buf.decode() + ": Momento de Recebimento :" + str(momentoRecebido)
            recebido.append(msg)
            print(str(cont)+"-" + msg)
    finally:
        receiver.close()
        return recebido


def execucaoAtraso():
    mensagensAtraso = mc_recv(sys.argv[1], mcastGpAddress, int(mcastPort))
    return mensagensAtraso


iteracoesAtrasos = []

for i in range(quantMensagens):
    print("Iteracao: ", i)
    iteracoesAtrasos.append(execucaoAtraso())


archive = open('Atraso.txt', 'w')
for i in range(len(iteracoesAtrasos)):
    archive.write("\n\n------Iteracao: "+ str(i) +" ------ tamanho: "+str(len(iteracoesAtrasos[i])))
    contMesg = 1
    for y in iteracoesAtrasos[i]:
        archive.write("\n"+str(contMesg)+"-"+y)
        contMesg += 1
archive.write("\n Fim de arquivo.")
archive.close()




