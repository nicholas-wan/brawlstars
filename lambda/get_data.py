# Author: ZSilverZ
# Date: 24 June 2022
# Python Version: 3.7
# Python Libraries Required: brawlstats, pandas

"""
Example Usage for Player Tags
>>> python main.py -t 2YQUPUYJ C9LR0R0V

Example Usage for Club Tags
>>> python -i main.py -t 202VGURG0 90JC22UQ 2GGGLQC98 2LUJ0G99U 2GRU08QGL P0Q9LPL0 2GV20JCPV 2R020C0VL 20J9LRP0V
"""

import brawlstats
import pandas as pd
from datetime import date
import string
from get_api_key import api_key

today = date.today()

# Insert your Brawl Stars Developer's API Key into a file in the same directory 'api_key.txt'
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjliYmRhODlhLWRiM2QtNDZhNS04NzNiLTllZDFjZTQxY2UwYiIsImlhdCI6MTY1NDc1MDgwMCwic3ViIjoiZGV2ZWxvcGVyL2E0ZTBmZGY2LTY2NTItYmE0ZS01ZjU5LTUwZmYxYmNkOWQ1ZSIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMTE1LjY2LjgzLjE1NyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.3c6p8Z2ilqRCTd5G2Ih4dz78uHgGDoehYXbN0yGr93qfMxOFlBWwzQb5jEP3KNEPeDSQloVmzrqc36eQ_FvAwQ"

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

def clean_string(s):
    """
    params: s - string of brawlers joined by ', '
    output: cleaned string
    """
    try:
        return s.replace('\n',' ').replace('\\n',' ')
    except:
        return s

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
        if valid_player_tag(tag):
            player_tags.append(tag)
        else:
            invalid_tags.append(tag)
    return player_tags, club_tags, invalid_tags

def get_club_stats(clubtag, truncate_num, include_tens, include_date):


    club = client.get_club(clubtag)
    members = club.members

    df_list = []

    for i in range(len(members)):
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
                    player_eleven_list.append(clean_string(col))
                if temp_df[col]==10:
                    player_ten_list.append(clean_string(col))
        player_ten_list, player_eleven_list = shorten_brawler_string(sorted(player_ten_list), truncate_num), shorten_brawler_string(sorted(player_eleven_list), truncate_num)
        club_ten_list.append(player_ten_list)
        club_eleven_list.append(player_eleven_list)

    res['brawlers_10'], res['brawlers_11'] = club_ten_list, club_eleven_list

    res['date'] = today.strftime("%m/%d/%y")
    res = res[avoid_cols]

    # Cleans players names to only have ascii_letters and digits
    valid_characters = string.ascii_letters + string.digits
    res['player'] = res['player'].map(lambda x: ''.join(ch for ch in x if ch in valid_characters).lower())
    res = res.sort_values(by=['player']).reset_index(drop=True)

    if include_tens=='no':
        res = res.drop('brawlers_10', axis=1)

    if include_date=='no':
        res = res.drop('date', axis=1)


    stats_dict = {'Club': club.name,
                  'Club Tag': clubtag,
                  'Total Trophies': sum(res['trophies']),
                  'Num Members':  len(members),
                  'Avg Trophies': int(sum(res['trophies'])/len(res)),
                  'Avg 9s per member':round(sum(res['level_9s'])/len(res),1),
                  'Avg 10s per member': round(sum(res['level_10s'])/len(res),1),
                  'Avg 11s per member': round(sum(res['level_11s'])/len(res),1)
                 }
    return res, stats_dict
    
def shorten_brawler_string(brawler_list, truncate_num):
    """
    params: brawler_list (list[string])
    output: brawler_string (string), comma seperated
    """
    if len(brawler_list) > truncate_num:
        return ', '.join(brawler_list[:truncate_num])+', ...'
    else:
        return', '.join(brawler_list)

def get_player_stats(playertag, truncate_num):
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
    res['brawlers_10'], res['brawlers_11'] = shorten_brawler_string(tens, truncate_num), shorten_brawler_string(elevens, truncate_num)
    res_df = pd.DataFrame(res, index=[0])
    
    return res_df

    # args = parser.parse_args()
    
    # player_tags, club_tags, invalid_tags = classify_tags(args.tags)
    # if len(invalid_tags)>0:
    #     print('Invalid Tags detected. Please check: ', invalid_tags)

    # if len(player_tags)>0:
    #     print('======================================')
    #     print(len(player_tags),'Player Tags detected.')
    #     print('======================================')
    #     player_df = []
    #     for playertag in player_tags:
    #         try:
    #             player_df.append(get_player_stats(playertag, args.truncate))
    #         except:
    #             print('Error for Clubtag:', clubtag)
    #     if len(player_df)>0:
    #         player_df = pd.concat(player_df).sort_values(by=['trophies'], ascending=False).reset_index(drop=True)
    #         if args.include_tens=='no':
    #             player_df = player_df.drop('brawlers_10', axis=1)
    

    # if len(club_tags)>0:
    #     print('===================================')
    #     print(len(club_tags), 'Club Tags detected.')
    #     print('===================================')        

    #     stats_dict_list = []
    #     for clubtag in club_tags:
    #         try:
    #             stats_dict_list.append(get_club_stats(clubtag, args.truncate, args.include_tens, args.include_date))
    #         except:
    #             print('Error for Clubtag:', clubtag)
        
    #     if len(stats_dict_list)>0:
    #         compare_stats = pd.DataFrame(stats_dict_list)
    #         compare_stats = compare_stats.sort_values(by=['Total Trophies'], ascending=False)
    #         print(compare_stats.to_markdown(tablefmt="pretty"))

    # print('Complete')
