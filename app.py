# Importing the necessary libraries and packages
import pandas as pd
import numpy as np

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from io import BytesIO
import base64

# Importing Custom functions
from functions import make_density_df, get_data_geo, plot_wordcloud

# Dataset read
path = 'data/'
df = pd.read_csv(path + 'merged.csv')

# Pre-defining the options for filtering menu in Map
category_options = ['All categories', 'Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics']

###########################
#### Building Graphs ######
###########################

#=======================================
#========== Age Histogram ==============
#=======================================

data_hist_age = dict(type='histogram', 
                     x=df['prizeAge'], 
                     marker=dict(color='#a57a50'),
                     hovertemplate='Age when won Prize: %{x} <br>'+'Number od winners: %{y}<br><extra></extra>')

layout_hist_age = dict(title=dict(text='Ages Distribution'),
                   plot_bgcolor='#fcf2bf')

fig_hist_age = go.Figure(data=data_hist_age, layout=layout_hist_age)
fig_hist_age.update_yaxes(showline=True, linewidth=2, linecolor='#674e04', gridcolor='#a57a50')
fig_hist_age.update_xaxes(showline=True, linewidth=2, linecolor='#674e04')

#=======================================
#======= Age by Gender Histogram ======= 
#=======================================

# Filter data by gender
male_data = df.loc[df['gender'] == 'male', 'prizeAge']
female_data = df.loc[df['gender'] == 'female', 'prizeAge']

# Create traces for each group
male_hist = go.Histogram(x=male_data, name='Male', marker=dict(color='#333F44'))
female_hist = go.Histogram(x=female_data, name='Female', marker=dict(color='#37AA9C'))
# Create layout
layout = go.Layout(title=dict(text='Ages Distribution by Gender'), 
                   paper_bgcolor='rgba(0,0,0,0)', 
                   plot_bgcolor='rgba(0,0,0,0)')
# Create figure 
fig_hist_age_by_gender = go.Figure(data=[male_hist, female_hist], layout=layout)

#=================================
#======= Category Barchart ======= 
#=================================

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

#===============================
#======= Sunburst Digram ======= 
#===============================

sunburst_df =  df.groupby(['category', 'gender'], as_index=False).size()
sunburst_df['total'] = str(df.shape[0]) + ' Laureates'
sunburst_df['laureate'] = sunburst_df['gender'].apply(lambda x: 'Organisation' if x=='org' else 'Individual')
sunburst_df['category'] = sunburst_df['category'].apply(lambda x: x.capitalize())

fig_sunburst = px.sunburst(sunburst_df, 
                           path=['total', 'laureate', 'category'],  
                           #path=['laureate', 'category'], 
                           values='size',
                           color = 'laureate',
                           color_discrete_map={'(?)':'', 'Individual':'#eb993c', 'Organisation':'#877769'},
                           #title="Laureate Types and Award Categories",
                          )

fig_sunburst.update_traces(hovertemplate="<b>%{label}:</b><br>%{value} Laureates<extra></extra>")
#fig_sunburst.update_traces(insidetextorientation='horizontal')
#fig_sunburst.update_traces(insidetextfont_size=14)
fig_sunburst.update_traces(leaf_opacity=0.6)
fig_sunburst.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig_sunburst.update_traces(textfont_size=14)

#===============================================
#======= Scatter plot - Category by Year ======= 
#===============================================

x = df['year']
y = df['category'].str.capitalize()
size = df.shape[0]*[6]

color_dict={'Physics':'#623f17', 'Chemistry':'#ab6400', 'Medicine':'#eb993c', 
            'Literature':'#6cb436', 'Peace':'#6a93c9', 'Economics': '#c32794'}  
color = [color_dict[i] for i in y]

data_scatter = dict(type='scatter', x=x, y=y,
                    marker_color=color,
                    marker_opacity=1,
                    mode='markers',
                    marker=dict(size=size),
                    hovertemplate="Category: %{y}<br>Year: %{x}<br><extra></extra>" ,
                    showlegend=False)

