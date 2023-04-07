import pandas as pd

from pycirclize import Circos
from pycirclize.parser import Matrix
import country_converter as coco


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



def create_cirle_assests(df, categories, default_category):
    for cat in categories:
        #print(cat)
        if cat==default_category:
            df_filtered = df.loc[(df['gender']!='org')]
        else:
            df_filtered = df.loc[(df['gender']!='org') & (df['category']==cat.lower())]

        # Creating matrix and circos image     
        matrix = create_circos_matrix(df_filtered)
        circos = Circos.initialize_from_matrix(
            matrix,
            space=3,
            cmap="YlOrBr",
            #ticks_interval=3,
            label_kws=dict(size=12, r=110),
            link_kws=dict(direction=1, ec="black", lw=0.5),
        )
        fig = circos.plotfig()

        # Storing image and returning path to image
        output_path = 'assets/'+cat+'.png'
        fig.savefig(output_path)       


# Dataset read
path = 'data/'
df = pd.read_csv(path + 'merged.csv')

# Make circos pictures for all categories
category_options = ['All categories', 'Physics', 'Chemistry', 'Medicine', 'Literature', 'Peace', 'Economics']
default_category = "All categories"

create_cirle_assests(df, category_options, default_category)