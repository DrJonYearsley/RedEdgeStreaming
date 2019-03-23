# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import plotly.graph_objs as go
import pandas as pd
from PIL import Image
import numpy as np

image = Image.open('image.png')
np_image = np.array(image)

red = np.rot90(np_image[:,:,0],2)
green = np.rot90(np_image[:,:,1],2)
blue = np.rot90(np_image[:,:,2],2)

ndvi = (red-blue) / (red+blue)

axis_fmt = dict(
                autorange=True,
                showgrid=False,
                zeroline=False,
                showline=False,
                ticks='',
                showticklabels=False
                )

def generate_image(img, label='Image',colorscale='Viridis',reversescale=False):
    return dcc.Graph(
                 id=label,
                 figure={
                     'data': [go.Heatmap(
                                         z=img,
                                         colorscale=colorscale,
                                         reversescale=reversescale,
                                         showscale=False),
                              ],
                     'layout': {
                         'title': label,
                         'height': 300,
                         'width':300,
                         'xaxis':axis_fmt,
                         'yaxis':axis_fmt,
                         'margin':go.layout.Margin(l=40, r=40, t=40, b=40)
                      }
                 },
                 config={
                     'displayModeBar': False
                 }
         )

app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Multispectral Data to Detect Plant Growth',
            className="app-header--title",
            style={'text-align':'center'}),

    html.Table(children=[
        html.Tr([
            html.Td([
                generate_image(red,
                               label='Red Band',
                               colorscale='Reds',
                               reversescale=False)
            ]),
            html.Td([
                generate_image(green,
                               label='Green Band',
                               colorscale='Greens',
                               reversescale=True)
            ]),
            html.Td([
                generate_image(ndvi,
                               label='NDVI',
                               colorscale='Viridis',
                               reversescale=True)
            ]),
        ])
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
