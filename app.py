import dash
from dash import dcc
from dash import html
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from functions import make_density_df, get_data_geo

# Dataset 'Processing'
path = 'data/'
df = pd.read_csv(path + 'merged.csv')
#df_emission_0 = df_emissions.loc[df_emissions['year']==2000]

###########################
#### Building Graphs ######
###########################

# Age 
"""
x = df['prizeAge']
hist_data = dict(type='histogram', x=x, marker=dict(color='silver'))
layout = dict(title=dict(text='Ages Distribution'))
fig_1 = go.Figure(data=hist_data, layout=layout)
fig_1.show(renderer='browser')
"""

# Choropleth
df_density = make_density_df(df)

data_choropleth = dict(type='choropleth',
                        locations=df_density['iso-a3'],
                        autocolorscale = False,
                        z=np.log(df_density['count']),
                        zmin=np.log(df_density['count'].min()),
                        zmax=np.log(df_density['count'].max()),
                        colorscale = ["#fcf2bf", "#ab8206"],   
                        marker_line_color = '#674e04',
                        colorbar=dict(title='Total Prizes(log)'),
                        text=df_density['name'],
                        hovertemplate='Country: %{text} <br>'+'Prizes (log): %{z} <br><extra></extra>'
                        )
                    
layout_choropleth = dict(geo=dict(projection={'type': 'natural earth'}, bgcolor= 'rgba(0,0,0,0)'))

fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)


###################
#### The APP ######
###################
app = dash.Dash(__name__)
server = app.server


app.layout = html.Div(children=[
    html.H1(children='Nobel Prizes Dashboard'),

    html.Div(children='''Map'''),

    dcc.Graph(
        id='choropleth-graph',
        figure=fig_choropleth
    )
])


app.layout =  html.Div([

    html.Div([
        html.H1(children='Nobel Prizes Dashboard'),
        html.Label('We are interested in investigating the historucal data on Nobel Prizes laureates.', 
                    style={'color':'rgb(33 36 35)'}), 
        html.Img(src=app.get_asset_url('Nobel_Prize.png'), style={'position': 'relative'}),
    ], className='side_bar'),

    html.Div(
        html.Label("Age"), 
    ),
    html.Div(
        html.Label("Map"), 
    )
])


app.layout =  html.Div([

     html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Nova_IMS.png"),
                            id="novaims-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Food consumption characteristics of the European Union",
                                    style={"font-weight": "bold"},
                                ),
                                html.H5(
                                    "Analysis of the relationship between nutritional patterns and \n the health status within the countries", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="three column",
                    id="title",
                ),

                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Nobel_Prize.png"),
                            id="nobel-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                                "float": "right"
                            },
                        )
                    ],
                    className="one-third column",
                ),
            ],
            
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),



    html.Div([
        html.H1(children='Nobel Prizes Dashboard'),
        html.Label('We are interested in investigating the historucal data on Nobel Prizes laureates.', 
                    style={'color':'rgb(33 36 35)'}), 
        html.Img(src=app.get_asset_url('Nobel_Prize.png'), style={'position': 'relative'}),
    ], className='side_bar'),

])


  


if __name__ == '__main__':
    app.run_server(debug=True)