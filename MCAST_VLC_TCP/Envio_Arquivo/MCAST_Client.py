import socket
import sys
import time
import hashlib
import pickle

HOST = '192.168.0.1'     # Endereco IP do Servidor
PORT = 5060            # Porta que o Servidor esta

McastAddress = ""
identifier = ""
buffer = 1024

try:
    identifier = pickle.load(open('IdentificadorMcast.pkl', 'rb'))
    print("Identificador Recuperado: ", identifier)
except Exception as e:
    print(e)
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dest = (HOST, PORT)
    tcp.connect(dest)
    #print('Para sair use CTRL+X\n')
    tcp.send('E'.encode())

    identifier = tcp.recv(1024).decode()
    print("Identificador recebido: ", identifier)
    if (identifier):
        tcp.send("OK".encode())

    pickle.dump(identifier, open('IdentificadorMcast.pkl', 'wb'))
    tcp.close()

#cliente MCAST:
def mc_recv(fromnicip, port=50001):

    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    orig = (fromnicip, port)

    tcp.bind(orig)

    digestServer=''
    archive=''
    while (True):
        sha1 = hashlib.sha1()
        print("Aguardando conexão...")
        tcp.listen(1)
        con, servidor = tcp.accept()
        
        data_bin = b''
        st = time.time()
        TempoInicial = time.time()
        while True:
            datarec = con.recv(buffer)
            if not datarec:
                break
            data_bin += datarec
            if time.time() - st >= 1:  # informacao sobre o total ja carregado
                print("Recebido: %d" % len(data_bin),"Bytes")
                st = time.time()
        tempoGasto = time.time() - TempoInicial
        print("Recebimento completo. Tempo gasto: %.4f" % tempoGasto, "segundos")
        print("Tamanho total de arquivo: %.2f KB\nTaxa media de download: %.2f" % (len(data_bin)/1024,(len(data_bin)/1024)/tempoGasto),'KB/s')
        data = pickle.loads(data_bin)
        if data['file']:  
            archive = data['name']
            print("Nome do arquivo recebido: ", archive)
            with open(archive, 'wb') as f:
                f.write(data['file'])
            digestServer = data['sha1hash']   
            
            with open(archive,'rb') as f2:
                sha1.update(f2.read())
                
            digest = sha1.hexdigest()
            if(digest != digestServer):
                print("Erro! Arquivo corrompido!")
                print("Hash de arquivo recebido:")
                print("\t",digest)
                print("Hash de arquivo em servidor:")
                print("\t",digestServer)
            else:
                print("Arquivo verificado! Match Hash!")
        con.close()


    

while(1):
    mc_recv(sys.argv[1])
    '''try:
        mc_recv(sys.argv[1])
    except Exception as e:
        print("ERRO!", e )
        break'''