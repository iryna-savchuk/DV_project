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
from functions import make_density_df, get_data_geo, plot_wordcloud, split_long_label

# Dataset read
path = 'data/'
df = pd.read_csv(path + 'merged.csv')

# Pre-defining the options for selection menus
category_options = ['All Categories', 'Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics']
default_category = "All Categories"
science_options = ['All Sciences', 'Physics', 'Chemistry', 'Medicine', 'Economics']
default_science = "All Sciences"

###########################
#### Building Graphs ######
###########################

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
                           path=['total', 'laureate', 'category'],  #path=['laureate', 'category'], 
                           values='size',
                           color = 'laureate',
                           color_discrete_map={'(?)':'', 'Individual':'#eb993c', 'Organisation':'#877769'},
                           #title="Laureate Types and Award Categories",
                          )

fig_sunburst.update_traces(hovertemplate="<b>%{label}:</b><br>%{value} Laureates<extra></extra>")
#fig_sunburst.update_traces(insidetextorientation='horizontal')
fig_sunburst.update_traces(leaf_opacity=0.6)
fig_sunburst.update_traces(textfont_size=14)
fig_sunburst.update_traces(textinfo="label+percent parent")
fig_sunburst.update_layout(margin={"r":5,"t":30,"l":5,"b":0})

fig_sunburst.update_layout(title={'text': 'Laureates and Categories', 
                                  'font': {'family':"Helvetica Neue", 'color':'black'},
                                   'y':0.95,
                                   'x':0.5,
                                   'xanchor': 'center',
                                   'yanchor': 'top'})

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

layout_scatter = dict(yaxis=dict(title='Category', gridwidth=2),
                      xaxis=dict(title='Year', gridwidth=2), 
                      plot_bgcolor='#fbe9d9')

fig_scatter = go.Figure(data=data_scatter, layout=layout_scatter)
fig_scatter.update_layout(margin={"r":20,"t":70,"l":35,"b":35})

fig_scatter.update_layout(title={'text': 'Awarded Categories by Year', 
                                  'font': {'family':"Helvetica Neue", 'color':'black'},
                                   'y':0.95,
                                   'x':0.5,
                                   'xanchor': 'center',
                                   'yanchor': 'top'})

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

fig_bar_gender = make_subplots(rows=1, cols=2, specs=[[{}, {}]], 
                               shared_yaxes=True, horizontal_spacing=0,
                               subplot_titles = ('Males', 'Females'))
  
# Adding Male data to the figure
fig_bar_gender.add_trace(go.Bar(y=year, x=male, 
                         name='Male', orientation='h',
                         marker=dict(color='#c66e00'),
                         hovertemplate='Year: %{y} <br>'+'Males: %{x} <br><extra></extra>',
                         ), 1, 1)

# Adding Female data to the figure
fig_bar_gender.add_trace(go.Bar(y=year, x=female,
                         name='Female', 
                         orientation='h',
                         marker=dict(color='#a58a89'),
                         hovertemplate='Year: %{y} <br>'+'Females: %{x} <br><extra></extra>',
                         ), 1, 2)
    
