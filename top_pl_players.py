import brawlstats
import time
import requests
import pandas as pd
import os
from bs4 import BeautifulSoup
import json
from tqdm import tqdm 
from multiprocessing.dummy import Pool as ThreadPool 
import datetime

print('=============================')
now = datetime.datetime.now() 
print("Current Time", now)

refresh_playertags = 'yes'
download_battles = 'yes'

################################
### Download Best Playertags ###
################################

if refresh_playertags == 'yes':
    def get_df(url, num_players):
        r = requests.get(url)
        html_table = BeautifulSoup(r.text, features="lxml").find('table')
        r.close()
        df = pd.read_html(str(html_table), header=0)[0].head(num_players)
        df['Link'] = [link.get('href') for link in html_table.find_all('a')][:num_players]
        df['player_tag'] = df['Link'].map(lambda x: x.split('%')[-1][2:])
        df = df[['Name','player_tag']]
        return df

    # best_countries_df = pd.read_csv(gsheet_url, usecols=['url','num_players'])
    # Global
    best_countries_df = pd.read_csv('battle_logs/Team Power League Drafts - Top Players.csv')[['url','num_players']]
    best_countries_regional_df  = pd.read_csv('battle_logs/Team Power League Drafts - Top Players (Regional).csv')[['url','num_players']]

    def get_top_players(df, label):
        countries = []
        for i in tqdm(range(len(df))):
            countries.append(get_df(df.iloc[i]['url'], df.iloc[i]['num_players']))
        res = pd.concat(countries).drop_duplicates().reset_index(drop=True)
        return res 

    global_df = get_top_players(best_countries_df, 'global')       
    regional_df = get_top_players(best_countries_regional_df, 'regional')

    g = set(global_df['player_tag'])
    r = set(regional_df['player_tag'])

    best_players_df = pd.concat([global_df, regional_df])[['Name','player_tag']].drop_duplicates()
    best_players_df['global'] = best_players_df['player_tag'].map(lambda x: 1 if x in g else 0)
    best_players_df['regional'] = best_players_df['player_tag'].map(lambda x: 1 if x in r else 0)

    best_players_df.to_csv('output/best_pl_players.csv', index=False)

else:
    best_players_df = pd.read_csv('output/best_pl_players.csv')
    g = set(best_players_df[best_players_df['global']==1]['player_tag'])
    r = set(best_players_df[best_players_df['regional']==1]['player_tag'])

############################
### Download Battle Logs ###
############################

api_key = "api_key.txt"
# Insert your Brawl Stars Developer's API Key into a file in the same directory 'api_key.txt'
with open(api_key,'r') as f:
    token = f.read()
client = brawlstats.Client(token)

def filter_records(df):
    if 'battle.trophy_change' in df.columns:
        df = df[~df['battle.type'].isin(['challenge','ranked'])]
        df = df[df['battle.trophy_change'].isna()]
    return df

def get_battle_records(player_tag):
    try:
        b = client.get_battle_logs(player_tag, use_cache=False )
        df = pd.DataFrame.from_records(b)
        json_struct = json.loads(df.to_json(orient="records"))    
        df_flat = pd.json_normalize(json_struct)
        df_flat['player_tag'] = player_tag
        df_flat = filter_records(df_flat)
        return df_flat
    except:
        pass

pl_maps = pd.read_csv('maps/maps.csv')['map'].tolist()
pl_maps = [x.replace('\'','') for x in pl_maps]

