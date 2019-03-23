# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import pandas as pd
from PIL import Image
import numpy as np

# Streams an image and calculates live stats from the image
# Image data is shared across two callbacks

axis_fmt = dict(
                autorange=True,
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False
                )


app = dash.Dash(__name__)

app.index_string = '''
    <!DOCTYPE html>
    <html>
    <head>
    {%metas%}
    <title>{%title%}</title>
    {%favicon%}
    {%css%}
    </head>
    <body>
    {%app_entry%}
    <footer>
    {%config%}
    {%scripts%}
    </footer>
    <div><IMG src='./assets/grass.png' style='width:100%'></div>
    </body>
    </html>
    '''

app.layout = html.Div(children=
  [
    html.H1(children='Multispectral Imaging of Greeness',
            className="app-header--title",
            style={'text-align':'center'}),

        dcc.Graph(id='live-graph',
                  className='live-graph',
                  config={'displayModeBar': False}),
   
        html.Div(id='live-text',
                 className='live-text',
                 children='Average Greeness Index ='),

        # Hidden div inside the app that stores image data
        html.Div(id='image_data', style={'display': 'none'}),

        dcc.Interval(
            id='graph_update',
            interval=1*1000,
            n_intervals=0
        ),
])

@app.callback(Output('image_data', 'children'),
              [Input('graph_update', 'n_intervals')])

def update_image(n):
    image =  np.rot90(np.array(Image.open('image.png'))[:,:,1],2)

    return pd.DataFrame(image).to_json(date_format='iso', orient='split')



@app.callback(Output('live-graph', 'figure'),
              [Input('image_data', 'children')])

def update_image(image_json):
    image = pd.read_json(image_json, orient='split')

    data=go.Heatmap(
             z=image,
             colorscale='Viridis',
             reversescale=False,
             showscale=False)

    return {'data':[data],
            'layout':go.Layout(title='Image',
                               height=400, width=400,
                               xaxis=axis_fmt, yaxis=axis_fmt,
                               margin=go.layout.Margin(l=40, r=40, t=40, b=40))}


@app.callback(Output('live-text', 'children'),
              [Input('image_data', 'children')])

def update_text(image_json):
    image = pd.read_json(image_json, orient='split')

    return 'Average Greeness Index = ' + str(np.sum(image.values))

if __name__ == '__main__':
    app.run_server(debug=False)
