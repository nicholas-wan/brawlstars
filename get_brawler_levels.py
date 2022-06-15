import brawlstats
import pandas as pd
from tqdm import tqdm
from datetime import date
import string

today = date.today()

# Insert your Brawl Stars Developer's API Key into a file in the same directory 'api_key.txt'
with open("api_key.txt",'r') as f:
    token = f.read()

client = brawlstats.Client(token)

def get_stats(clubtag):
    """
    params: clubtag (string) e.g #202VGURG0
    output: res (dataframe), csv - writes to CSV file
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

    res['level_9s'] = levels[9]
    res['level_10s'] = levels[10]
    res['level_11s'] = levels[11]

    res = res.fillna(0)

    float_col = res.select_dtypes(include=['float64'])
    for col in float_col.columns.values:
        res[col] = res[col].astype('int64')

    avoid_cols = ['player','tag','trophies','level_9s','level_10s','level_11s','brawlers_11','date']

    # Gets the names of all the level 11 brawlers and aggregates into a single string, which is added as a new column 'brawlers_11'
    club_eleven_list = []
    for i in range(len(res)):
        temp_df = res.iloc[i]
        player_eleven_list = []
        for col in res.columns:
            if col not in avoid_cols:
                if temp_df[col]==11:
                    player_eleven_list.append(col)
        player_eleven_list = sorted(player_eleven_list)
        club_eleven_list.append(player_eleven_list)

    club_eleven_list = [', '.join(x) for x in club_eleven_list]
    res['brawlers_11'] = club_eleven_list

    res['date'] = today.strftime("%m/%d/%y")
    res = res[avoid_cols]

    # Cleans players names to only have ascii_letters and digits
    valid_characters = string.ascii_letters + string.digits
    res['player'] = res['player'].map(lambda x: ''.join(ch for ch in x if ch in valid_characters).lower())
    res = res.sort_values(by=['player']).reset_index(drop=True)

    res.to_csv(club.name+'_brawler_levels.csv', index=False)
    print(res.head(5))

    print('---------------------')
    print('Stats for: ', club.name)
    print('---------------------')
    print('Avg 9s per member', round(sum(res['level_9s'])/len(res),3))
    print('Avg 10s per member', round(sum(res['level_10s'])/len(res),3))
    print('Avg 11s per member', round(sum(res['level_11s'])/len(res),3))
    print('Avg Trophies', round(sum(res['trophies'])/len(res),3))

    return res
    
if __name__=='__main__':
    mk1 = '202VGURG0' 
    mk2 = '90JC22UQ'

    mage_knights_one = get_stats(mk1)
    mage_knights_two = get_stats(mk2)

    print('Complete')