# Updating the layout for our graph
fig_bar_gender.update_layout(#title='Annual Number of Awarded Individuals, split by Gender',
                 title_x=0.5, title_y = 0,
                 barmode = 'overlay',
                 bargap = 0.2, bargroupgap = 0,
                 xaxis = dict(tickmode = 'array',
                              tickvals = [-14, -13, -12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1],
                              ticktext = [14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
                            ),
                xaxis2 = dict(range=[0, 14],
                              tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                              ticktext = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
                            ),

                yaxis=dict(#side='right',
                           tickvals = [1901, 1911, 1921, 1931, 1941, 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2021],
                           ticktext = [1901, 1911, 1921, 1931, 1941, 1951, 1961, 1971, 1981, 1991, 2001, 2011, 2021],
                           autorange="reversed"
                        ),
                plot_bgcolor='#fbe9d9',
                showlegend=False,
                )

fig_bar_gender.update_layout(margin={"r":20,"t":35,"l":20,"b":15})

# Create a horizontal highlight section
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

#=======================================
#======= Barchart - Universities ======= 
#=======================================

df['uni_full'] = df['name'] +', ' +df['country'] 
top = df['uni_full'].value_counts().head(10)
data = {'values': top.index[::-1], 'counts': top.values[::-1]}
df_top = pd.DataFrame(data)

# Splitting column into two columns based on comma separation
df_top[['University', 'Country']] = df_top['values'].str.split(',', expand=True)
df_top.drop('values', axis=1, inplace=True) # dropping the original column 

data_bar_uni = dict(type='bar',
                    x=df_top['counts'],
                    y=df_top['University'],
                    text=df_top['Country'],
                    orientation='h',
                    marker=dict(color=['#E3B166', '#D6A359', '#C8964D', '#BA8941', '#AC7D36', 
                                       '#9D7030', '#8F6529', '#805823', '#714B1C', '#623F17']),
                    hovertemplate='%{y}, %{text}<br>'+'Laureates: %{x}<br><extra></extra>',
                    )

layout_bar_uni = dict(#xaxis=dict(title='Number of Laureates'), 
                      #yaxis=dict(title='University'),
                      plot_bgcolor='#fbe9d9')

fig_bar_uni = go.Figure(data=[data_bar_uni], layout=layout_bar_uni)

fig_bar_uni.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


##########################
#### The APP Layout ######
##########################

app = dash.Dash(__name__)
server = app.server
app.title = "Nobel Prize Winners"

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
                    className="two columns bare_container", style={"float": "left"}
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "Nobel Prize Winners (1901-2022)",
                                    style={"font-weight": "bold"},
                                ),
                                html.H5(
                                    "Exploring historical data on the world’s most coveted award", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="sixish columns bare_container",
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
                                "float": "right",
                                #"margin-right":"-17.333333%"
                            },
                        )
                    ],
                    className="two columns bare_container", style={ "float": "right"}
                ),
            ],
            id="header",
            className="row",
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
                html.H6("General Nobel Prize Information", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                html.Div([dcc.Graph(id="fig_sunburst", figure=fig_sunburst)], className="pretty_container four columns"),
                
                html.Div([
                    html.Div(style={'margin-top': 20}),
                    dcc.Markdown("A person or organisation awarded the Nobel Prize is called Nobel Prize **laureate**. Between 1901 and 2022, 615 Nobel Prizes were awarded to 989 laureates."),
                    html.P("The Nobel Prize recognises the highest achievement in six categories: Medicine, Physics, Chemistry, Literature, Peace,  Economics"),
                    
                    html.Div(style={'margin-top': 20}),
                    html.Div([
                        html.P("Motivation for the Award", 
                                style={"font-weight": "bold","text-align": "center"}),
                        html.P("The cloud of words below outlines which words appear more frequently in the textual motivation for the Nobel Prize awards:"),
                        html.Div(style={'margin-top': 20}),
                        html.Div([html.Img(id="image_wordcloud", style={'position':'relative', 'width':'100%'})],
                                className="eight columns bare_container"),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id='radio_category_general',
                                    options= category_options,
                                    value=default_category,
                                    labelStyle={'display':'block'},
                                    ),
                            ],className="three columns bare_container"
                        ), 
                    ], className="mini_container twelve columns",),

                    ], className="container sixish columns"
                ),
                html.Div([dcc.Graph(id="fig_scatter", figure=fig_scatter)], 
                className="bare_container eleven columns"),
            ],
            className="row pretty_container",
        ),

        # Demographic information
        html.Div([
            html.H5("Demographic Information about Individual Laureates", style={"margin-top": "0","font-weight": "bold","text-align": "center"}), 
            # Gender Info Div
            html.Div([
                html.H6("Genders of the Nobel Prize Laureates", 
                        style={"margin-top": "0","text-align": "center"}),
                html.Div([dcc.Graph(id="fig_bar_gender", figure=fig_bar_gender)], 
                                    className ="eight columns pretty_container"),
                html.Div([
                    html.Div(style={'margin-top': 20}),
                    html.P("Insights on Gender Figures:", style={"font-weight":"bold"}),
                    html.P("- More than 90 percent of Nobel Prize winners have been men."),
                    html.P("- Last year, in 2022, two out of the fourteen Nobel laureates were women."),
                    html.P("- The graph illustrates annual number of the awarded individuals split by gender. As can be seen, the situation with gender disproportion becomes a bit better with the time."),
                    html.P("- One more thing is noticeable on the graph - the gap in the 1940-th. It turned out, during the Second World War, no Nobel Peace Prize was awarded.")
                    ], className ="three columns"),
                ],
                className ="twelve columns pretty_container"
            ),
  
            # Age Info Div
            html.Div([
                html.H6("Ages of the Nobel Prize Laureates", style={"margin-top":"50","text-align": "center"}),
                html.Div([
                    dcc.Graph(id="fig_hist_age")], className="eight columns pretty_container"       
                    ),
                ]),
                html.Div([
                    html.Div(style={'margin-top': 20}),
                    html.Div(
                        [   
                            html.P("Maximum Age",style={"text-align": "center","font-weight":"bold"}),
                            html.P(id="max_age",style={"text-align": "center"}),
                            html.P(id="max_name",style={"text-align": "center"}),
                            html.P(id="max_year",style={"text-align": "center"}),
                            html.P(id="max_category",style={"text-align": "center"}),
                        ],
                        className="mini_container",
                        id="max_age_container",
                    ),
                    html.Div(style={'margin-top': 30}),
                    html.Div(
                        [
                            html.P("Minimum Age",style={"text-align": "center","font-weight":"bold"}),
                            html.P(id="min_age",style={"text-align": "center"}),
                            html.P(id="min_name",style={"text-align": "center"}),
                            html.P(id="min_year",style={"text-align": "center"}),
                            html.P(id="min_category",style={"text-align": "center"}),
                        ],
                        className="mini_container",
                        id="min_age_container",
                    ),
                    ], className="three columns",
                ),
                html.Div([
                    html.P(),
                    #html.P("Select Research Category:", className="control_label",style={"text-align": "center","font-weight":"bold"}),
                    dcc.RadioItems(
                                id='radio_category',
                                options= category_options,
                                value=default_category,
                                labelStyle={'display': 'inline',}     
                            ),
                    ],
                    className="eight columns",
                    style={"text-align": "center"},
                ),
                #html.Div(style={'margin-top': 50}),
            ], className="row pretty_container"),

        # Geographical Distribution of Nobel Prizes Winners
        html.Div(
            [
                html.H6("Home Countries of Nobel Prizes Winners", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),     
                html.Div([
                    # Div containing choropleth graph
                    html.Div([
                        html.Div(
                            [dcc.Graph(id='choropleth-graph', figure=fig_choropleth)],
                            className="pretty_container",
                        ),
                        html.Div(style={'margin-top': 50}), 
                        dcc.RangeSlider(min=1901, max=2022, value=[1901, 2022], 
                                    marks={ 1901: '1901', 1910: '1910', 1920: '1920',  1930: '1930',
                                            1940: '1940', 1950: '1950', 1960: '1960',  1970: '1970',
                                            1980: '1980', 1990: '1990', 2000: '2000',  2010: '2010',
                                            2020: '2020',},
                                    tooltip={"always_visible": True}, 
                                    id='year-range-slider',
                                    #className ="eleven columns" 
                                    ),
                    ], className="nine columns",
                    ),

                    # Div containg selection options for Scale and Award Category
                    html.Div(
                        [   
                        html.Div([
                            html.P("Select Scale", className="control_label",style={"text-align":"left","font-weight":"bold"}),
                            dcc.RadioItems(id='scale-type',
                                options=[{'label': i, 'value': i} for i in ['Log Scale', 'Absolute Count']],
                                value='Log Scale',
                                labelStyle={'display':'block'},
                            ), 
                            ], className="mini_container two columns",
                        ),
                        html.Div([
                            html.P("Select Category", className="control_label",style={"text-align":"left","font-weight":"bold"}),
                            dcc.RadioItems(id='category-type',
                                options=category_options,
                                value=default_category,
                                labelStyle={'display':'block'},
                                ),
                            ], className="mini_container two columns",
                        ), 
                        ], #className="two columns bare_container", 
                    )
                ],className="row"),
            ],
            className="row pretty_container",
        ),

        # Schooling Section
        html.Div(
            [
                html.H6("Laureates' School Information", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                html.Div(
                    [
                    html.P("Top 10 Universities in the World", 
                            style={"font-weight": "bold", "text-align": "left", "margin-left": 70}),

                    html.Div([dcc.Graph(id="fig_bar_uni", figure=fig_bar_uni)], className="pretty_container"),
                    html.Div(style={'margin-top': 30}),
                    html.Div([
                        dcc.RadioItems(
                                    id='radio_science',
                                    options=[x for x in science_options],
                                    value=default_science,
                                    labelStyle={"display": "inline"}    
                                ),
                        ],
                        style={"text-align": "center"},
                    ),
                    html.Div(style={"margin-top": 30}),
                    ],className="bare_container eleven columns"),


                html.P("The Flow of Laureates to the US-based Schools", className="bare_container columns",
                       style={"font-weight": "bold", "text-align": "left", "margin-left": 100}), 

                html.Div(id="circle_US",   
                        style={
                                'width': '50%',  # set the width of the Div
                                'padding-bottom': '50%',  # set the height of the Div to be the same as the width (i.e., 1:1 aspect ratio)
                                'position': 'relative'  # set position to relative so that the child elements can be positioned absolutely
                            },
                        className="pretty_container five columns", 
                        ),

                html.Div([
                    html.Div(style={'margin-top': 20}),
                    html.P("Insights on Geographical Distribution:", style={"font-weight":"bold"}),
                    html.P(),
                    html.P("- Individuals who were born in the USA become the Nobel Prize Laureates more often than those who were born in other countries. \
                              (The exact total figures and figures for each nominated category, can be explored using the map above)."),
                    html.P(),
                    html.P("- The top performing universities in terms of winning the Nobel Prize for their research are also based in the USA. It is true throughout all the scientific categories of the Award: Physics, Chemistry, Medicine, and Economics."),
                    html.P(),
                    html.P("- The circular graph to the right outlines the proportion of individual Laureates who were born in different countries and received their Nobel Prize Award while schooling in the United States.\
                            As can be seen, there is a fair fraction of reserchers whose home country is not the USA, but they have done their discoveries in American institutions."),
                    ], className ="bare_container four columns"),
            ],
            className="row pretty_container",
        ),

    ]), # Main Body Div --end


    # Footer Div: References and Authors
    html.Div([ 
        # References pretty_container
        html.Div(
                [
                    html.H6("References", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                    dcc.Markdown(
                        """\
                            - Inspiration #1 - Infographic: Nobel Prize winners 1901-2021: https://www.aljazeera.com/news/2021/10/7/infographic-nobel-prize-winners-1901-2021
                            - Inspiration #2 - "Nobel Prizes: Is there a secret formula to winning one?": https://www.bbc.com/future/article/20121008-winning-formula-for-nobel-prizes
                            - The Nobel Prize official website: https://www.nobelprize.org/prizes/
                            - Nobelprize.org API reference used to get the data: https://nobelprize.readme.io/reference/getting-started
                            - Plotly open source graphing library for Python: https://plotly.com/python/
                            - Dashboard styling inspiration: https://dash.gallery/dash-food-consumption/
                            - Circular chord diagrams have been created with pyCirclize tool: https://moshi4.github.io/pyCirclize/chord_diagram/
                            """
                    ,style={"font-size":"10pt"}),                  
                ],
                className="row pretty_container",
            ),

        # Authors pretty_container
        html.Div(
                [
                    html.H6("Authors", style={"margin-top": "0","font-weight": "bold","text-align": "center"}),
                    html.P("Cátia Parrinha (m20201320@novaims.unl.pt)  -  Iryna Savchuk (m20211310@novaims.unl.pt)", 
                        style={"text-align": "center", "font-size":"10pt"}),
                ],
                className="row pretty_container",
            )
    ]) # Footer Div --end
]) # app layout Div --end


