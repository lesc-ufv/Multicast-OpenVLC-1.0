import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from os import listdir

delays = ['0', '0.015625', '0.03125', '0.0625', '0.09375', '0.125', '0.25']

plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
plt.rcParams.update({'font.size': 14})
dic = {'Delays (Segundos)':[],'Pacotes perdidos':[]}
for delay in delays:
    path = './Resultados/'+delay+'/'

    lista_arqs = [arq for arq in listdir(path) if '.txt' in arq]
    #lista_arqs = sorted(lista_arqs)

    #print(lista_arqs)

    
    for i in lista_arqs:
        vel = []
        arq = open(path+i, 'r')
        linha = arq.readline()
        while linha:
            if('Perda total de pacote(s):' in linha):
                palavras = linha.split(':')
                valor = float(palavras[1])
                dic['Delays (Segundos)'].append(delay[:5])
                dic['Pacotes perdidos'].append(valor)
            linha = arq.readline()

        arq.close()

print(dic)
df = pd.DataFrame.from_dict(dic)
print(df)

boxplot = sns.barplot(data=df,x='Delays (Segundos)',y='Pacotes perdidos')
#plt.ylabel('Delays (Segundos)')
plt.show()   
fig = boxplot.get_figure()
fig.savefig("./graph/result.jpg")
plt.clf()
