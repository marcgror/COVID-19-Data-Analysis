
from ipywidgets import widgets
import plotly.graph_objects as go
import plotly.express as px

def create_interactive_plot(df, ccaa_series, dates, traces, title_text):
    widget = widgets.Dropdown(
    options=ccaa_series.unique().tolist(),
    description='CCAA'
    )
    g = go.FigureWidget(layout=go.Layout(
                        title=dict(
                            text=title_text
                        ), legend=dict(orientation='h', bgcolor='LightSteelBlue'),
                        barmode='overlay'
                    ))
    for trace, trace_name in traces:
        g.add_trace(go.Bar(x=dates, y=df[trace], name=trace_name))

    def validate():
        if widget.value in ccaa_series.unique():
            return True
        else:
            return False

    def response(change):
        if validate():
            filter_list = [i for i in ccaa_series == widget.value]
            temp_df = df[filter_list]
            x = temp_df['fecha']
            i=0
        with g.batch_update():
            for trace, trace_name in traces:
                g.data[i].x = x
                g.data[i].y = temp_df[trace]
                i+=1
            g.layout.barmode = 'overlay'
            g.layout.xaxis.title = ''
            g.layout.yaxis.title = ''
    widget.observe(response, names='value')
    return widgets.VBox([widget, g])