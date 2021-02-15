# Import required packages
import pandas as pd 
import numpy as np
import pycountry

# Load data
ccaa = pd.read_csv('https://cnecovid.isciii.es/covid19/resources/casos_tecnica_ccaa.csv', index_col='fecha', parse_dates=True, dayfirst=True)
print("Visual data validation:")
print(ccaa.tail())
ccaa_poblation = pd.read_csv('población_ccaa.csv', delimiter=';')
ccaa_deaths = pd.read_csv('https://raw.githubusercontent.com/datadista/datasets/master/COVID%2019/ccaa_covid19_datos_sanidad_nueva_serie.csv', 
        delimiter=',', header=0, names=['fecha', 'cod-ine', 'ccaa', 'cases', 'deceased', 'hospitalizated', 'UCI'], parse_dates=True, index_col='fecha')
ccaa_deaths = ccaa_deaths.drop(['cod-ine', 'cases'], axis=1)
print("Visual data validation:")
print(ccaa_deaths.tail())

# Transform iso code to ccaa name
def iso_to_ccaa(df):
    return pycountry.subdivisions.get(code=df['ccaa_iso']).name
ccaa['ccaa_iso'] = 'ES-' + ccaa['ccaa_iso']
ccaa['ccaa']=ccaa.apply(iso_to_ccaa, axis=1)

# Drop iso code column
ccaa = ccaa.drop('ccaa_iso', axis=1)

# Match CCAA names
ccaa = ccaa.reset_index()
ccaa.set_index('fecha', inplace=True)
ccaa.loc[ccaa['ccaa'] == 'Asturias, Principado de', 'ccaa'] = 'Asturias'
ccaa.loc[ccaa['ccaa'] == 'Madrid, Comunidad de', 'ccaa'] = 'Madrid'
ccaa.loc[ccaa['ccaa'] == 'Navarra, Comunidad Foral de / Nafarroako Foru Komunitatea', 'ccaa'] = 'Navarra'
ccaa.loc[ccaa['ccaa'] == 'País Vasco / Euskal Herria', 'ccaa'] = 'País Vasco'
ccaa.loc[ccaa['ccaa'] == 'Murcia, Región de', 'ccaa'] = 'Murcia'
ccaa.loc[ccaa['ccaa'] == 'Valenciana, Comunidad / Valenciana, Comunitat', 'ccaa'] = 'Comunitat Valenciana'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Baleares', 'ccaa'] = 'Illes Balears'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Castilla La Mancha', 'ccaa'] = 'Castilla-La Mancha'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Cataluña', 'ccaa'] = 'Catalunya'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'C. Valenciana', 'ccaa'] = 'Comunitat Valenciana'

# Set MultiIndex
ccaa_deaths.set_index([ccaa_deaths.index, 'ccaa'], inplace=True)
ccaa.set_index([ccaa.index, 'ccaa'], inplace=True)

# Join deceased
ccaa = ccaa.join(ccaa_deaths)
ccaa = ccaa.reset_index()
ccaa.set_index('fecha', inplace=True)

# Replace empty cells 
ccaa.fillna(0, inplace=True)
ccaa[['deceased', 'hospitalizated', 'UCI']] = ccaa[['deceased', 'hospitalizated', 'UCI']].astype(int)

# Compute national stats
total = ccaa.groupby(ccaa.index).sum()
total['ccaa'] = 'España'

# Append national stats to ccaa
ccaa = ccaa.append(total, ignore_index = False).sort_values(by=['fecha', 'ccaa'])

# Join poblations
ccaa = ccaa.join(ccaa_poblation.set_index('ccaa'), on='ccaa')

# Store data for tableau
ccaa.to_csv('ccaa_tableau.csv')