layout_scatter = dict(title=dict(text='Awarded Categories by Year'), 
                      yaxis=dict(title='Category', gridwidth=2),
                      xaxis=dict(title='Year', gridwidth=2), #, tickvals= [i for i in range(1900, 2025, 10)]),
                      plot_bgcolor='#fbe9d9')

fig_scatter = go.Figure(data=data_scatter, layout=layout_scatter)

#========================================
#======= Barchart: Gender by Year ======= 
#========================================

df['count'] = 1
df['total'] = len(df['count'])

pivot_table = pd.pivot_table(df, values='count', index='year', columns='gender', aggfunc='count', fill_value = 0)
df_gender_year = pivot_table.reset_index()

# Set the columns we want to our plot
year = df_gender_year['year']
female = df_gender_year['female']
male = df_gender_year['male']*(-1)

# Creating instance of the figure
#fig_bar_gender = go.Figure()
fig_bar_gender = make_subplots(rows=1, cols=2, specs=[[{}, {}]], 
                               shared_yaxes=True, horizontal_spacing=0.05,
                               )
  
# Adding Male data to the figure
fig_bar_gender.add_trace(go.Bar(y=year, x=male, 
                         name='Male', orientation='h',
                         marker=dict(color='#83531b'),
                         hovertemplate='Year: %{y} <br>'+'Males: %{x} <br><extra></extra>',
                         ), 1, 1)

# Adding Female data to the figure
fig_bar_gender.add_trace(go.Bar(y=year, x=female,
                        name='Female', orientation='h',
                        marker=dict(color='#cb7e1f'),
                        hovertemplate='Year: %{y} <br>'+'Females: %{x} <br><extra></extra>',
                        ), 1, 2)
    
