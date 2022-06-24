# Author: ZSilverZ
# Date: 24 June 2022
# Python Version: 3.7
# Python Libraries Required: brawlstats, tqdm, pandas

"""
Example Usage for Player Tags
>>> python main.py -t 2YQUPUYJ C9LR0R0V

Example Usage for Club Tags
>>> python -i main.py -t 202VGURG0 90JC22UQ 2GGGLQC98 2LUJ0G99U 2GRU08QGL P0Q9LPL0 2GV20JCPV 2R020C0VL 20J9LRP0V
"""

import brawlstats
import pandas as pd
from tqdm import tqdm
from datetime import date
import string
import argparse

today = date.today()

# Insert your Brawl Stars Developer's API Key into a file in the same directory 'api_key.txt'
with open("api_key.txt",'r') as f:
    token = f.read()

client = brawlstats.Client(token)

def valid_player_tag(tag):
    """
    params: tag (string) 
    output: boolean
    """
    try:
        player = client.get_player(tag)
        return True
    except:
        return False

def valid_club_tag(tag):
    """
    params: tag (string) 
    output: boolean
    """
    try:
        club = client.get_club(tag)
        return True
    except:
        return False

def classify_tags(tags):
    """
    # Playertags and Clubtags might be the same. Checks for clubtags as priority

    params: tags (list[string]) 
    output: player_tags, club_tags, invalid_tags (list[string])
    """
    player_tags = []
    club_tags = []
    invalid_tags = []

    for tag in tags:
        if valid_club_tag(tag):
            club_tags.append(tag)
        elif valid_player_tag(tag):
            player_tags.append(tag)
        else:
            invalid_tags.append(tag)
    return player_tags, club_tags, invalid_tags

def get_club_stats(clubtag, save_club_csv):
    """
    params: clubtag (string) e.g #202VGURG0
    output: res (dataframe), csv - writes to CSV file (Only for MK1 and MK2)
    """

    club = client.get_club(clubtag)
    members = club.members

    df_list = []

    for i in tqdm(range(len(members))):
        tag = members[i].tag[1:]
        player = client.get_player(tag)
        df = pd.DataFrame(player.brawlers)[['name','power']]
        df = df.set_index('name').T

        df.insert(0, 'trophies', player.trophies)
        df.insert(0, 'tag', player.tag)
        df.insert(0, 'player', player.name)
        df_list.append(df)

    res = pd.concat(df_list).reset_index(drop=True)

    levels = res.apply(pd.Series.value_counts, axis=1)[[9,10,11]].fillna(0)

    res['level_9s'], res['level_10s'], res['level_11s'] = levels[9], levels[10], levels[11]
    res = res.fillna(0)

    float_col = res.select_dtypes(include=['float64'])
    for col in float_col.columns.values:
        res[col] = res[col].astype('int64')

    avoid_cols = ['player','tag','trophies','level_9s','level_10s','level_11s','brawlers_10','brawlers_11','date']

    # Gets the names of all the level 11 brawlers and aggregates into a single string, which is added as a new column 'brawlers_11'
    club_ten_list, club_eleven_list = [], []
    for i in range(len(res)):
        temp_df = res.iloc[i]
        player_ten_list, player_eleven_list = [], []
        for col in res.columns:
            if col not in avoid_cols:
                if temp_df[col]==11:
                    player_eleven_list.append(col)
                if temp_df[col]==10:
                    player_ten_list.append(col)
        player_ten_list, player_eleven_list = sorted(player_ten_list), sorted(player_eleven_list)
        club_ten_list.append(player_ten_list)
        club_eleven_list.append(player_eleven_list)

    club_ten_list, club_eleven_list = [', '.join(x) for x in club_ten_list], [', '.join(x) for x in club_eleven_list]
    res['brawlers_10'], res['brawlers_11'] = club_ten_list, club_eleven_list

    res['date'] = today.strftime("%m/%d/%y")
    res = res[avoid_cols]

    # Cleans players names to only have ascii_letters and digits
    valid_characters = string.ascii_letters + string.digits
    res['player'] = res['player'].map(lambda x: ''.join(ch for ch in x if ch in valid_characters).lower())
    res = res.sort_values(by=['player']).reset_index(drop=True)

    if clubtag in save_club_csv:
        res.to_csv('./output/'+club.name+'_brawler_levels.csv', index=False)

    stats_dict = {'Club': club.name,
                  'Club Tag': clubtag,
                  'Total Trophies': sum(res['trophies']),
                  'Num Members':  len(members),
                  'Avg Trophies': int(sum(res['trophies'])/len(res)),
                  'Avg 9s per member':round(sum(res['level_9s'])/len(res),1),
                  'Avg 10s per member': round(sum(res['level_10s'])/len(res),1),
                  'Avg 11s per member': round(sum(res['level_11s'])/len(res),1)
                 }
    return stats_dict
    
def get_player_stats(playertag):
    """
    params: playertag (string) e.g #202VGURG0
    output: res_df (dataframe)
    """
    player = client.get_player(playertag)

    df = pd.DataFrame(player.brawlers)[['name','power']]
    nines, tens, elevens = sorted(list(df[df['power']==9]['name'])), sorted(list(df[df['power']==10]['name'])), sorted(list(df[df['power']==11]['name']))
    
    res = {}
    res['player'], res['tag'], res['trophies'] = player.name, playertag, player.trophies
    res['level_9s'], res['level_10s'], res['level_11s'] = len(nines), len(tens), len(elevens)
    res['brawlers_10'], res['brawlers_11'] = ', '.join(tens), ', '.join(elevens)
    res_df = pd.DataFrame(res, index=[0])
    
    return res_df

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tags', '-t', nargs="+", default=['2YQUPUYJ'], type=str, help='input brawl stars tags, seperated by a space')
    parser.add_argument('--save_club_csv', '-s' nargs="+", default=['202VGURG0','90JC22UQ'], type=str, help='Enter club tags seperated by space for specfic clubs you want to save the CSV for')
    args = parser.parse_args()
    
    player_tags, club_tags, invalid_tags = classify_tags(args.tags)
    if len(invalid_tags)>0:
        print('Invalid Tags detected. Please check: ', invalid_tags)

    if len(player_tags)>0:
        print('======================================')
        print(len(player_tags),'Player Tags detected.')
        print('======================================')
        player_df = []
        for playertag in player_tags:
            player_df.append(get_player_stats(playertag))
        player_df = pd.concat(player_df).sort_values(by=['trophies'], ascending=False).reset_index(drop=True)
        player_df.to_csv('./output/players.csv', index=False)
        print(player_df)
        #print(player_df.drop(['brawlers_10'], axis=1).to_markdown(tablefmt="pretty"))

    if len(club_tags)>0:
        print('===================================')
        print(len(club_tags), 'Club Tags detected.')
        print('===================================')        

        stats_dict_list = []
        for clubtag in club_tags:
            stats_dict_list.append(get_club_stats(clubtag, args.save_club_csv))

        compare_stats = pd.DataFrame(stats_dict_list)
        compare_stats = compare_stats.sort_values(by=['Total Trophies'], ascending=False)
        compare_stats.to_csv('./output/comparison.csv', index=False)
        print(compare_stats.to_markdown(tablefmt="pretty"))

    print('Complete')
