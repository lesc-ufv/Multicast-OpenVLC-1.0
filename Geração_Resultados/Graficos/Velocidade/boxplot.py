import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

from os import listdir

lista_arqs = [arq for arq in listdir('./resultados')]
print(lista_arqs)

velocidades = []

for i in lista_arqs:
    arq = open('resultados/'+i,'r')
    linha = arq.readline()
    while linha:
        if('KB/s' in linha):
            palavras = linha.split(' ')
            valor = float(palavras[len(palavras)-2])
            if(valor<3):
                velocidades.append(valor * 8)
        linha = arq.readline()

    arq.close()

print(velocidades)
df = pd.DataFrame(data=velocidades,columns=['Kb/s'])

print(df)

boxplot = sns.boxplot(data=df, x='Kb/s').set_title("Velocidade de download")
plt.show()
fig = boxplot.get_figure()
fig.savefig("out.png")
