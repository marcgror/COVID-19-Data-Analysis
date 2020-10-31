# Análisis de la pandémia de Covid-19 en España
- [Análisis de la pandémia de Covid-19 en España](#análisis-de-la-pandémia-de-covid-19-en-españa)
  - [Obtención de los datos](#obtención-de-los-datos)
    - [Aclaraciones](#aclaraciones)
## Obtención de los datos
Los datos sanitarios se obtienen directamente del Ministerio de Sanidad:
- datos de diagnosticados por COVID en España por CCAA: https://cnecovid.isciii.es/covid19/resources/datos_ccaas.csv
- datos de fallecidos diagnosticados con COVID por CCAA: https://www.mscbs.gob.es/profesionales/saludPublica/ccayes/alertasActual/nCov-China/documentos/Fallecidos_COVID19.xlsx

Para calcular otros datos como la incidéncia acumulada, se usan las poblaciones de cada Comunidad proporcionados por el INE, las cuales se pueden consultar en el archivo CSV población_ccaa.csv.

El Ministerio de Sanidad, a través del Instituto Carlos III, facilita los siguientes datos:
- ccaa_iso: código ISO para cada Cominidad Autónoma.
- fecha.
- num_casos: el número de casos totales, confirmados o probables.
- num_casos_prueba_pcr: el número de casos con prueba de laboratorio PCR o técnicas moleculares.
- num_casos_prueba_test_ac: el número de casos con prueba de laboratorio de test rápido de anticuerpos.
- num_casos_prueba_otras: el número de casos con otras pruebas de laboratorio, mayoritariamente por detección de antígeno o técnica Elisa.
- num_casos_prueba_desconocida: el número de casos sin información sobre la prueba de laboratorio.

A partir de ellos, en el script de Python script.py se calculan los siguiente datos, para cada fecha y Comunidad Autónoma:
- ccaa: nombre de la Comunidad Autónoma, usando el campo ccaa_iso. Este último se elimina, ya que deja de ser útil.
- cases_accumulated: número de casos totales detectados. Es acumulativo.
- cases_accumulated_PCR: número de casos totales detectados por PCR. Es acumulativo.
- cases_7_days: número de casos detectados en los últimos 7 días.
- cases_14_days: número de casos detectados en los últimos 14 días.
- avg_cases_7_days: número de casos medio en los últimos 7 días.
- avg_cases_14_days: número de casos medio en los últimos 14 días.
- ia_100000_week: incidéncia acumulada en los últimos 7 días.
- ia_100000_2week: incidéncia acumulada en los últimos 14 días.
- ia_accumulated: incidéncia acumulada desde el inicio de la pandémia.

Por otra parte, utilizando los datos de fallecidos diarios en cada Cominidad Autónoma, se calculan los siguiente campos:
- deceased_accumulated: número de fallecidos desde el inicio de la pandémia. Es acumulativo.
- deceased_per_100000: número de fallecidos por cada 100000 habitantes.
- deaths_7_days: número de fallecidos en los últimos 7 días.
- deaths_14_days: número de fallecidos en los últimos 14 días.
- deaths_7_days_1M: número de fallecidos en los últimos 7 días por cada millón de habitantes.
- avg_deaths_3_days: número de fallecidos medio en los últimos 3 días.
- avg_deaths_7_days: número de fallecidos medio en los últimos 7 días.

Todo este trabajo de calculo de datos se realiza para cada Comunidad Autónoma, en cada fecha. Adicionalmente, se agrupan todas las estadísticas diarias a nivel nacional, que se corresponde con las filas donde 'ccaa' indique España. De esta forma, es posible seguir la evolución de la pandémia tanto a nivel nacional como autonómico.

Finalmente, los datos obtenidos y los calculados se vuelcan en dos archivos CSV, en función de si son datos nacionales (spain.csv) o autonómicos (ccaa.csv)

### Aclaraciones
Los datos de contagiados por COVID proporcionados por el Ministerio de Sanidad no están totalmente completos hasta el último día. Esto quiere decir que se van completando poco a poco, y que los que se corresponden con los días más recientes no son fiables. Por lo tanto, es posible que si se consultan los del día en curso, o los del día anterior, se indique un número de casos ridículamente bajo, o incluso 0.