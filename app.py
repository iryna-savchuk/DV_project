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
x = df['prizeAge']
hist_data = dict(type='histogram', x=x, marker=dict(color='silver'))
layout = dict(title=dict(text='Ages Distribution'))
fig_1 = go.Figure(data=hist_data, layout=layout)



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


app.layout =  html.Div([

    # Header DIV
     html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("Nova_IMS.png"),
                            id="novaims-image",
                            style={
                                "height": "70px",
                                "width": "auto",
                                "margin-bottom": "20px",
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
                                    "Nobel Prize winners (1901-2022)",
                                    style={"font-weight": "bold"},
                                ),
                                html.H5(
                                    "Exploring historical data on the world’s most coveted award", style={"margin-top": "0px"}
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
                                "height": "70px",
                                "width": "auto",
                                "margin-bottom": "20px",
                                "float": "right"
                            },
                        )
                    ],
                    className="one-third column",
                ),
            ],
            
            id="header",
            className="row flex-display",
            style={"margin-bottom": "20px"},
        ), # Header Div --end


    # Main body DIV
    html.Div([

        html.Div(
            [
                html.H6("General health information about the countries", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                html.P("Similarly to nutrition, the health status also varies from country to country. The bar chart below shows the differences between the countries in terms of the following variables: prevalence of obesity in the adult population in % (Obesity), prevalence of diabetes in the adult population in % (Diabetes Prevalence), cardiovascular death rate per 100,000 population (Cardiovascular Death Rate), average life expectancy in years (Life Expectancy) and the expenditure of the government on the country's health system in % of the respective GDP (Health Expenditure).", className="control_label",style={"text-align": "justify"}),
                
                html.Div([dcc.Graph(id="bar_chart_category", figure=fig_1)],className="pretty_container twelve columns"),
            ],
            className="row pretty_container",
        ),

        html.Div([
            html.H1(children='Nobel Prizes Dashboard'),
            html.Label('We are interested in investigating the historucal data on Nobel Prizes laureates.', 
                        style={'color':'rgb(33 36 35)'}), 
            html.Img(src=app.get_asset_url('Nobel_Prize.png'), style={'position': 'relative'}),
            ]
        ),

        html.Div(children=[
            html.H1(children='Nobel Prizes Dashboard'),

            html.Div(children='''Map'''),

            dcc.Graph(
                id='choropleth-graph',
                figure=fig_choropleth
            )
        ])
    ]), # Main Body Div --end


    # Footer Div: Sources and Authors
    html.Div([ 
        # Sources pretty container
        html.Div(
                [
                    html.H6("Sources", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                    dcc.Markdown(
                        """\
                            - Inspiration: https://www.nobelprize.org/prizes/
                            - Nobelprize API reference that was used to get the data: https://nobelprize.readme.io/reference/getting-started
                            - Kaggle dataset that was used for additional info: https://www.kaggle.com/datasets/imdevskp/nobel-prize
                            - pyCirclize tool to create chord diagram graphs: https://moshi4.github.io/pyCirclize/chord_diagram/
                            """
                    ,style={"font-size":"10pt"}),
                    
                ],
                className="row pretty_container",
            ),

        # Authors pretty container
        html.Div(
                [
                    html.H6("Authors", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                    html.P("Cátia Sofia Pereira Parrinha (m20201320@novaims.unl.pt)  -  Iryna Savchuk (m20211310@novaims.unl.pt)  -  Gueu (????@novaims.unl.pt) ", 
                        style={"text-align": "center", "font-size":"10pt"}),
                ],
                className="row pretty_container",
            )
    ]) # Footer Div --end
]) # app layout Div --end


if __name__ == '__main__':
    app.run_server(debug=True) 