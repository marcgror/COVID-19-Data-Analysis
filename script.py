# Import required packages
import pandas as pd 
import numpy as np
import pycountry

# Load data
ccaa = pd.read_csv('https://cnecovid.isciii.es/covid19/resources/datos_ccaas.csv', index_col='fecha', parse_dates=True)
ccaa_poblation = pd.read_csv('población_ccaa.csv', delimiter='\t')
# Transform iso code to ccaa name
def iso_to_ccaa(df):
    return pycountry.subdivisions.get(code='ES-' + df['ccaa_iso']).name
ccaa['ccaa']=ccaa.apply(iso_to_ccaa, axis=1)
# Drop iso code column
ccaa = ccaa.drop('ccaa_iso', axis=1)

# Compute national stats
total = ccaa.groupby(ccaa.index).sum()
total['ccaa'] = 'Total'
# Append national stats to ccaa
ccaa = ccaa.append(total, ignore_index = False).sort_values(by=['fecha', 'ccaa'])
# Append poblations
ccaa = ccaa.join(ccaa_poblation.set_index('ccaa'), on='ccaa')

# Compute cumulative stats
ccaa['cases_accumulated'] = ccaa.groupby('ccaa')['num_casos'].cumsum()
ccaa['cases_accumulated_PCR'] = ccaa.groupby('ccaa')['num_casos_prueba_pcr'].cumsum()

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
total = ccaa.loc[ccaa['ccaa'] == 'Total']
total = total.drop('ccaa', axis=1)
total.to_csv('spain.csv')

# Save ccaa data 
ccaa.to_csv('ccaa.csv')