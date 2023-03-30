import dash
from dash import dcc, html, Input, Output
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

#### Age Histogram
data_hist_age = dict(type='histogram', 
                     x=df['prizeAge'], 
                     marker=dict(color='#a57a50'),
                     hovertemplate='Age when won Prize: %{x} <br>'+'Number od winners: %{y}<br><extra></extra>')

layout_hist_age = dict(title=dict(text='Ages Distribution'),
                   plot_bgcolor='#fcf2bf')

fig_hist_age = go.Figure(data=data_hist_age, layout=layout_hist_age)
fig_hist_age.update_yaxes(showline=True, linewidth=2, linecolor='#674e04', gridcolor='#a57a50')
fig_hist_age.update_xaxes(showline=True, linewidth=2, linecolor='#674e04')


#### Category Barchart
category_labels = df['category'].value_counts()
category_values = (category_labels / category_labels.sum()) * 100
unique_category = df['category'].unique()

data_bar_category = dict(type='bar',
                        x=unique_category,
                        y=category_values,
                        marker=dict(color=[ '#623f17', '#ab6400', '#eb993c',  '#a57a50', '#e4a76c','#877769', '#a58a89' ]),
                        hovertemplate='Category: %{x} <br>'+'Percentage: %{y}<br><extra></extra>'
                        )

layout_bar_category = dict(title=dict(text='Prizes by Category'), 
                           xaxis=dict(title='category'), 
                           yaxis=dict(title='Percentage'),
                           plot_bgcolor='#fcf2bf'
                  )

fig_bar_category = go.Figure(data=[data_bar_category], layout=layout_bar_category)


#### Choropleth
df_density = make_density_df(df)

data_choropleth = dict(type='choropleth',
                        locations=df_density['iso-a3'],
                        autocolorscale = False,
                        z=np.log(df_density['count']),
                        zmin=np.log(df_density['count'].min()),
                        zmax=np.log(df_density['count'].max()),
                        colorscale = ["#fcf2bf", "#ab6400"],   
                        marker_line_color = '#674e04',
                        colorbar=dict(title='Total Prizes(log)'),
                        text=df_density['name'],
                        hovertemplate='Country: %{text} <br>'+'Prizes (log): %{z} <br><extra></extra>',
                        )
                    
layout_choropleth = dict(geo=dict(projection={'type': 'natural earth'}, 
                         bgcolor= 'rgba(0,0,0,0)'))

fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)
fig_choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

##########################
#### The APP Layout ######
##########################
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
                html.H6("General Nobel Prize information", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                html.P("The Nobel Prize is an international award administered by the Nobel Foundation in Stockholm, Sweden, and based on the fortune of Alfred Nobel, Swedish inventor and entrepreneur. In 1968, Sveriges Riksbank established The Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel, founder of the Nobel Prize. Each prize consists of a medal, a personal diploma, and a cash award.", 
                    className="control_label",style={"text-align": "justify"}),
                html.P("A person or organisation awarded the Nobel Prize is called Nobel Prize laureate. The word “laureate” refers to being signified by the laurel wreath. In ancient Greece, laurel wreaths were awarded to victors as a sign of honour.", 
                    className="control_label",style={"text-align": "justify"}),
                html.Div([dcc.Graph(id="fig_hist_age", figure=fig_hist_age)], className="pretty_container five columns"),
                html.Div([dcc.Graph(id="fig_bar_category", figure=fig_bar_category)], className="pretty_container five columns"),
            ],
            className="row pretty_container",
        ),

        html.Div([
            html.H6("Nobel Prizes Distribution by Country", style={"margin-top": "0","font-weight": "bold","text-align": "center"}), 
            html.Div(
                [dcc.Graph( id='choropleth-graph', figure=fig_choropleth)],
                className="row pretty_container",
            ),
            html.Div(style={'margin-top': 50}), 
            dcc.RangeSlider(min=1900, max=2022, value=[1901, 2022], 
                            marks={ 1901: '1901', 1910: '1910', 1920: '1920',  1930: '1930',
                                    1940: '1940', 1950: '1950', 1960: '1960',  1970: '1970',
                                    1980: '1980', 1990: '1990', 2000: '2000',  2010: '2010',
                                    2020: '2020',},
                            tooltip={"always_visible": True}, 
                            id='my-range-slider'
                            ),
             html.Div(id='output-container-range-slider', style={'margin-top': 50})
            ],
            className="row pretty_container",
        ),
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


#####################
#### Callbacks ######
#####################
@app.callback(
    Output('output-container-range-slider', 'children'),
    [Input('my-range-slider', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)

if __name__ == '__main__':
    app.run_server(debug=True) 