# Updating the layout for our graph
fig_bar_gender.update_layout(title = 'Gender by Year',
                 title_font_size = 22, barmode = 'overlay',
                 bargap = 0.1, bargroupgap = 0,
                 xaxis = dict(tickmode = 'array',
                              tickvals = [-14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1],
                                          #0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                              ticktext = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                                          #0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                              title = 'Male',
                              title_font_size = 15),
                xaxis2 = dict(range=[0, 14],
                              tickvals = [#-14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1,
                                          1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                              ticktext = [#14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1,
                                          1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                              title = 'Female',
                              title_font_size = 15),

                yaxis=dict(side='right',
                           tickvals = [1901, 1911, 1921, 1931, 1941, 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2021],
                           ticktext = [1901, 1911, 1921, 1931, 1941, 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2021],
                           autorange="reversed"
                        ),

                plot_bgcolor='#fbe9d9'
                )

# Make a horizontal highlight section
fig_bar_gender.add_hrect(y0=1939, y1=1945, row=1, col=1,
                fillcolor="Grey", opacity=0.25)

fig_bar_gender.add_hrect(y0=1939, y1=1945, row=1, col=2,
                annotation_text="II World War", annotation_position='right',  
                annotation_font_size=12,
                annotation_font_color="Black",
                fillcolor="Grey", opacity=0.25)

#==============================
#======= Choropleth Map ======= 
#==============================
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
fig_choropleth.update_geos(showcoastlines=False)


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
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "20px",
                                "float": "left",
                                "margin-left":"-17.333333%"
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
                html.P("The Nobel Prize is an international award administered by the Nobel Foundation in Stockholm, Sweden, and based on the fortune of Alfred Nobel, Swedish inventor and entrepreneur. In 1968, Sveriges Riksbank established The Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel. Each prize consists of a medal, a personal diploma, and a cash award.", 
                    className="control_label",style={"text-align": "justify"}),
            ],
            className="row pretty_container",
        ),


        #General Nobel Prize information
        html.Div(
            [
                html.H6("General Nobel Prize information", style={"margin-top": "0","font-weight": "bold","text-align": "center"}), 
                html.Div([dcc.Graph(id="fig_sunburst", figure=fig_sunburst)], className="sixish columns pretty_container"),
                html.Div([
                    dcc.Markdown("A person or organisation awarded the Nobel Prize is called Nobel Prize **laureate**. Between 1901 and 2022, 615 Nobel Prizes were awarded to 989 laureates."),
                    html.P("The Nobel Prize recognises the highest achievement in 6 categories: Medicine, Physics, Chemistry, Literature, Peace,  Economics"),
                    ], className="fivish columns pretty_container"),
                html.Div([html.Img(id="image_wordcloud", className="fivish columns pretty_container")]),
                html.Div([dcc.Graph(id="fig_scatter", figure=fig_scatter)], className="eleven columns pretty_container"),
            ],
            className="row pretty_container",
        ),
        #html.Div(style={'margin-top': 50}), 


       html.Div(
            [
                html.H6("Huge Gender Gap", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),          
                html.Div([
                    html.P("Some text here, some more text, more text, more text, even more more more text.\
                            Some text here, some more text, more text, more text, even more more more text.\
                            Some text here, some more text, more text, more text, even more more more text.\
                            Some text here, some more text, more text, more text, even more more more text."),
                    ],
                    className="two columns"
                ),
                html.Div([dcc.Graph(id="fig_bar_gender", figure=fig_bar_gender)], className="nine columns"),
            ],
            className="row pretty_container",
        ),

        # "Nobel Prizes Distribution by Country"
        html.Div(
            [
                html.H6("Nobel Prizes Distribution by Country", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),     
                html.Div(style={'margin-top': 30}), 

                html.Div([
                    # Div contining choropleth graph
                    html.Div(
                        [dcc.Graph(id='choropleth-graph', figure=fig_choropleth)],
                        className="no_border_container nine columns",
                    ),

                    # Div containg selection options
                    html.Div(
                        [
                        html.Div([
                            html.P("Select Gender", className="control_label", style={"font-weight": "bold", "text-align": "left"}),
                            dcc.Dropdown(
                                id="chosen-gender",
                                options=[{"label": i, "value": i} for i in ['Male', 'Female', 'Both']],
                                value="Both")
                            ], className="container twelve columns"
                        ),

                        #html.Div(style={'margin-top': 100}),

                        html.Div([
                            html.P("Select Category", className="control_label", style={"font-weight": "bold", "text-align": "left"}),
                            dcc.Dropdown(
                                id="chosen-category",
                                options=[{"label": i, "value": i} for i in category_options],
                                value="All categories")
                            ], className="container twelve columns",  style={'margin-top': 100}
                        ),

                        html.Div([dcc.RadioItems(id='scale-type',
                                    options=[{'label': i, 'value': i} for i in ['Log Scale', 'Absolute Count']],
                                    value='Log Scale',
                                    #labelStyle={'display': 'inline-block'}, #,className="pretty_container four columns",
                                    style={"float": "right"})
                                    ], 
                                className="container twelve columns",
                                style={'margin-top': 100}
                                #style={'display': 'flex', 'vertical-align':'bottom'}
                        ),    

                        ], className="pretty_container two columns", 
                    )
                ],className="row"),

                html.Div(style={'margin-top': 50}), 

                dcc.RangeSlider(min=1901, max=2022, value=[1901, 2022], 
                                marks={ 1901: '1901', 1910: '1910', 1920: '1920',  1930: '1930',
                                        1940: '1940', 1950: '1950', 1960: '1960',  1970: '1970',
                                        1980: '1980', 1990: '1990', 2000: '2000',  2010: '2010',
                                        2020: '2020',},
                                tooltip={"always_visible": True}, 
                                id='my-range-slider'
                                ),

                html.Div(id='output-container-range-slider', style={'margin-top': 50}) # for debugging
            ],
            className="row pretty_container",
        ),

        html.Div(
            [
                html.H6("DRAFT General Nobel Prize information", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                html.P("The Nobel Prize is an international award administered by the Nobel Foundation in Stockholm, Sweden, and based on the fortune of Alfred Nobel, Swedish inventor and entrepreneur. In 1968, Sveriges Riksbank established The Sveriges Riksbank Prize in Economic Sciences in Memory of Alfred Nobel, founder of the Nobel Prize. Each prize consists of a medal, a personal diploma, and a cash award.", 
                    className="control_label",style={"text-align": "justify"}),
                html.P("A person or organisation awarded the Nobel Prize is called Nobel Prize laureate. The word “laureate” refers to being signified by the laurel wreath. In ancient Greece, laurel wreaths were awarded to victors as a sign of honour.", 
                    className="control_label",style={"text-align": "justify"}),
                html.Div([dcc.Graph(id="fig_hist_age", figure=fig_hist_age)], className="pretty_container five columns"),
                html.Div([dcc.Graph(id="fig_bar_category", figure=fig_bar_category)], className="pretty_container five columns"),
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
                            - Inspiration #1 - "Nobel Prizes: Is there a secret formula to winning one?": https://www.bbc.com/future/article/20121008-winning-formula-for-nobel-prizes
                            - Inspiration #2 - Infographic: Nobel Prize winners 1901-2021: https://www.aljazeera.com/news/2021/10/7/infographic-nobel-prize-winners-1901-2021
                            - Official website: https://www.nobelprize.org/prizes/
                            - Nobelprize.org API reference that was used to get the data: https://nobelprize.readme.io/reference/getting-started
                            """
                    ,style={"font-size":"10pt"}),                  
                ],
                className="row pretty_container",
            ),

        # Authors pretty container
        html.Div(
                [
                    html.H6("Authors", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                    html.P("Cátia Parrinha (m20201320@novaims.unl.pt)  -  Iryna Savchuk (m20211310@novaims.unl.pt)  -  Gueu (????@novaims.unl.pt) ", 
                        style={"text-align": "center", "font-size":"10pt"}),
                ],
                className="row pretty_container",
            )
    ]) # Footer Div --end
]) # app layout Div --end


#####################
#### Callbacks ######
#####################

################################### 1. choropleth callback #####################################
@app.callback(
    Output('choropleth-graph', 'figure'),
    Input('scale-type', 'value'),
    [Input('my-range-slider', 'value')])

def update_colorpleth(radiovalue, slidervalue):

    # Filtering years and generating new df_density
    mask = (df['year'] >= slidervalue[0]) & (df['year'] <= slidervalue[1])  # including the chosen years
    df_chosen = df.loc[mask]
    df_density = make_density_df(df_chosen)
    
    # Updating values that depend on Scale chosen by user
    if radiovalue=="Log Scale":
        z = np.log(df_density['count'])
        for_hover_string = ' (log)'
        zmin=np.log(df_density['count'].min())
        zmax=np.log(df_density['count'].max())
    else:
        z = df_density['count']
        for_hover_string = ''
        zmin=df_density['count'].min()
        zmax=df_density['count'].max()

    # Cenerating a new Cholorpleth
    data_choropleth = dict(type='choropleth',
                            locations=df_density['iso-a3'],
                            autocolorscale = False,
                            z=z,
                            zmin=zmin,
                            zmax=zmax,
                            colorscale = ["#fcf2bf", "#ab6400"],   
                            marker_line_color = '#674e04',
                            colorbar=dict(title='Total Prizes'+for_hover_string),
                            text=df_density['name'],
                            hovertemplate='Country: %{text} <br>'+'Prizes'+ for_hover_string+': %{z} <br><extra></extra>',
                            )
                        
    layout_choropleth = dict(geo=dict(projection={'type': 'natural earth'}, 
                            bgcolor= 'rgba(0,0,0,0)'))

    fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)
    fig_choropleth.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig_choropleth.update_geos(showcoastlines=False)
    return fig_choropleth 


################################### 2. WorldCLoud callback #####################################
@app.callback(
    Output('image_wordcloud', 'src'), 
    [Input('image_wordcloud', 'id')])
def make_image(b):
    text = str(df['motivation'].values)
    img = BytesIO()
    plot_wordcloud(text).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())


# Helpful for debugging (delete when the app is ready)
""" 
@app.callback(
    Output('output-container', 'children'),
    [Input('my-range-slider', 'value')])
def update_output(value):
    return 'You have selected "{}"'.format(value)
"""


######################
#### SERVER RUN ######
######################
if __name__ == '__main__':
    app.run_server(debug=True) 
    