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
ccaa_deaths.columns = ['Andalucía', 'Aragón', 'Asturias', 'Illes Balears', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León',  
       'Catalunya', 'Ceuta', 'Comunitat Valenciana', 'Extremadura', 'Galicia', 'Madrid', 'Melilla', 'Murcia',
       'Navarra', 'País Vasco', 'La Rioja', 'España']

# Melt dataframe
ccaa_deaths.index.rename('fecha', inplace=True)
ccaa_deaths = ccaa_deaths.melt(var_name='ccaa', value_name='deceased', ignore_index=False)

# Change large CCAA names
ccaa.loc[ccaa['ccaa'] == 'Asturias, Principado de', 'ccaa'] = 'Asturias'
ccaa.loc[ccaa['ccaa'] == 'Madrid, Comunidad de', 'ccaa'] = 'Madrid'
ccaa.loc[ccaa['ccaa'] == 'Navarra, Comunidad Foral de / Nafarroako Foru Komunitatea', 'ccaa'] = 'Navarra'
ccaa.loc[ccaa['ccaa'] == 'País Vasco / Euskal Herria', 'ccaa'] = 'País Vasco'
ccaa.loc[ccaa['ccaa'] == 'Murcia, Región de', 'ccaa'] = 'Murcia'
ccaa.loc[ccaa['ccaa'] == 'Valenciana, Comunidad / Valenciana, Comunitat', 'ccaa'] = 'Comunitat Valenciana'

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
ccaa['cases_accumulated_AC'] = ccaa.groupby('ccaa')['num_casos_prueba_test_ac'].cumsum()
ccaa['cases_accumulated_otras'] = ccaa.groupby('ccaa')['num_casos_prueba_otras'].cumsum()
ccaa['cases_accumulated_desconocida'] = ccaa.groupby('ccaa')['num_casos_prueba_desconocida'].cumsum()
ccaa['cases_accumulated_PCR_percentage'] = ccaa['cases_accumulated_PCR'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_AC_percentage'] = ccaa['cases_accumulated_AC'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_otras_percentage'] = ccaa['cases_accumulated_otras'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_desconocida_percentage'] = ccaa['cases_accumulated_desconocida'] * 100 / ccaa['cases_accumulated']
ccaa['cases_inc'] = round(ccaa.groupby('ccaa')['num_casos'].diff() / ccaa.groupby('ccaa')['num_casos'].shift() * 100,2)
ccaa['deceased_accumulated'] = ccaa.groupby('ccaa')['deceased'].cumsum()
ccaa['deceased_per_100000'] = round(ccaa['deceased_accumulated'] * 100000 / ccaa['Población'],2)
ccaa['deceased_inc'] = round(ccaa.groupby('ccaa')['deceased'].diff() / ccaa.groupby('ccaa')['deceased'].shift() * 100,2)

# Compute rolling stats
ccaa['cases_7_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(7, min_periods=1).sum())
ccaa['cases_14_days'] = ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(14, min_periods=1).sum())
ccaa['deaths_7_days'] = ccaa.groupby('ccaa')['deceased'].transform(lambda x: x.rolling(7, min_periods=1).sum())
ccaa['deaths_14_days'] = ccaa.groupby('ccaa')['deceased'].transform(lambda x: x.rolling(14, min_periods=1).sum())
ccaa['deaths_7_days_1M'] = round(ccaa['deaths_7_days'] * 1000000 / ccaa['Población'],2)
ccaa['avg_cases_7_days'] = round(ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(7, min_periods=1).mean()),2)
ccaa['avg_cases_14_days'] = round(ccaa.groupby('ccaa')['num_casos'].transform(lambda x: x.rolling(14, min_periods=1).mean()),2)
ccaa['avg_deaths_3_days'] = round(ccaa.groupby('ccaa')['deceased'].transform(lambda x: x.rolling(3, min_periods=1).mean()),2)
ccaa['avg_deaths_7_days'] = round(ccaa.groupby('ccaa')['deceased'].transform(lambda x: x.rolling(7, min_periods=1).mean()),2)

# Compute IA
ccaa['ia_100000_week'] = round(ccaa['cases_7_days'] * 100000 / ccaa['Población'],2)
ccaa['ia_100000_2week'] = round(ccaa['cases_14_days'] * 100000 / ccaa['Población'],2)
ccaa['ia_accumulated'] = round(ccaa['cases_accumulated'] * 100000 / ccaa['Población'],2)

# Save national data in separated csv
total = ccaa.reset_index().set_index('fecha')
total = total.loc[total['ccaa'] == 'España']
total = total.drop(['ccaa', 'Población'], axis=1)
total.to_csv('spain.csv')

# Save ccaa data 
ccaa.to_csv('ccaa.csv')