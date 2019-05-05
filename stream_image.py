# -*- coding: utf-8 -*-
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import pandas as pd
from PIL import Image
import numpy as np
import json

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
    red = Image.open('rededge_red.jpg')
    green = Image.open('rededge_green.jpg')
    blue = Image.open('rededge_blue.jpg')
    nir = Image.open('rededge_nir.jpg')
    
    # Resize image
    width,height = red.size   # Find size of image

    # Offsets, order is blue, green, red, nir
    # These are good offsets for 2m away
    xOffset = [32,10,34,45]   # +ve moves image to right
    yOffset = [0,8,32,25]    # +ve moves image down
    base = [200,200]

    red_crop = red.crop((base[0]-xOffset[2],
                         base[1]-yOffset[2],
                         width-xOffset[2],
                         height-yOffset[2]))

    green_crop = green.crop((base[0]-xOffset[1],
                             base[1]-yOffset[1],
                             width-xOffset[1],
                             height-yOffset[1]))

    blue_crop = blue.crop((base[0]-xOffset[0],
                           base[1]-yOffset[0],
                           width-xOffset[0],
                           height-yOffset[0]))

    nir_crop = nir.crop((base[0]-xOffset[3],
                         base[1]-yOffset[3],
                         width-xOffset[3],
                         height-yOffset[3]))
    
    # Normalise red and nir
    red_np = np.asarray(red_crop).astype(float)
    nir_np = np.asarray(nir_crop).astype(float)
    
    # Calculate the NDVI
    ndvi = (nir_np - red_np) / (nir_np+red_np)
    
    return pd.DataFrame(ndvi).to_json(date_format='iso', orient='split')



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
