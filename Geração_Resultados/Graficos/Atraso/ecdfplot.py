import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from os import listdir

distancias = ['10cm', '20cm', '40cm', '80cm', '100cm']

plt.rcParams['xtick.labelsize'] = 16
plt.rcParams['ytick.labelsize'] = 16
plt.rcParams.update({'font.size': 16})

for distancia in distancias:
    path ='./resultados/'+distancia+'/'

    lista_arqs = [arq for arq in listdir(path) if '.txt' in arq]
    lista_arqs = sorted(lista_arqs)
    
    print(lista_arqs)

    atrasos = []

    for i in lista_arqs:
        atraso = []
        arq = open(path+i, 'r')
        linha = arq.readline()
        while linha:
            if('Momento' in linha):
                palavras = linha.split(':')
                valor1 = float(palavras[1])
                valor2 = float(palavras[3])
                intervalo = valor2 - valor1

                atraso.append(intervalo)
            linha = arq.readline()

        arq.close()
        atrasos.append(atraso)

    print(atrasos[0])
    d = {'BBB 1': atrasos[0], 'BBB 2': atrasos[1], 'BBB 3': atrasos[2]}
    df = pd.DataFrame.from_dict(d, orient='index')
    df = df.transpose()
    print(df)

    boxplot = sns.ecdfplot(data=df).set_title("Atraso de recebimento para "+ distancia)
    plt.xlabel('Segundos')
    #plt.show()
    fig = boxplot.get_figure()
    fig.savefig('./ecdfplot/'+distancia+".jpg")
    plt.clf()
