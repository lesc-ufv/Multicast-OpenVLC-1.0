import socket
import sys
import struct
import hashlib
import pickle

HOST = '192.168.0.1'     # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta
buffer = 2048

McastAddress = ""
identifier = ""

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

    (mcastGpAddress,mcastPort) = McastAddress.split(":")
    print("Endereco MCAST Recebido: ",mcastGpAddress,mcastPort)
    MCastServer = [McastAddress, identifier]
    pickle.dump(MCastServer, open('MCastServer.pkl', 'wb'))
    tcp.close()


#cliente MCAST:

def mc_recv(fromnicip, mcgrpip="224.1.1.5", mcport=50001):

   
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


    print("Aguardando mensagem...")

    sha1 = hashlib.sha1()
    datagram,_ = receiver.recvfrom(buffer)
    archive = datagram.decode()
    print("Arquivo a receber: ", archive)
    f = open(archive, "wb")

    datagram, _ = receiver.recvfrom(buffer)
    cont = 1
    try:
        while(datagram):
            f.write(datagram)
            receiver.settimeout(2)
            datagram, _ = receiver.recvfrom(buffer)
            cont += 1
            print("Recebendo datagrama ", cont)
    except:
        digestServer, _ = receiver.recvfrom(buffer)
        digestServer = digestServer.decode()
        f.close()
        print("Arquivo recebido!")
        f = open(archive, "rb")
        sha1.update(f.read())
        f.close()
        digest = sha1.hexdigest()
        if(digest != digestServer):
            print("Erro! Arquivo corrompido!")
            print("Hash de arquivo recebido:")
            print("\t",digest)
            print("Hash de arquivo em servidor:")
            print("\t",digestServer)
        else:
            print("Arquivo verificado! Match Hash!")
        receiver.close()


    

while(1):
    try:
        mc_recv(sys.argv[1], mcastGpAddress, int(mcastPort))
    except Exception as e:
        print("ERRO!", e )
        break