if download_battles=='yes':
    pool = ThreadPool(4) 
    start_time = time.time()
    print('Starting Multithreading to get Battle logs')
    df_list = pool.map(get_battle_records, list(best_players_df['player_tag']))
    print("--- %s seconds ---" % (time.time() - start_time))

    battles_df = pd.concat(df_list)

    def get_brawler_name(team_data, player_tag):
        for player in team_data[0]:
            if player['tag'].replace('#','')==player_tag:
                return player['brawler']['name']
        for player in team_data[1]:
            if player['tag'].replace('#','')==player_tag:
                return player['brawler']['name']

    battles_df = battles_df.dropna(subset=['battle.teams','event.map'])
    battles_df['brawler_name']  = battles_df.apply(lambda x: get_brawler_name(x['battle.teams'], x['player_tag']), axis=1)

    battles_df['event.map'] = battles_df['event.map'].map(lambda x: x.replace("\'",''))
    # print(battles_df['event.map'].value_counts())
    battles_df_original = battles_df.copy()
    battles_df = battles_df[battles_df['event.map'].isin(pl_maps)]
    battles_df = battles_df.sort_values(['event.map','brawler_name','battle.result']).reset_index(drop=True)
    battles_df['battle_time'] = pd.to_datetime(battles_df['battle_time'])
    battles_df['battle_time'] = battles_df['battle_time'].map(lambda x: x.strftime("%m/%d/%Y %H:%M:%S"))
    battles_df = battles_df[['battle_time','event.map','battle.result','player_tag','brawler_name']]

    if os.path.exists('battle_logs/battle_logs.csv'):
        old = pd.read_csv('battle_logs/battle_logs.csv')
        print('Old Data Size:', len(old))
        battles_df = pd.concat([battles_df, old]).drop_duplicates().reset_index(drop=True)
        print('New Data Size:', len(battles_df))

    # Minimum time of new map
    battles_df['global'] = battles_df['player_tag'].map(lambda x: 1 if x in g else 0)
    battles_df['regional'] = battles_df['player_tag'].map(lambda x: 1 if x in r else 0)
    battles_df.to_csv('battle_logs/battle_logs.csv', index=False)

#############################
### Generate Infographics ###
#############################

battles_df = pd.read_csv('battle_logs/battle_logs.csv')

def prepare_stats(battles_df, label):
    battles_df = battles_df[battles_df[label]==1].reset_index(drop=True)
    maps = []

    for map_name in pl_maps:
        temp_df = battles_df[battles_df['event.map']==map_name.replace('\'','')]
        brawlers = []
        unique_brawlers = set(temp_df['brawler_name'])
        for brawler in unique_brawlers:
            temp_df2 = temp_df[temp_df['brawler_name']==brawler]
            victories = len(temp_df2[temp_df2['battle.result']=='victory'])
            win_rate = victories / len(temp_df2)
            use_rate = len(temp_df2) / len(temp_df)
            brawlers.append([brawler, win_rate, use_rate])
        brawlers = sorted(brawlers, key = lambda x: (-x[2], -x[1]))[:12]
        best_brawlers = ', '.join([str.lower(i[0]).replace("'",'') for i in brawlers])
        win_rates = [i[1] for i in brawlers]
        use_rates = [i[2] for i in brawlers]
        win_rates = ', '.join([str(round(i*100,2))+'%' for i in win_rates])
        use_rates = ', '.join([str(round(i*100))+'%' for i in use_rates])
        maps.append({'map':str.lower(map_name), 'best_brawlers':best_brawlers,'win_rates':win_rates,'use_rates':use_rates, 'num_battles':len(temp_df), 'num_brawlers':len(unique_brawlers)})

    res = pd.DataFrame(maps)

    reference = pd.read_csv('maps/maps.csv')[['gamemodes','map']]
    reference['map'] = reference['map'].map(lambda x: x.replace("\'",''))
    reference['map'] = reference['map'].map(lambda x: str.lower(x))
    res = res.merge(reference, on='map')
    res['gamemodes'] = res['gamemodes'].map(lambda x: str.lower(x))
    res['label']=label
    return res 
print('Total Num Battles:',len(battles_df))
days_ago = (datetime.datetime.now()-datetime.timedelta(days=7)).strftime('%m/%d/%Y %H:%M:%S')
battles_df = battles_df[battles_df['battle_time']>=days_ago]
print("Total Num Battles (Last 7 Days):", days_ago,':', len(battles_df))

global_battles_df = prepare_stats(battles_df, 'global')
regional_battles_df = prepare_stats(battles_df, 'regional')
res = pd.concat([global_battles_df, regional_battles_df]).reset_index(drop=True)
res.to_csv('maps/pro_battles.csv',index=False)

