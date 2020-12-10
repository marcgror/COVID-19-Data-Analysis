# Import required packages
import pandas as pd 
import numpy as np
import pycountry

# Load data
ccaa = pd.read_csv('https://cnecovid.isciii.es/covid19/resources/datos_ccaas.csv', index_col='fecha', parse_dates=True, dayfirst=True)
ccaa_poblation = pd.read_csv('población_ccaa.csv', delimiter=';')
ccaa_deaths = pd.read_csv('https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov/documentos/Datos_Casos_COVID19.csv', header=0, keep_default_na=True, dayfirst=True, names=['ccaa_iso', 'fecha', 'casos', 'hospitalizated', 'UCI', 'deceased'], parse_dates=True, skiprows=6, delimiter=';', index_col='fecha')
ccaa_deaths_old = pd.read_excel('https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Fallecidos_COVID19.xlsx', parse_dates=True, index_col='Fecha / CCAA', skipfooter=1)

# Transform iso code to ccaa name
def iso_to_ccaa(df):
    return pycountry.subdivisions.get(code=df['ccaa_iso']).name
ccaa['ccaa_iso'] = 'ES-' + ccaa['ccaa_iso']
ccaa['ccaa']=ccaa.apply(iso_to_ccaa, axis=1)
ccaa_deaths['ccaa'] = ccaa_deaths.apply(iso_to_ccaa, axis=1)

# Drop iso code column
ccaa = ccaa.drop('ccaa_iso', axis=1)
ccaa_deaths = ccaa_deaths.drop(['ccaa_iso', 'casos'], axis=1)

# New dataframes
hosp_uci = ccaa_deaths[['ccaa', 'hospitalizated', 'UCI']]
ccaa_deaths = ccaa_deaths.drop(['hospitalizated', 'UCI'], axis=1)
ccaa_deaths = ccaa_deaths['18-11-2020':]

# Match CCAA names
ccaa_deaths_old = ccaa_deaths_old.drop('España', 1)
ccaa_deaths_old.columns = ['Andalucía', 'Aragón', 'Asturias', 'Illes Balears', 'Canarias', 'Cantabria', 'Castilla-La Mancha', 'Castilla y León',  
       'Catalunya', 'Ceuta', 'Comunitat Valenciana', 'Extremadura', 'Galicia', 'Madrid', 'Melilla', 'Murcia',
       'Navarra', 'País Vasco', 'La Rioja']

# Melt dataframe
ccaa_deaths_old.index.rename('fecha', inplace=True)
ccaa_deaths_old = ccaa_deaths_old.melt(var_name='ccaa', value_name='deceased', ignore_index=False)

# Append hospitalizated and UCI
hosp_uci.set_index([hosp_uci.index, 'ccaa'], inplace=True)
ccaa.set_index([ccaa.index, 'ccaa'], inplace=True)
ccaa = ccaa.join(hosp_uci)

# Change large CCAA names
ccaa = ccaa.reset_index()
ccaa.set_index('fecha', inplace=True)
ccaa.loc[ccaa['ccaa'] == 'Asturias, Principado de', 'ccaa'] = 'Asturias'
ccaa.loc[ccaa['ccaa'] == 'Madrid, Comunidad de', 'ccaa'] = 'Madrid'
ccaa.loc[ccaa['ccaa'] == 'Navarra, Comunidad Foral de / Nafarroako Foru Komunitatea', 'ccaa'] = 'Navarra'
ccaa.loc[ccaa['ccaa'] == 'País Vasco / Euskal Herria', 'ccaa'] = 'País Vasco'
ccaa.loc[ccaa['ccaa'] == 'Murcia, Región de', 'ccaa'] = 'Murcia'
ccaa.loc[ccaa['ccaa'] == 'Valenciana, Comunidad / Valenciana, Comunitat', 'ccaa'] = 'Comunitat Valenciana'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Asturias, Principado de', 'ccaa'] = 'Asturias'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Madrid, Comunidad de', 'ccaa'] = 'Madrid'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Navarra, Comunidad Foral de / Nafarroako Foru Komunitatea', 'ccaa'] = 'Navarra'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'País Vasco / Euskal Herria', 'ccaa'] = 'País Vasco'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Murcia, Región de', 'ccaa'] = 'Murcia'
ccaa_deaths.loc[ccaa_deaths['ccaa'] == 'Valenciana, Comunidad / Valenciana, Comunitat', 'ccaa'] = 'Comunitat Valenciana'

# New dataframe contained all deceased
ccaa_deaths_old = ccaa_deaths_old.append(ccaa_deaths)

# Set MultiIndex
ccaa_deaths_old.set_index([ccaa_deaths_old.index, 'ccaa'], inplace=True)
ccaa.set_index([ccaa.index, 'ccaa'], inplace=True)

# Join deceased
ccaa = ccaa.join(ccaa_deaths_old)
ccaa = ccaa.reset_index()
ccaa.set_index('fecha', inplace=True)

# Replace empty cells 
ccaa.fillna(0, inplace=True)

# Compute national stats
total = ccaa.groupby(ccaa.index).sum()
total['ccaa'] = 'España'

# Append national stats to ccaa
ccaa = ccaa.append(total, ignore_index = False).sort_values(by=['fecha', 'ccaa'])

# Join poblations
ccaa = ccaa.join(ccaa_poblation.set_index('ccaa'), on='ccaa')

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