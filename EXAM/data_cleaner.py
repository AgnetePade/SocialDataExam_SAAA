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
pd.options.mode.chained_assignment = None  # default='warn'


# multiline list
# THIS IS THE MAP THAT WE LOOK THROUGG
# INEFFICIENT BUT IT EASY
COLUMNS_TO_CHECK =  [
    (["køkken"], "køkken"),
    (["vaskemaskine"], "vaskemaskine"),
    (["parkering på gaden"], "gratis parkering på gaden"),
    (['tv', 'hdtv', 'streaming'], 'tv'),
    (['hårtørrer'], 'hårtørrer'),
    (['aircondition'], 'aircondition'),
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

COLUMNS_TO_CHECK = [
    (['vaskemaskine','gratis tørretumbler', 'gratis tørretumbler .1', 'tørretumbler'], 'washing machine'),
    (['en pejs i boligen', 'pejs'], 'fireplace'),
    (['32" hdtv med netflix', '32" tv med alm. kabel-tv', '32" hdtv med stor tv','underholdning', '49" hdtv med alm. kabel-tv', 'tv med alm. kabel-tv', 'hdtv med amazon prime', 'bose-stereoanlæg med bluetooth', 'billardbord', 'pejs', 'pladespiller', 'klaver', '32" hdtv med netflix', '32" tv med alm. kabel-tv', '55" hdtv med netflix', '32"-fjernsyn', '32" hdtv med stor tv','tv', 'hdtv', 'streaming','tv', 'tv med alm. kabel-tv', 'hdtv med amazon prime', 'tv med alm. kabel-tv', 'lydanlæg','sjov og leg', 'bordtennis', 'bordtennisbord'], 'entertainment'),
    (['hårtørrer'], 'hair dryer'),
    (['wi-fi', 'wifi', 'internet', 'trådløst internet','internet','wi-fi – 33 mbps*14', 'wi-fi – 14 mbps', 'wi-fi – 8 mbps', 'hurtig wi-fi – 439 mbps', 'wi-fi – 14 mbps', 'wi-fi – 8 mbps', 'bekræftet'], 'wi-fi'),
    (['røgalarm', 'kuliltealarm'], 'security'),
    (['håndklæder', 'håndklæde', 'basisting', 'håndklæder'], 'towels'),
    (['sengetøj', 'sengetøj', 'sengetøj i ','håndklæder, sengetøj', 'håndklæder, sengetøj' 'ekstra puder og dyner', 'sengetøj*9', 'sengetøj', 'sengetøj i .1', 'sengetøj', 'sengetøj i .2', 'sengetøj', 'sengetøj i .3','ekstra puder og dyne'], 'bed linen'),
    (['udsigt', 'bjergudsigt', 'udsigt til bjerge','flodudsigt', 'udsigt til flod','byudsigt', 'udsigt over byen','haveudsigt', 'pooludsigt', 'udsigt til pool','udsigt til have','naturskøn udsigt', 'udsigt over gården', 'udsigt til bjerge', 'udsigt over dalen', 'udsigt over byens skyline', 'haveudsigt','udsigt', 'udsigt','udsigt','naturskøn udsigt', 'haveudsigt','havudsigt', 'vandudsigt', 'ocean view','søudsigt', 'udsigt til sø'], 'view'),
    (['pool', 'swimmingpool','privat udendørs pool','fælles pool', 'fælles pool', 'fælles pool – sæsonå', 'fælles pool – sæsonå','boblebad', 'spabad','sauna', 'fælles sauna', 'privat sauna', 'badstue'], 'pool etc.'),
    (['familie', 'børn', 'baby', 'barn', 'børnebøger og legetøj', 'service og bestik til børn', 'høj stol', 'babybadekar', 'puslebord', 'vugge', 'pack \'n play / rejse', 'vugge – til rådighed', 'babybadekar – til rådighed', 'puslebord – til rådighed', 'anbefalinger af babyudstyr'], 'family'),
    (['shampoo', 'showergel', 'bodyshampoo','schauma-bodyshampoo','shampoo', 'balsam', 'showergel', 'coop-bodyshampoo', 'wella-shampoo', 'wella-hårbalsam', 'dove-bodyshampoo', 'schauma-shampoo', 'schäumend-shampoo', 'xx-hårbalsam', 'jebe-bodyshampoo'], 'shampoo'),
    (['opvaskemasine', 'opvaskemaskine'], 'dishwasher'),
    (['mikroovn'], 'microwave'),
    (['køleskab', 'minikøleskab', 'severin-køleskab', 'bosch-køleskab', 'neff-køleskab'], 'refrigerator'),
    (['ting i nærheden', 'privat indgang*14', 'ting i nærheden'], 'attractions nearby'),
    (['gratis'], 'free'),
    (['overvågningskameraer', 'overvågningskameraer.1', 'overvågningskameraer.2', 'overvågningskameraer.3', 'overvågningskameraer.4', 'overvågningskameraer.5'], 'security'),
    (['privat badeværelse', 'badeværelse', 'privat badeværelse med bruser','badeværelse', 'babybadekar','1 badeværelse'], 'bathroom'),
    (['privat'], 'bedroom'),
    (['dedikeret arbejdsplads', 'arbejdsområde', 'arbejdsområde med plads til','bærbare ventilatorer', 'ethernet-forbindelse', 'dedikeret arbejdsplads', 'adgang til sø', 'gæster kan bruge fællesområderne', 'ski direkte til døren', 'fælles terrasse eller gårdhave', 'fitnessrum', 'dedikeret arbejdsplads.1', 'dedikeret arbejdsplads.2', 'dedikeret arbejdsplads.3', 'dedikeret arbejdsplads.4', 'dedikeret arbejdsplads.5', 'dedikeret arbejdsplads.6', 'dedikeret arbejdsplads.7'], 'work'),
    (['køkken og spisning', 'køkken*7', 'sted hvor gæs', 'service og bestik*14', 'skåle', 'fryser', 'elkedel', 'kaffemaskine', 'vinglas', 'brødrister', 'bagepapir', 'blender', 'spisebord', 'kaffemaskine: kaffemaskine', 'kaffemaskine: filter', 'komfur', 'elkomfur', 'elkomfur fra goronje', 'elkomfur fra der her', 'komfur i rustfrit stål','køkken', 'gaskomfur', 'gasovn','køkken', 'tekøkken', 'køkkentøj','porcelæn', 'porcelæn og bestik'], 'kitchen'),
    (['parkering og faciliteter', 'gratis parkering på stedet', 'betalingsparkering i nærheden', 'betalingsparkering på stedet','betalingsparkering på stedet', 'gratis parkering i indkørslen', 'betalingsparkering p.1''oplader til elbiler', 'bekræftet', 'betalingsparkering p.1', 'betalingsparkering p.2'], 'parkering and faciliteter'),
    (['udendørs', 'privat terrasse eller balkon', 'privat baghave/baggård','grill', 'grillplads', 'grill', 'udekøkken med ovn', 'solsenge', 'udekøkken', 'bålsted', 'hængekøje', 'udendørsmøbler', 'udendørs spiseområde', 'baghave/baggård*11', 'udendørs brusebad', 'solsenge', 'fælles spabad – tilgængeligt','terrasse', 'privat terrasse','udendørskøkken','terrasse eller balkon','solsenge', 'solsenge','udendørs', 'privat terrasse eller balkon', 'privat baghave/baggård', 'grill', 'udekøkken med ovn', 'solsenge', 'udekøkken', 'bålsted', 'hængekøje', 'udendørsmøbler', 'udendørs spiseområde', 'baghave/baggård*11', 'udendørs brusebad', 'solsenge', 'fælles spabad – tilgængeligt', 'fælles baghave/baggå.1', 'privat baghave/baggå.1', 'privat baghave/baggå.2','udendørs brusebad'], 'outdoor'),
    (['en pejs i boligen', 'pejs'], 'fireplace'),
    (['elevator*10', 'boligen eller bygningen har en elevator, der kan transportere gæster op og ned','elevator*10', 'boligen eller bygningen har en elevator, der kan transportere gæster op og ned'], 'elevator'),
    (['morgenmad*9', 'der tilbydes morgenmad'], 'breakfast'),
    (['indtjekning uden vært','værten bor i nærhede', 'værten bor i nærhede'], 'host'),
    (['postboks'], 'mailbox'),
    (['træningsudstyr', 'træningsudstyr', 'privat fitnesscenter', 'fælles fitnesscenter'], 'fitness equipment'),
    (['kaffemaskine: espresso', 'kaffe', 'te', 'kaffemaskine: stempe', 'kaffemaskine: filter', 'kaffemaskine: nespre', 'kaffemaskine: kaffemaskine'], 'kitchen'),
    (['centralvarme','central aircondition', 'central air conditioning','aircondition','aircondition', 'aircondition – kanal', 'bærbart varmeapparat', 'aircondition', 'bærbart varmeapparat', 'aircondition – kanal', 'bærbart varmeapparat', 'aircondition', 'bærbart varmeapparat'], 'temperature'),
    (['træningsudstyr', 'træningsudstyr'], 'fitness equipment'),
    (['kæledyr tilladt', 'kæledyr tilladt'], 'pets allowed'),
    #(['2 gæster', '3 gæster', '6 senge', '2 senge', '4 senge', '1 seng', '1 enkeltseng', '1 dobbeltseng', '1 soveværelse', '2 soveværelser', '3 senge', '6 senge', '3 senge', '2 delte badeværelser', '4 senge', '2 senge', '1 seng', '1 sovesofa', '3 gæster'], 'Bedrooms'),
    (['førstehjælpskasse','sikkerhed i hjemmet', 'røgalarm', 'kuliltealarm','førstehjælpskasse', 'brandslukker','sikkerhed i hjemmet', 'røgalarm', 'kuliltealarm','førstehjælpskasse', 'brandslukker'], 'security'),
    (['internet og kontor', 'trådløst internet', 'dedikeret arbejdspla', 'dedikeret arbejdspla.1', 'dedikeret arbejdspla.2', 'dedikeret arbejdspla.3', 'dedikeret arbejdspla.4', 'dedikeret arbejdspla.5', 'dedikeret arbejdspla.6', 'dedikeret arbejdspla.7'], 'work'),
    (['ting i nærheden', 'vandudsigt', 'lige ved ', 'adgang til sø', 'gæster', 'privat indgang', 'separ', 'privat baghave/baggå.1', 'værten bor her med s'], 'attractions nearby'),
    (['rengøringsprodukter', 'tøjopbevaring: kommo', 'tøjopbevaring: garde', 'tøjopbevaring: garde.1', 'tøjopbevaring: walk-'], 'other'),
    (['bordtennisbord', 'puslebord', 'bærbar aircondition', 'bærbare ventilatorer', 'børnebøger og legetø.1', 'babyporte', 'indendørs pejs: bræn', 'ovn', 'fælles baghave/baggå.1', 'børnebøger og legetø.1', 'babyalarm – altid i ', 'babybadekar – altid i ', 'babybadekar – altid i ', 'pack \'n play / rejse', 'pack \'n play / rejse.1', 'børnebøger og legetø.1', 'babybadekar', 'puslebord', 'høj stol', 'fritstående høj stol''høj stol med pude – ', 'babyalarm'], 'family'),
    #(['4 gæster'], 'accommodation capacity'),
    (['1 soveværelse'], 'number of bedrooms'),
    (['2 senge'], 'number of beds'),
    (['rengøringsprodukter'], 'cleaning products'),
    (['varmt vand'], 'hot water'),
    (['bøjler'], 'hangers'),
    (['mørklægningsgardiner'], 'blackout curtains'),
    (['eget', 'egen indgang'], 'private entrance'),
    (['adgang til hjemmet', 'selvstændig indgang'], 'access to home'),
    (['kæledyr tilladt', 'kæledyr tilladt'], 'pets allowed'),
    (['rygning tilladt', 'rygning tilladt','rygepolitik', 'rygepolitik', 'smoking policy'], 'smoking allowed'),

]


def clean_airbnb_data(df, taylor_df, city_df):

    df_now = df[['Cities', 'Day_pre','location','price','rating']].copy()
    

    df_now['price'] = df_now['price'].astype(str)
    df['info'] = df['info'].astype(str)

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
                char_num = ""
                for char in info_now:
                    if char.isdigit():
                        char_num += char
                
                if char_num != "":
                    char_num = int(char_num)
                    df_now.loc[i, 'gæster'] = char_num

            if ('seng' in info_now) or ('sovesofa' in info_now):
                char_num = ""
                for char in info_now:
                    if char.isdigit():
                        char_num += char
                
                if char_num != "":
                    char_num = int(char_num)
                    df_now.loc[i, 'soveværelser'] = char_num

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
    df_now['omtaler'] = df_now['omtaler'].str.replace(",", "")
    #df_now['omtaler'] = df_now['omtaler'].str.replace(".", "")
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
    #df_now = df_now.merge(city_df, left_on='city', right_on='city', how='left')


    # put these columns first
    cols_first = ["city", "date", "treat", "price", "rating", "omtaler", "gæster", "soveværelser"]
    # get the rest of the columns
    
    # remove the first 3 columns
    cols = cols[8:]
    # add the first 3 columns to the rest of the columns
    cols = cols_first + cols + col_names_city
    #print(cols)
    # set the columns
    df_now = df_now[cols]



    return df_now