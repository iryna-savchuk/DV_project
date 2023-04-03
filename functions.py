import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sb
import plotly.graph_objects as go

import geojson
import country_converter as coco # to convert and match country names

path = 'data/'


def get_data_geo(): # not used
    with open('data/countries.geojson') as f:
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