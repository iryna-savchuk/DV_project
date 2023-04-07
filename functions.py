import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sb
import plotly.graph_objects as go

import geojson
import country_converter as coco # to convert and match country names
from wordcloud import WordCloud, STOPWORDS

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


def split_long_label(label, limit=20, separator=' '):
    words = label.split(separator)
    lines = []
    current_line = ''
    for word in words:
        if len(current_line + word) <= limit:
            current_line += word + separator
        else:
            lines.append(current_line.strip())
            current_line = word + separator
    if current_line:
        lines.append(current_line.strip())
    return '<br>'.join(lines)