#####################
#### Callbacks ######
#####################

################################### 1. WorldCLoud callback #####################################
@app.callback(
    Output('image_wordcloud','src'),
    Input('radio_category_general','value')
)
def make_image(chosen_category):
    # Filter by chosen category
    if chosen_category==default_category:
        chosen_df = df.copy()
    else:
        chosen_df = df.loc[df['category']==chosen_category.lower()]  
    text = str(chosen_df['motivation'].values)
    img = BytesIO()
    plot_wordcloud(text).save(img, format='PNG')
    return 'data:image/png;base64,{}'.format(base64.b64encode(img.getvalue()).decode())

###################### 2. Histogram Calback: Age when prize awarded #######################
@app.callback(
    [
        Output('max_age','children'),
        Output('max_name','children'),
        Output('max_year','children'),
        Output('min_age','children'),
        Output('min_name','children'),
        Output('min_year','children'),
        Output('fig_hist_age','figure')
    ],
    [
        Input('radio_category','value'),
    ]
)
def get_ages(chosen_category):
    # Filter by chosen category
    if chosen_category==default_category:
        chosen_df = df.loc[(df['gender']!='org')]
    else:
        chosen_df = df.loc[(df['gender']!='org') & (df['category']==chosen_category.lower())]

    # Getting info about Max Age Individual Laureate
    id_max = chosen_df['prizeAge'].idxmax()
    max_age = chosen_df.loc[id_max,'prizeAge']
    max_name = chosen_df.loc[id_max,'firstname'] + ' ' + chosen_df.loc[id_max,'surname']
    max_year = chosen_df.loc[id_max,'year']
    max_category = str(chosen_df.loc[id_max,'category']).capitalize()

    # Getting info about Max Age Individual Laureate
    id_min = chosen_df['prizeAge'].idxmin()
    min_age = chosen_df.loc[id_min,'prizeAge']
    min_name = chosen_df.loc[id_min,'firstname'] + ' ' + chosen_df.loc[id_min,'surname']
    min_year = chosen_df.loc[id_min,'year']
    min_category = str(chosen_df.loc[id_min,'category']).capitalize()

    ######### Histogram: Age when prize awarded #########
    fig_hist_age = px.histogram(chosen_df, 
                            x='prizeAge', 
                            color='gender', 
                            marginal = 'box', # or violin, rug, box
                            nbins=90,
                            color_discrete_sequence=['#e4a76c', '#877769'])
    fig_hist_age.update_layout(
                           plot_bgcolor='rgba(0,0,0,0)',
                           xaxis_title="Age", 
                           yaxis_title="Number of Laureates",
                           margin={"r":0,"t":0,"l":0,"b":0},
                           legend_title_text = "",
                           legend=dict(x=1, y=0.5, itemclick='toggleothers'),
                           ) 
    fig_hist_age.update_traces(hovertemplate="<br>".join(["Age award received: %{x}","Number of Laureates: %{y}",]))
    fig_hist_age.update_layout(margin={"r":20,"t":50,"l":20,"b":20})

    return str(max_age)+" years old", str(max_name), "Year: " + str(max_year) +" ("+max_category+")",\
           str(min_age)+" years old", str(min_name), "Year: " + str(min_year) +" ("+min_category+")",\
           fig_hist_age


