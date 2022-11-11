import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from os import listdir
path ='./resultados'

lista_arqs = [arq for arq in listdir(path) if '.txt' in arq]
print(lista_arqs)

atrasos = []

for i in lista_arqs:
    arq = open('resultados/'+i,'r')
    linha = arq.readline()
    while linha:
        if('Momento' in linha):
            palavras = linha.split(':')
            valor1 = float(palavras[1])
            valor2 = float(palavras[3])
            intervalo = valor2 - valor1
            
            atrasos.append(intervalo)
        linha = arq.readline()

    arq.close()

print(atrasos)
df = pd.DataFrame(data=atrasos,columns=['ms'])

print(df)

boxplot = sns.boxplot(data=df, x='ms').set_title("Atraso de recebimento")
plt.show()
fig = boxplot.get_figure()
fig.savefig("out.png")
