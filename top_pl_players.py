import brawlstats
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
from tqdm import tqdm 
from multiprocessing.dummy import Pool as ThreadPool 

url = 'http://brawlace.com/rankings-power-league'
r = requests.get(url)

html_table = BeautifulSoup(r.text, features="lxml").find('table')
r.close()

best_players_df = pd.read_html(str(html_table), header=0)[0]
best_players_df['Link'] = [link.get('href') for link in html_table.find_all('a')]
best_players_df['player_tag'] = best_players_df['Link'].map(lambda x: x.split('%')[-1][2:])

best_players_df = best_players_df[['Name','Club','player_tag']]
best_players_df.to_csv('output/best_pl_players.csv', index=False)

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
    b = client.get_battle_logs(player_tag, use_cache=False )
    df = pd.DataFrame.from_records(b)
    json_struct = json.loads(df.to_json(orient="records"))    
    df_flat = pd.json_normalize(json_struct)
    df_flat['player_tag'] = player_tag
    df_flat = filter_records(df_flat)
    return df_flat

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

battles_df = battles_df[['event.map','battle.result','battle.teams','player_tag']]
battles_df = battles_df.dropna(subset=['battle.teams','event.map'])
battles_df['brawler_name']  = battles_df.apply(lambda x: get_brawler_name(x['battle.teams'], x['player_tag']), axis=1)

pl_maps = [ 'Hard Rock Mine', 'Double Swoosh', 'Crystal Arcade',
            'Pinhole Punt', 'Sneaky Fields', 'Super Beach',
            'Safe Zone', 'Bridge Too Far', 'Pit Stop',
            'Shooting Star','Layer Cake','Canal Grande',
            'Dueling Beetles',  'Ring of Fire', 'Open Zone', 
            'Goldarm Gulch', 'Belles Rock','Out in the Open']
battles_df['event.map'] = battles_df['event.map'].map(lambda x: x.replace("'",''))
battles_df = battles_df[battles_df['event.map'].isin(pl_maps)]
battles_df = battles_df[['event.map','battle.result','brawler_name']]
battles_df = battles_df.sort_values(['event.map','brawler_name','battle.result']).reset_index(drop=True)

maps = []

for map_name in pl_maps:
    temp_df = battles_df[battles_df['event.map']==map_name]
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

reference = pd.read_csv('maps/brawlers.csv')[['gamemodes','map']]
reference['map'] = reference['map'].map(lambda x: str.lower(x))
res = res.merge(reference, on='map')
res['gamemodes'] = res['gamemodes'].map(lambda x: str.lower(x))
res.to_csv('maps/pro_battles.csv', index=False)
print(res)