# Compute cumulative stats
ccaa['cases_accumulated'] = ccaa.groupby('ccaa')['num_casos'].cumsum()
ccaa['cases_accumulated_PCR'] = ccaa.groupby('ccaa')['num_casos_prueba_pcr'].cumsum()
ccaa['cases_accumulated_AC'] = ccaa.groupby('ccaa')['num_casos_prueba_test_ac'].cumsum()
ccaa['cases_accumulated_AG'] = ccaa.groupby('ccaa')['num_casos_prueba_ag'].cumsum()
ccaa['cases_accumulated_elisa'] = ccaa.groupby('ccaa')['num_casos_prueba_elisa'].cumsum()
ccaa['cases_accumulated_desconocida'] = ccaa.groupby('ccaa')['num_casos_prueba_desconocida'].cumsum()
ccaa['cases_accumulated_PCR_percentage'] = ccaa['cases_accumulated_PCR'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_AC_percentage'] = ccaa['cases_accumulated_AC'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_ag_percentage'] = ccaa['cases_accumulated_AG'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_elisa_percentage'] = ccaa['cases_accumulated_elisa'] * 100 / ccaa['cases_accumulated']
ccaa['cases_accumulated_desconocida_percentage'] = ccaa['cases_accumulated_desconocida'] * 100 / ccaa['cases_accumulated']
ccaa['cases_inc'] = round(ccaa.groupby('ccaa')['num_casos'].diff() / ccaa.groupby('ccaa')['num_casos'].shift() * 100,2)
ccaa['deceased_accumulated'] = ccaa.groupby('ccaa')['deceased'].cumsum(skipna=False)
ccaa['deceased_per_100000'] = round(ccaa['deceased_accumulated'] * 100000 / ccaa['Población'],2)
ccaa['deceased_inc'] = round(ccaa.groupby('ccaa')['deceased'].diff() / ccaa.groupby('ccaa')['deceased'].shift() * 100,2)
ccaa['hospitalizated_accumulated'] = ccaa.groupby('ccaa')['hospitalizated'].cumsum()
ccaa['UCI_accumulated'] = ccaa.groupby('ccaa')['UCI'].cumsum()

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
ccaa['avg_hospitalizated_7_days'] = round(ccaa.groupby('ccaa')['hospitalizated'].transform(lambda x: x.rolling(7, min_periods=1).mean()),2)
ccaa['avg_UCI_7_days'] = round(ccaa.groupby('ccaa')['UCI'].transform(lambda x: x.rolling(7, min_periods=1).mean()),2)

# Compute IA
ccaa['ia_100000_week'] = round(ccaa['cases_7_days'] * 100000 / ccaa['Población'],2)
ccaa['ia_100000_2week'] = round(ccaa['cases_14_days'] * 100000 / ccaa['Población'],2)
ccaa['ia_accumulated'] = round(ccaa['cases_accumulated'] * 100000 / ccaa['Población'],2)

# Save national data in separated csv
total = ccaa.reset_index().set_index('fecha')
total = total.loc[total['ccaa'] == 'España']
total = total.drop(['ccaa', 'Población'], axis=1)
total.to_csv('spain.csv')

# Store data for datawrapper
dw_data = ccaa.reset_index().set_index('fecha')
dw_data = dw_data.loc[dw_data['ccaa'] != 'España']
dw_data.loc[dw_data['ccaa'] == 'Asturias', 'ccaa'] = 'Principado de Asturias'
dw_data.loc[dw_data['ccaa'] == 'Madrid', 'ccaa'] = 'Comunidad de Madrid'
dw_data.loc[dw_data['ccaa'] == 'Navarra', 'ccaa'] = 'Comunidad Foral de Navarra'
dw_data.loc[dw_data['ccaa'] == 'Catalunya', 'ccaa'] = 'Cataluña'
dw_data.loc[dw_data['ccaa'] == 'Murcia', 'ccaa'] = 'Región de Murcia'
dw_data.loc[dw_data['ccaa'] == 'Comunitat Valenciana', 'ccaa'] = 'Comunidad Valenciana'
dw_data.loc[dw_data['ccaa'] == 'Illes Balears', 'ccaa'] = 'Islas Baleares'
dw_data[['ccaa', 'cases_accumulated', 'deceased_accumulated', 'cases_7_days', 'deaths_7_days', 'ia_100000_2week']].tail(19).to_csv('dw_data.csv')

# Save ccaa data 
ccaa.to_csv('ccaa.csv')