################################ 3. Choropleth Map Callback #####################################
@app.callback(
    Output('choropleth-graph', 'figure'),
    Input('scale-type', 'value'),
    Input('category-type', 'value'),
    [Input('year-range-slider', 'value')])

def update_colorpleth(radiovalue, radiovalue2, slidervalue):

    # Filtering years
    mask = (df['year'] >= slidervalue[0]) & (df['year'] <= slidervalue[1])  # including the chosen years
    df_chosen = df.loc[mask]

    # Filter by chosen category
    if radiovalue2==default_category:
        df_chosen = df_chosen.loc[(df['gender']!='org')]
    else:
        df_chosen = df_chosen.loc[(df['gender']!='org') & (df['category']==radiovalue2.lower())]

    # Generating dataframe for map
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


############################## 4. Universities Section Callback #####################################
@app.callback(
    Output('fig_bar_uni','figure'),
    Output('circle_US', 'children'),
    Input('radio_science','value')
)
def get_top_uni(chosen_science):
    # Filter by chosen category
    if chosen_science==default_science:
        df_chosen = df.loc[(df['gender']!='org')]
    else:
        df_chosen = df.loc[(df['gender']!='org') & (df['category']==chosen_science.lower())]

    df_chosen.loc[df_chosen['name'].isna(), :] = None #droping rows without university

    df_chosen.loc[:, 'uni_full'] = df_chosen['name'] + ',' + df_chosen['country'] 
    top = df_chosen['uni_full'].value_counts().head(10)
    data = {'values': top.index[::-1], 'counts': top.values[::-1]}
    df_top = pd.DataFrame(data)

    # Splitting column into two columns based on comma separation
    df_top[['University', 'Country']] = df_top['values'].str.split(',', expand=True)
    df_top.drop('values', axis=1, inplace=True) # dropping the original column 

    # Split long names of universities and add to new_labels list
    new_labels = []
    for label in df_top.loc[:,'University']:
        new_label = split_long_label(label, 40) #allowing labels to be no wider than 40 letters
        new_labels.append(new_label)

    data_bar_uni = dict(type='bar',
                        x=df_top['counts'],
                        y=new_labels, # edited df_top['University'],
                        text=df_top['Country'],
                        orientation='h',
                        marker=dict(color=['#E3B166', '#D6A359', '#C8964D', '#BA8941', '#AC7D36', 
                                        '#9D7030', '#8F6529', '#805823', '#714B1C', '#623F17']),
                        hovertemplate='%{y}, %{text}<br>'+'Laureates: %{x}<br><extra></extra>',
                        )

    layout_bar_uni = dict(#xaxis=dict(title='Number of Laureates'), 
                        plot_bgcolor='#fbe9d9')

    fig_bar_uni = go.Figure(data=[data_bar_uni], layout=layout_bar_uni)
    fig_bar_uni.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    file_name_US = chosen_science+'_US_.png'
    full_path = 'assets/{}'.format(file_name_US)

    # Creating a trace for the image
    image_trace = go.layout.Image(
        source=full_path,
        xref="x",
        yref="y",
        x=0,
        y=0,
        sizex=1,
        sizey=1,
        #sizing="stretch",
        opacity=1,
        layer="above"
    )

    # Creating a plot with the image trace
    fig_us = go.Figure()

    fig_us.update_layout(
        #width=100,
        #height=100,
        autosize=True,  # automatically adjust the size of the plot
        margin=dict(l=0, r=0, t=0, b=0),
        template='plotly_white',
        xaxis=dict(
            range=[0, 1], # set the x-axis range
            autorange=False, # disable auto-ranging for the x-axis
            showticklabels=False, # hide the x-axis tick labels
            showgrid=False # hide the x-axis grid
            ),
        yaxis=dict(
            range=[-1, 0], # set the y-axis range
            autorange=False, # disable auto-ranging for the y-axis
            showticklabels=False, # hide the y-axis tick labels
            showgrid=False # hide the y-axis grid
            ),
        images=[image_trace], # add image trace to layout
    )
    
    graph_style = {'position': 'absolute', 'top': 0, 'left': 0,
                    'width': '100%', 'height': '100%'}

    return fig_bar_uni, dcc.Graph(figure=fig_us, config={'displayModeBar': False}, style=graph_style) 


######################
#### SERVER RUN ######
######################
if __name__ == '__main__':
    app.run_server(debug=True) 
    