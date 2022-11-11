import socket
import os

HOST = '192.168.0.1'    # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta
tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
dest = (HOST, PORT)
tcp.connect(dest)

tcp.send('Q'.encode())


if(tcp.recv(1024).decode()=="RSucess!"):
    try:
        os.remove('MCastServer.pkl')
    except: 
        print("ERRO ao apagar endereco salvo!")
    print("Removido com sucesso!")
else:
    print("Erro! Cliente não encontrado em lista!")

tcp.close()
