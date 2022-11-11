import socket
import sys
import struct


HOST = '192.168.0.1'     # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

tcp.send('E'.encode())

identifier = tcp.recv(1024).decode()
print("Identificador recebido: ", identifier)
if(identifier):
    tcp.send("OK".encode())
McastAddress = tcp.recv(1024).decode()
if("224" in McastAddress):
    tcp.send("OK".encode())

(mcastGpAddress,mcastPort) = McastAddress.split(":")
print("ENDEREÇO MCAST RECEBIDO: ",mcastGpAddress,mcastPort)
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

    # Receive the mssage
    msg = ""
    while(True):
        buf, senderaddr = receiver.recvfrom(1024)
        msg = buf.decode()

        if(msg == "stop"):
            break

        print("Mensagem recebida:",msg)

    receiver.close()


mc_recv(sys.argv[1], mcastGpAddress, int(mcastPort))
