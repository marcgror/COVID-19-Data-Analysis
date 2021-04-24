
# Import required packages
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from ipywidgets import widgets
import matplotlib.dates as mdates
import chart_studio.plotly as py
import chart_studio.tools as tls
sns.set_style(style="darkgrid")
from datawrapper import Datawrapper
import streamlit as st
from funciones import create_interactive_plot
def write():
    st.title('Análisis de los datos del COVID-19 en España')
    st.empty()
    st.empty()
    st.markdown('2020 y 2021 serán siempre recordados como los años de la pandemia de COVID-19. España ha sido y es uno de los países más afectados, \
        tanto en la primera ola en marzo como en la siguiente en setiembre.')
    st.markdown('Para analizar la situación, a nivel nacional y autonómico, se usarán los datos proporcionados por el Ministerio de Sanidad.')
    # Load each data file from the repository
    ccaa = pd.read_csv('ccaa.csv', parse_dates=True)
    #provincias = pd.read_csv('https://raw.githubusercontent.com/montera34/escovid19data/master/data/output/covid19-provincias-spain_consolidated.csv')
    spain = pd.read_csv('spain.csv', parse_dates=True)

    sections = ['España', 'CCAA']
    st.sidebar.title('COVID')
    section = st.sidebar.radio('Alcance', sections)

    if section == 'España':
        st.header('España')
        st.subheader('Métodos de diagnóstico del COVID-19')
        st.markdown('En España, el COVID se está detectando principalmente usando las pruebas de PCR y test de anticuerpos, a parte de otras pruebas como el test de antígenos. \
        La prueba PCR (Polimerasa Chain Reaction) es una prueba de diagnóstico utilizada para detectar fragmentos del material genético de un patógeno. En este caso en concreto, \
        el patógeno se corresponde con el virus SARS-CoV-2. La idea es sencilla: se toma una muestra respiratoria de la persona sospechosa de infección, y se analiza en un laboratorio \
        de microbiología con un PCR en busca de una molécula de ARN del virus. El positivo vendría cuando la prueba detecta ese ARN del virus, mientras será negativo en caso contrario. \
        Actualmente se dispone tanto de datos de contagiados diagnosticados con PCR como de diagnosticados con otros tipos de prueba, como puede ser el test de anticuerpos o de antígenos. \
        El siguiente gráfico muestra la contribución en porcentaje de cada tipo de prueba. Como es obvio, más de un 75 % de las detecciones de contagiados son gracias a PCR. La siguiente \
        que más contribuye a la detección de la enfermedad es el test de antígenos.')

        labels = ['PCR', 'Test AC', 'Test AG', ' Elisa', 'Desconocida']
        values = list(spain[['num_casos_prueba_pcr', 'num_casos_prueba_test_ac', 'num_casos_prueba_ag', 'num_casos_prueba_elisa', 'num_casos_prueba_desconocida']].sum())
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.3)], layout=dict(title='Contribución de cada método de detección', width=500))
        py.iplot(fig, filename='Test Pie Chart')
        st.plotly_chart(fig)


        st.subheader('Evolución de los contagios')
        st.markdown('En la siguiente tabla se muestran los casos diarios, acumulados, el incremento diario, en los últimos 7 y 14 días, la media de casos en los últimos 7 y 14 días, \
        la incidéncia acumulada en los últimos 7 y 14 días y la acumulada para los últimos 10 días a nivel nacional:')
        st.dataframe(spain[['fecha', 'num_casos', 'cases_accumulated', 'cases_inc', 'cases_7_days', 'cases_14_days', 'avg_cases_7_days', 
        'avg_cases_14_days', 'ia_100000_week', 'ia_100000_2week', 'ia_accumulated']].tail(10).set_index('fecha'))

        st.markdown('La curva de contagiados en España desde el inicio de la pandémia se muestra a continuación:')

        fig = go.Figure()
        fig.add_trace(go.Bar(x=spain['fecha'], y=spain['num_casos'], name='Nuevos casos'))
        fig.add_trace(go.Scatter(x=spain['fecha'], y=spain['avg_cases_7_days'], name='Media de 7 días'))
        fig.update_layout(legend=dict(orientation='h', bgcolor='LightSteelBlue'), width=2100, title='Casos diarios desde el inicio de la pandémia')
        st.plotly_chart(fig)

        st.markdown('Las tres olas se pueden diferenciar claramente. Los efectos del confinamiento, desescalada y fin del Estado de Alarma son también evidentes, \
        ya que el número de contagios diarios decae a mínimos practicamente hasta principios de julio, fruto del parón social y laboral del país. \
        Es entonces cuando empiezan a aumentar los nuevos positivos, seguramente porque la "Nueva Normalidad" lleva vigente 1-2 semanas en toda España, \
        y por lo tanto la población empieza poco a poco a interactuar de nuevo. El hecho de que esta vuelta a la socialización y al trabajo se diera en verano seguramente no ayuda tampoco.')

        st.markdown('Si nos fijamos en los positivos acumulados, las tendencias son prácticamente las mismas, como es lógico:')

        fig = go.Figure(data=[go.Bar(x=spain['fecha'], y=spain['cases_accumulated'])], layout=go.Layout(title=go.layout.Title(text='Casos PCR acumulados desde el inicio de la pandémia')))
        fig.update_layout(width=2100)
        st.plotly_chart(fig)

        st.subheader('Incidéncia acumulada')
        st.markdown('La incidéncia acumulada (IA) es una forma de medir el impacto de la pandémia en cada territorio teniendo en cuenta su población. Por lo tanto, \
        permite comparar valores entre distintas regiones/paises y establecer valores máximos que, una vez superados, exijan aplicar medidas de restricción de movilidad. \
        La evolución de la IA en 7 y 14 días durante toda la pandémia se muestra a continuación:')

        fig = go.Figure(data=[go.Scatter(x=spain['fecha'], y=spain['ia_100000_2week'], mode='lines', name='IA 14 días')], layout=go.Layout(title=go.layout.Title(text='Incidencia acumulada')))
        fig.add_trace(go.Scatter(x=spain['fecha'], y=spain['ia_100000_week'], mode='lines', name='IA 7 días'))
        fig.update_layout(width=2100, legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)

        st.markdown('Se observa una tendéncia similar a la curva de contágios.')

        st.subheader('Fallecidos')
        st.dataframe(spain[['fecha', 'deceased', 'deceased_accumulated', 'deceased_inc', 'deaths_7_days', 'deaths_14_days', 'avg_deaths_3_days', 'avg_deaths_7_days', 'deceased_per_100000', 'deaths_7_days_1M']].tail(10).set_index('fecha'))

        st.markdown('El siguiente paso es el número de fallecidos. A continuación se muestra la evolución del número de fallecidos diario diagnosticados con COVID desde el inicio de la pandémia:')

        fig = go.Figure(data=[go.Bar(x=spain['fecha'], y=spain['deceased'], name='Fallecidos diarios')], layout=go.Layout(title=go.layout.Title(text='Fallecimientos diarios desde el inicio de la pandémia')))
        fig.add_trace(go.Scatter(x=spain['fecha'], y=spain['avg_deaths_7_days'], name='Media de 7 días'))
        fig.update_yaxes(range=[0,1000])
        fig.update_layout(width=2100, legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)

        spain['fecha_dt'] = pd.to_datetime(spain['fecha'])
        spain_deaths_week = spain.resample('W-Mon', on='fecha_dt', label='left', closed='left')['deceased'].sum().reset_index().sort_values('fecha_dt')
        spain = spain.drop('fecha_dt', axis=1)
        fig = go.Figure(data=[go.Bar(x=spain_deaths_week['fecha_dt'], y=spain_deaths_week['deceased'], name='Fallecidos semanales')], layout=go.Layout(title=go.layout.Title(text='Fallecimientos semanales desde el inicio de la pandémia')))
        fig.update_yaxes(range=[0,6000])
        fig.update_layout(width=2100, legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)


        st.markdown('Durante la primera ola, se alcanzaron cifras diarias de más de 1000 muertos diarios positivos por COVID. Gracias al confinamiento, estas cifras fueron disminuyendo \
        lentamente durante mayo y junio, llegando a su mínimo durante el verano. Una vez los contagios e infectados vuelven a incrementarse a finales de agosto, los fallecidos empiezan a aumentar también.')

        fig = go.Figure(data=[go.Bar(x=spain['fecha'], y=spain['deceased_accumulated'])], layout=go.Layout(title=go.layout.Title(text='Fallecimientos acumulados desde el inicio de la pandémia')))
        fig.update_layout(width=2100)
        st.plotly_chart(fig)

        st.markdown('En el acumulado, se puede observar un estancamiento en el número de fallecidos durante el verano, pero a partir de los últimos días de agosto se observa de nuevo \
        una tendencia al aumento.')
        st.subheader('Ingresados y en UCI')

        fig = go.Figure(data=[go.Bar(x=spain['fecha'], y=spain['hospitalizated'], name='Hospitalizados diarios')], layout=go.Layout(title=go.layout.Title(text='Hospitalizados diarios desde el inicio de la pandémia')))
        fig.add_trace(go.Scatter(x=spain['fecha'], y=spain['avg_hospitalizated_7_days'], name='Media de 7 días'))
        fig.update_layout(width=2100, legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)

        fig = go.Figure(data=[go.Bar(x=spain['fecha'], y=spain['UCI'], name='Ingresados en UCI diarios')], layout=go.Layout(title=go.layout.Title(text='Ingresados en UCI diarios desde el inicio de la pandémia')))
        fig.add_trace(go.Scatter(x=spain['fecha'], y=spain['avg_UCI_7_days'], name='Media de 7 días'))
        fig.update_layout(width=2100, legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)
    if section == 'CCAA':
        st.header('CCAA')

        st.subheader('Métodos de diagnóstico del COVID-19')

        x = ccaa['ccaa'].unique().tolist()
        fig = go.Figure(layout=go.Layout(title=go.layout.Title(text='Distribución de los diferentes métodos de diagnóstico para cada CCAA')))
        fig.add_trace(go.Bar(y=x, x=ccaa['cases_accumulated_PCR_percentage'].tail(20), name='PCR', orientation='h'))
        fig.add_trace(go.Bar(y=x, x=ccaa['cases_accumulated_AC_percentage'].tail(20), name='Anticuerpos', orientation='h'))
        fig.add_trace(go.Bar(y=x, x=ccaa['cases_accumulated_ag_percentage'].tail(20), name='Antígenos', orientation='h'))
        fig.add_trace(go.Bar(y=x, x=ccaa['cases_accumulated_elisa_percentage'].tail(20), name='Elisa', orientation='h'))
        fig.add_trace(go.Bar(y=x, x=ccaa['cases_accumulated_desconocida_percentage'].tail(20), name='Desconocido', orientation='h'))
        fig.update_layout(width=1200, barmode='stack', legend=dict(orientation='h', bgcolor='LightSteelBlue'))
        st.plotly_chart(fig)

        st.markdown('A partir de los datos separados por Comunidades Autónomas es posible seguir la evolución de la pandemia en estas.')

        st.subheader('Evolución de los contagios y fallecidos')
        st.markdown('Empecemos con una tabla resumen: en ella se muestran los casos acumulados diagnosticados por PCR, el número de nuevos casos (diarios, en 7 y en 14 días) \
        y la IA por 100000 habitantes para cada comunidad autónoma, ordenado por IA:')

        st.dataframe(ccaa[['fecha', 'ccaa','cases_accumulated', 'num_casos', 'cases_7_days', 'cases_14_days', 'ia_100000_week', 'ia_100000_2week']].tail(20).set_index('fecha'), height=1000)

        st.markdown('En la siguiente tabla se muestran los fallecimientos acumulados, diarios, incrementos respecto al día anterior, en la última semana y por cada 100000 habitantes, \
        ordenados por este último:')
        st.dataframe(ccaa[['fecha', 'ccaa', 'deceased_accumulated', 'deceased', 'deceased_inc', 'deaths_7_days', 'deceased_per_100000']].tail(20).set_index('fecha'), height=1000)

        st.subheader('Curvas casos y fallecidos CCAA')

        ca = st.selectbox('Selecciona CCAA', ccaa['ccaa'].unique())
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['num_casos'], fill='tonexty', name='Casos', line_color='darkcyan'))
        fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['deceased'],  fill='tonexty', name='Fallecidos', line_color='darkcyan'))
        fig.update_layout(showlegend=False, title='# casos diarios para ' +ca, width=1600, height=800)
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    type='buttons',
                    bgcolor='LightSteelBlue',
                    buttons=list([
                        dict(label="Casos",
                            method="update",
                            args=[{"visible": [True, False]},
                                {"title": "# casos diarios para cada CA"}]),
                        dict(label="Fallecidos",
                            method="update",
                            args=[{"visible": [False, True]},
                                {"title": "# de fallecidos diarios para cada CA"}]),
                    ]),
                    direction="left",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.4,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ])
        st.plotly_chart(fig)
        rows = 5
        cols=4
        st.subheader('Incidéncia acumulada')
        fig = make_subplots(rows=rows, cols=cols, vertical_spacing=0.05, subplot_titles=ccaa['ccaa'].unique())
        i, j = 1, 1
        for ca in ccaa['ccaa'].unique():
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['ia_100000_week'], fill='tonexty', name=ca, line_color='darkcyan'), row=i, col=j)
            j+=1
            if j>cols:
                i+=1
                j=1
        fig.update_layout(showlegend=False, width=1600, height=1200, title='Incidencia acumulada en una semana para cada CA')
        st.plotly_chart(fig)

        fig = make_subplots(rows=rows, cols=cols, vertical_spacing=0.05, subplot_titles=ccaa['ccaa'].unique())
        i, j = 1, 1
        for ca in ccaa['ccaa'].unique():
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['ia_100000_2week'], fill='tonexty', name=ca, line_color='darkcyan'), row=i, col=j)
            j+=1
            if j>cols:
                i+=1
                j=1
        fig.update_layout(showlegend=False, width=1600, height=1200, title='Incidencia acumulada en dos semanas para cada CA')
        fig.add_hline(y=150, line_color='red', row='all', col='all')
        st.plotly_chart(fig)

        st.subheader('Curvas casos y fallecidos acumulados CCAA')
        fig = make_subplots(rows=rows, cols=cols, vertical_spacing=0.05, subplot_titles=ccaa['ccaa'].unique())
        i, j = 1, 1
        for ca in ccaa['ccaa'].unique():
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['cases_accumulated'], fill='tonexty', name='Casos', line_color='darkcyan'), row=i, col=j)
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['deceased_accumulated'],  fill='tonexty', name='Fallecidos', line_color='darkcyan'), row=i, col=j)
            j+=1
            if j>cols:
                i+=1
                j=1
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    type='buttons',
                    bgcolor='LightSteelBlue',
                    buttons=list([
                        dict(label="Casos",
                            method="update",
                            args=[{"visible": [True, False]},
                                {"title": "# casos acumulado para cada CA"}]),
                        dict(label="Fallecidos",
                            method="update",
                            args=[{"visible": [False, True]},
                                {"title": "# de fallecidos acumulado para cada CA"}]),
                    ]),
                    direction="left",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.4,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ])
        fig.update_layout(showlegend=False, width=1600, height=1200, title='# casos acumulado para cada CA')
        st.plotly_chart(fig)

        st.subheader('Evolución de hospitalizados y en UCI')
        fig = make_subplots(rows=rows, cols=cols, vertical_spacing=0.05, subplot_titles=ccaa['ccaa'].unique())
        i, j = 1, 1
        for ca in ccaa['ccaa'].unique():
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['hospitalizated'], fill='tonexty', name='Hospitalizados', line_color='darkcyan'), row=i, col=j)
            fig.add_trace(go.Scatter(x=ccaa.loc[ccaa['ccaa']==ca]['fecha'], y=ccaa.loc[ccaa['ccaa']==ca]['UCI'], visible=False, fill='tonexty', name='UCI', line_color='darkcyan'), row=i, col=j)
            j+=1
            if j>cols:
                i+=1
                j=1
        fig.update_layout(showlegend=False, width=1600, height=1200, title='# de hospitalizados diarios para cada CA')
        fig.update_layout(
            updatemenus=[
                dict(
                    active=0,
                    type='buttons',
                    bgcolor='LightSteelBlue',
                    buttons=list([
                        dict(label="Hospitalizados",
                            method="update",
                            args=[{"visible": [True, False]},
                                {"title": "# de hospitalizados diarios para cada CA"}]),
                        dict(label="UCI",
                            method="update",
                            args=[{"visible": [False, True]},
                                {"title": "# de ingresados en UCI diario para cada CA"}]),
                    ]),
                    direction="left",
                    pad={"r": 10, "t": 10},
                    showactive=True,
                    x=0.4,
                    xanchor="left",
                    y=1.1,
                    yanchor="top"
                )
            ])
        st.plotly_chart(fig)

if __name__ == "__main__":
    write()