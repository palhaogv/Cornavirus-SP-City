import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Sites used https://covid.saude.gov.br/ (SP cases confirmed)
df_SP_CC = pd.read_csv('HIST_PAINEL_COVIDBR_20mai2020.csv')
df_SP_CC = df_SP_CC[['municipio', 'data', 'casosAcumulado', 'obitosAcumulado']]
df_SP_CC['data'] = pd.to_datetime(df_SP_CC['data'])
df_SP_CC = df_SP_CC[df_SP_CC['municipio'] == 'São Paulo']  # selecting only SP city
df_SP_CC = df_SP_CC.sort_values(by='data')
df_SP_CC['municipio'] = df_SP_CC['municipio'].str.upper()

# Sites used https://www.saopaulo.sp.gov.br/coronavirus/isolamento/ (SP social isolation rate)
df_SP_SI_rating = pd.read_csv('Grafico_Cidade_SP2.csv')
df_SP_SI_rating = df_SP_SI_rating[['Data', 'Município1', 'Índice De Isolamento']]
df_SP_SI_rating['Data'] = pd.to_datetime(df_SP_SI_rating['Data'])
df_SP_SI_rating.columns = ['data', 'municipio', 'Índice De Isolamento']
df_SP_SI_rating['Índice De Isolamento'] = df_SP_SI_rating['Índice De Isolamento'].str.rstrip('%').astype(
    'float') / 100.0
df_SP_SI_rating = df_SP_SI_rating.sort_values(by='data')
df_SP_SI_rating = df_SP_SI_rating.reset_index()

list_geral_columns = ['municipio_x', 'data', 'casosAcumulado', 'obitosAcumulado', 'Índice De Isolamento']
list_geral_columns2 = ['City', 'Date', 'Total Cases', 'Total Deaths', 'Social Isolation Rate']
list_SI_days = []

# Social Isolation after x days
for c in range(1, 20):
    df_SP_SI_rating['Social Isolation Rate after ' + str(c) + ' days'] = 0
    list_geral_columns.append('Social Isolation Rate after ' + str(c) + ' days')
    list_geral_columns2.append('Social Isolation Rate after ' + str(c) + ' days')
    list_SI_days.append('Social Isolation Rate after ' + str(c) + ' days')
    for i in range(c, len(df_SP_SI_rating)):
        df_SP_SI_rating.loc[i, 'Social Isolation Rate after ' + str(c) + ' days'] = df_SP_SI_rating.loc[
            i - c, 'Índice De Isolamento']

df_SP_SI_rating = df_SP_SI_rating[df_SP_SI_rating['data'] > '2020-03-27']

# mearging Data Frames
df_geral = pd.merge(df_SP_CC, df_SP_SI_rating, how='left', left_on='data', right_on='data')
df_geral = df_geral[list_geral_columns]
df_geral.columns = [list_geral_columns2]
df_geral['Proportional Growth by Day'] = 0  # creating the Proportional Growth by Day
for i in range(1, len(df_geral)):
    df_geral.loc[i, 'Proportional Growth by Day'] = (df_geral.loc[i, 'Total Cases'] - df_geral.loc[
        i - 1, 'Total Cases']) / df_geral.loc[i - 1, 'Total Cases']
df_geral = df_geral[df_geral['Date'] > '2020-03-31']
df_geral.replace(0, np.nan, inplace=True)

# identify the minor correlation
for item in list_SI_days:
    c, p = stats.pearsonr(df_geral['Proportional Growth by Day'], df_geral[item])
    if list_SI_days[0] == item:
        min_cvalue = 0
        min_pvalue = 0
        min_itemvalue = 0
    if p < 0.05 and c < 0:
        if c < min_cvalue:
            min_cvalue = c
            min_itemvalue = item
            min_pvalue = p

# Graphic study
print(
    f'The minor correlation in 19 days between Social Isolation rate and Proportional Growth by day is {min_itemvalue}, with a {min_cvalue:.3f} correlation and {min_pvalue:.6f} p-value.')
sns.jointplot(df_geral[min_itemvalue], df_geral['Proportional Growth by Day'], space=0, color="r")
plt.show()