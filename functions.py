import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sb
import plotly.graph_objects as go

import geojson
import country_converter as coco # to convert and match country names
from wordcloud import WordCloud, STOPWORDS

from pycirclize import Circos
from pycirclize.parser import Matrix
import country_converter as coco
from plotly.tools import mpl_to_plotly

path = 'data/'


def get_data_geo(): # not used
    with open(path+'countries.geojson') as f:
        data_geo = geojson.load(f)
    # In order to feed the GeoJson into Plotly,
    # Adding the 'id' key to each feature containing the value of each countries ISO-A3 code 
    for feature in data_geo['features']:
        feature['id'] = feature['properties']['ISO_A3'] 
    
    return data_geo


def make_density_df(df):
    # Grouping the dataset by country and counting cases
    df_by_country = df[['id', 'bornCountryCode']].groupby('bornCountryCode').count().rename(columns={"id": "count"})

    df_country_points = pd.read_csv(path+'country_points.csv')
    df_country = df_country_points.rename(columns={'country' : 'iso-a2'})

    df_density = pd.merge(df_country, df_by_country, left_on='iso-a2', right_on='bornCountryCode')
    df_density.sort_values(by=['count'], inplace=True)

    cc = coco.CountryConverter()
    df_density['iso-a3'] = cc.convert(df_density['iso-a2'], to='ISO3')
    
    return df_density


def plot_wordcloud(text):
    stopwords = set(STOPWORDS)
    wc = WordCloud(stopwords=stopwords,
                   background_color='white', colormap='copper').generate(text) #width=480, height=360
    return wc.to_image()


# Supplimentary function to create 'from-to' dataframe & convert it to matrix
# Input: df of Nobel Prizes
# Return: Matrix

def create_circos_matrix(df):
  fromto_table = []
  
  for index, row in df.iterrows():
    # We will compare the country of birth and the country of university
    bornCountryCode = row['bornCountryCode']
    country = row['country']

    if country!=country: # if 'country' is nan, we assume the person didn't go to other country for the reseach 
      fromto_table.append([bornCountryCode, bornCountryCode]) 
    elif country=='Germany (now France)': # the person from 'Germany (now France)' didn't go to other country for the reseach
      fromto_table.append([bornCountryCode, 'Germany'])   
    else:
      fromto_table.append([bornCountryCode, country])

  # Counting number of "from - to" pairs 
  fromto_table_df = pd.Series(fromto_table).value_counts()
  fromto_table_df = fromto_table_df.reset_index(name='number_of_cases').rename(columns = {'index':'from_to'})
  fromto_table_df[['from','to']] = pd.DataFrame(fromto_table_df.from_to.tolist())

  # Converting destination country to the same format as the country origin
  cc = coco.CountryConverter()
  fromto_table_df['to'] = cc.convert(fromto_table_df['to'], to='ISO2')

  # Keeping only 3 columns and in specific order: 'from', 'to', 'number_of_cases'
  fromto_table_df.drop(columns=['from_to'], inplace=True)
  fromto_table_df = fromto_table_df[['from', 'to', 'number_of_cases']]

  if fromto_table_df.shape[0]>100:
    matrix = Matrix.parse_fromto_table(fromto_table_df[fromto_table_df['number_of_cases']>1])
  else:
    matrix = Matrix.parse_fromto_table(fromto_table_df) 
  return matrix


def plot_country_circle(df):
    matrix = create_circos_matrix(df)
    circos = Circos.initialize_from_matrix(
        matrix,
        space=3,
        cmap="viridis",
        #ticks_interval=3,
        label_kws=dict(size=12, r=110),
        link_kws=dict(direction=1, ec="black", lw=0.5),
    )
    fig = circos.plotfig()
    plotly_fig = mpl_to_plotly(fig)
    return fig