import pandas as pd 
import requests
import re
from tqdm import tqdm

from pl_mapping_dict import mapping_dict

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}

def get_highest_pl_score(tag):
    attempts = 0
    while attempts <5:
        try:
            brawlstars_url = 'https://brawlstats.com/profile/'
            tag = tag.replace('#','')
            url = brawlstars_url + tag
            response = requests.get(url, headers=headers).text
            response = response[response.find('Highest Solo League'):response.find('Highest Solo League')+135]
            response = response[response.find('<img'):]
            highest_pl_score = int(re.findall(r'\d+', response)[0])
            return highest_pl_score
        except:
            print('Error for:', tag)
            print(response)
    return -1


# Run for C9
# if True:
#     df = pd.read_csv('./output/c9/c9aurac_brawler_levels.csv')
#     highest_pl_scores = []

#     for i in tqdm(range(len(df))):
#         highest_pl_scores.append(get_highest_pl_score(df['tag'].iloc[i]))

#     df['highest_pl_score'] = highest_pl_scores
#     df['highest_pl_rank'] = df['highest_pl_score'].map(lambda x: mapping_dict[x])

#     df = df.sort_values(by=['highest_pl_score','pl_score','trophies'], ascending=[False,False,False]).reset_index(drop=True)
#     df = df[['player', 'tag', 'trophies', 'level_11s', 'pl_score', 'pl_rank','highest_pl_score', 'highest_pl_rank']]
#     avg_highest_score = round(sum(df['highest_pl_score']/ len(df[df['highest_pl_score']!=0])),2)
#     avg_score = round(sum(df['pl_score']/ len(df[df['pl_score']!=0])),2)
#     print('Avg Highest PL Score C9:', avg_highest_score, mapping_dict[int(avg_highest_score)])
#     print('Avg PL Score C9:', avg_score, mapping_dict[int(avg_score)])
#     df.to_csv('./output/c9/c9aurac_pl_ranks.csv', index=False)

# Run for C6
if True:
    df = pd.read_csv('./output/c6/c6aurac_brawler_levels.csv')
    highest_pl_scores = []

    for i in tqdm(range(len(df))):
        highest_pl_scores.append(get_highest_pl_score(df['tag'].iloc[i]))

    df['highest_pl_score'] = highest_pl_scores
    df['highest_pl_rank'] = df['highest_pl_score'].map(lambda x: mapping_dict[x])

    df = df.sort_values(by=['highest_pl_score','pl_score','trophies'], ascending=[False,False,False]).reset_index(drop=True)
    df = df[['player', 'tag', 'trophies', 'level_11s', 'pl_score', 'pl_rank','highest_pl_score', 'highest_pl_rank']]
    avg_highest_score = round(sum(df['highest_pl_score']/ len(df[df['highest_pl_score']!=0])),2)
    avg_score = round(sum(df['pl_score']/ len(df[df['pl_score']!=0])),2)
    print('Avg Highest PL Score C6:', avg_highest_score, mapping_dict[int(avg_highest_score)])
    print('Avg PL Score C6:', avg_score, mapping_dict[int(avg_score)])
    df.to_csv('./output/c6/c6aurac_pl_ranks.csv', index=False)