import socket
import sys
import struct
import pickle


HOST = '192.168.0.1'     # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta

McastAddress = ""
identifier = ""

quantMensagens = 30

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
    msg = buf.decode()
    recebido.append(msg)
    print("Mensagem recebida:", msg)
    try:
        while(True):
            receiver.settimeout(2)
            buf, senderaddr = receiver.recvfrom(1024)
            msg = buf.decode()
            recebido.append(msg)
            print("Mensagem recebida:", msg)
    except:
        receiver.close()
        return recebido







def execucaoPerdaPacote():
    listaMensagensRecebidas = mc_recv(sys.argv[1], mcastGpAddress, int(mcastPort))

    QuantCertas = 0
    QuantErradas = 0
    for i in listaMensagens:
        if(i not in listaMensagensRecebidas):
            QuantErradas+=1
        else:
            QuantCertas+=1
            listaMensagensRecebidas.remove(i)

    if(QuantCertas == len(listaMensagens)):
        print("Nenhuma mensagem foi perdida!")
        return 0
    else:
        print("Cerca de ",QuantErradas," mensagens foram perdidas!")
        return QuantErradas
    #if(len(listaMensagensRecebidas)>0):
        #print("Cerca de ", len(listaMensagensRecebidas)," mensagens foram recebidas duplicadas!")


listaMensagens = []
prefixo = 'Realizando teste de recebimento! Mensagem numero: '
for i in range(1, quantMensagens + 1):
    msg = prefixo + str(i)
    listaMensagens.append(msg)


archive = open('PerdaDePacote.txt', 'w')
perdaTotal = 0

for i in range(1, quantMensagens + 1):
    print("Iteracao: ",i)
    iteracao = execucaoPerdaPacote()
    if(iteracao != 0):
        perdaTotal += iteracao
        archive.write("\n"+str(i)+" -> Perda de " + str(iteracao) +" pacote(s)")

    else:
        archive.write("\n"+str(i)+" -> Nenhum pacote perdido")

archive.write("\nPerda total de pacote(s): "+str(perdaTotal))
archive.close()




