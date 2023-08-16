from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd

#import action chains
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import numpy as np

import warnings

warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
#pd.options.mode.chained_assignment = None  # default='warn'


# multiline list
# THIS IS THE MAP THAT WE LOOK THROUGG
# INEFFICIENT BUT IT EASY
COLUMNS_TO_CHECK =  [
    (["køkken"], "køkken"),
    (["vaskemaskine"], "vaskemaskine"),
    (["parkering på gaden"], "gratis parkering på gaden"),
    (['tv', 'hdtv', 'streaming'], 'tv'),
    (['hårtørrer'], 'hårtørrer'),
    (['wi-fi', 'wifi', 'internet'], 'wi-fi'),
    (['røgalarm'], 'røgalarm'),
    (['kaffe', 'te'], 'kaffe'),
    (['håndklæder', 'håndklæde'], 'håndklæder'),
    (['sengetøj'], 'sengetøj'),
    (['udsigt'], 'udsigt'),
    (['pool'], 'pool'),
    (['familie', 'børn', 'baby', 'barn'], 'familie'),
    (['shampoo', 'balsam', 'showergel'], 'shampoo'),
    (['opvaskemasine'], 'opvaskemasine'),
    (['mikroovn'], 'mikroovn'),
    (['køleskab'], 'køleskab'),
    (['ting i nærheden'], 'ting i nærheden'),
    (['underholdning'], 'underholdning'),
    (['gratis'], 'gratis'),
]



def clean_airbnb_data(df, taylor_df, city_df):

    df_now = df[['Cities', 'Day_pre','location','price','rating']].copy()
    

    def price_split(x):
        if type(x) is int:
            return x

        if x is np.nan:
            return np.nan
        elif x == "'[]'":
            return np.nan

        else:
            if type(x) is not str:
                return x
            if len(x) < 3:
                return np.nan

            price = x.split(" ")[0]
            price = price.strip()
            price = price.replace(".", "")
            return int(price)

    #df_now['temp_price'] = df_now['price']
    df_now['price'] = df_now['price'].apply(price_split)

    #df_now.drop(columns=['temp_price'], inplace=True)


    def location_split(x):
        if x == "'[]'":
            return np.nan
        elif x == []:
            return np.nan
        elif type(x) is str:
            if len(x) < 3:
                return np.nan

        else:
            return x
        
    df_now['location'] = df_now['location'].apply(location_split)

    
    def rating_split(x):
        # if is nan not a string
        if type(x) is not str:
            return np.nan
        else:
            split = x.split(" · ")
            if len(split) > 1:
                return split[0].split(" ")[0].strip()
            else:
                return np.nan
    def omtaler_split(x):
        if type(x) is not str:
            return np.nan

        if x is np.nan:
            return x
        elif x == "'[]'":
            return x
        else:
            split = x.split(" · ")
            if len(split) > 1:
                return split[1].split(" ")[0].strip()
            else:
                return np.nan

    df_now['score'] = df_now['rating'].apply(rating_split)
    df_now['omtaler'] = df_now['rating'].apply(omtaler_split)

    # drop the rating column
    df_now.drop(columns=['rating'], inplace=True)

    df = df[df['price'].notna()]
    df = df[df['info'].notna()]

    # drop where price and info len is less than 10
    #df = df[df['price'].str.len() > 10]
    df = df[df['info'].str.len() > 10]

    df.reset_index(inplace=True)

    #df.reset_index(inplace=True)
    df_i = list(df.index)

    #df_now = df[['Cities', 'Day_pre','location','price','rating']].copy()

    for i in df_i:
        row = df.iloc[i]

        # if is nan
        if df.iloc[i]['info'] is np.nan:
            continue
        

        infos = df.iloc[i]['info'].split("||")
        #temp_dict = {}
        for info in infos:
            info_now = info.strip()
            # lower case
            info_now = info_now.lower()

            info_now = info_now.replace("· ", "")
            info_now = info_now.replace("·", "")
            
            if ('gæst' in info_now):
                for char in info_now:
                    if char.isdigit():
                        df_now.loc[i, 'gæster'] = int(char)

        if df.iloc[i]['features'] is np.nan:
            continue

        #continue
        infos = df.iloc[i]['features'].split("||")
        #print(infos)
        for map in COLUMNS_TO_CHECK:
            df.loc[map[1]] = 0

        for info in infos:
            info_now = info.strip()
            # lower case
            info_now = info_now.lower()
            #info_dict[info_now] = info_now[1]

            if "ikke tilgængelig" in info_now:
                continue
            elif "ikke inkluderet" in info_now:
                continue
            for map in COLUMNS_TO_CHECK:
                if info_now in map[0]:
                    df_now.loc[i, map[1]] = 1

   # replace "," with "." in om
    df_now['omtaler'] = df_now['omtaler'].str.replace(",", ".")
    # convert to float
    df_now['omtaler'].astype(float)

    df_now['score'] = df_now['score'].str.replace(",", ".")
    # convert to float
    df_now['score'].astype(float)

    # remove all columns with "Unnamed" in it
    df_now = df_now.loc[:, ~df_now.columns.str.contains('Unnamed')]

    

    # rename Day_pre to date
    df_now.rename(columns={'Day_pre': 'date', 'Cities': 'city', 'score': 'rating'}, inplace=True)

    cols = list(df_now.columns)
   
    # only keep columns Cities and treat in taylor_df
    taylor_df = taylor_df[['Cities', 'Treat']]

    # rename taylor_df "Cities" to "city"
    taylor_df.rename(columns={'Cities': 'city', 'Treat': 'treat'}, inplace=True)

    # merge with taylor_df on city
    df_now = pd.merge(df_now, taylor_df, on='city')

    # getting col names from city_df from col 1
    col_names_city = list(city_df.iloc[:, 1:].columns)
    # rename City to city
    city_df.rename(columns={'City': 'city'}, inplace=True)

    # merge city_df with df_now on city
    df_now = pd.merge(df_now, city_df, on='city')



    # put these columns first
    cols_first = ["city", "date", "treat"]
    # get the rest of the columns
    
    # remove the first 3 columns
    cols = cols[3:]
    # add the first 3 columns to the rest of the columns
    cols = cols_first + cols + col_names_city
    #print(cols)
    # set the columns
    df_now = df_now[cols]



    return df_now