# Import required packages
import pandas as pd 
import numpy as np
import pycountry

# Load data
ccaa = pd.read_csv('https://cnecovid.isciii.es/covid19/resources/datos_ccaas.csv', index_col='fecha', parse_dates=True)
ccaa_poblation = pd.read_csv('población_ccaa.csv', delimiter=';')
ccaa_deaths = pd.read_excel('https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Fallecidos_COVID19.xlsx', parse_dates=True, index_col='Fecha / CCAA', skipfooter=1)
# Transform iso code to ccaa name
def iso_to_ccaa(df):
    return pycountry.subdivisions.get(code='ES-' + df['ccaa_iso']).name
ccaa['ccaa']=ccaa.apply(iso_to_ccaa, axis=1)
# Drop iso code column
ccaa = ccaa.drop('ccaa_iso', axis=1)
# Match CCAA names
ccaa_deaths.columns = ['Andalucía', 'Aragón', 'Asturias, Principado de', 'Illes Balears', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León',  
       'Catalunya', 'Ceuta', 'Valenciana, Comunidad / Valenciana, Comunitat', 'Extremadura', 'Galicia', 'Madrid, Comunidad de', 'Melilla', 'Murcia, Región de',
       'Navarra, Comunidad Foral de / Nafarroako Foru Komunitatea', 'País Vasco / Euskal Herria', 'La Rioja', 'España']

# Melt dataframe
ccaa_deaths.index.rename('fecha', inplace=True)
ccaa_deaths = ccaa_deaths.melt(var_name='ccaa', value_name='deceased', ignore_index=False)

# Compute national stats
total = ccaa.groupby(ccaa.index).sum()
total['ccaa'] = 'España'
# Append national stats to ccaa
ccaa = ccaa.append(total, ignore_index = False).sort_values(by=['fecha', 'ccaa'])
# Append poblations
ccaa = ccaa.join(ccaa_poblation.set_index('ccaa'), on='ccaa')

# Set MultiIndex
ccaa_deaths.set_index([ccaa_deaths.index, 'ccaa'], inplace=True)
ccaa.set_index([ccaa.index, 'ccaa'], inplace=True)

# Append deceased
ccaa = ccaa.join(ccaa_deaths)

# Compute cumulative stats
ccaa['cases_accumulated'] = ccaa.groupby('ccaa')['num_casos'].cumsum()
ccaa['cases_accumulated_PCR'] = ccaa.groupby('ccaa')['num_casos_prueba_pcr'].cumsum()
ccaa['deceased_accumulated'] = ccaa.groupby('ccaa')['deceased'].cumsum()

# Compute rolling stats
ccaa['cases_7_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(7, min_periods=1).sum())
ccaa['cases_14_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(14, min_periods=1).sum())
ccaa['avg_cases_7_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(7, min_periods=1).mean())
ccaa['avg_cases_14_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(14, min_periods=1).mean())

# Compute IA
ccaa['ia_100000_week'] = ccaa['cases_7_days'] * 100000 / ccaa['Población']
ccaa['ia_100000_2week'] = ccaa['cases_14_days'] * 100000 / ccaa['Población']
ccaa['ia_accumulated'] = ccaa['cases_accumulated'] * 100000 / ccaa['Población']

# Save national data in separated csv
total = ccaa.reset_index().set_index('fecha')
total = total.loc[total['ccaa'] == 'España']
total = total.drop(['ccaa', 'Población'], axis=1)
total.to_csv('spain.csv')

# Save ccaa data 
ccaa.to_csv('ccaa.csv')