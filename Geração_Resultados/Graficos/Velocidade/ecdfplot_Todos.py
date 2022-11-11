import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from os import listdir

distancias = ['10cm','20cm','40cm','80cm','100cm']

plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams.update({'font.size': 16})

for distancia in distancias:
    path ='./resultados/'+distancia+'/'

    lista_arqs = [arq for arq in listdir(path) if '.txt' in arq]
    lista_arqs = sorted(lista_arqs)
    
    print(lista_arqs)

    velocidades = []

    for i in lista_arqs:
        vel = []
        arq = open(path+i, 'r')
        linha = arq.readline()
        while linha:
            if('KB/s' in linha):
                palavras = linha.split(' ')
                valor = float(palavras[len(palavras)-2])
                if(valor<=2):
                    vel.append(valor * 8)
            linha = arq.readline()

        arq.close()
        velocidades.append(vel)

    print(velocidades[0])
    d = {'BBB 1': velocidades[0], 'BBB 2': velocidades[1], 'BBB 3': velocidades[2]}
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df.transpose()
    print(df)

    boxplot = sns.ecdfplot(data=df).set_title("Velocidade de cada BBB para "+ distancia)
    plt.xlabel('Kb/s')
    #plt.show()
    fig = boxplot.get_figure()
    fig.savefig('./ecdfplot/'+distancia+".jpg")
    plt.clf()
