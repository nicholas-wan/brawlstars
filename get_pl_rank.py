import pandas as pd 
import requests
import re

from pl_mapping_dict import mapping_dict

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}

tag = '#2GV02VVQR'

def get_pl_rank_df(club_df, tag):
        brawlstars_url = 'https://brawlstats.com/club/'
        tag = tag.replace('#','')
        url = brawlstars_url + tag
        response = requests.get(url, headers=headers).text

        start_index = response.find('"members":[')
        end_index = response.find('],"membersOnline"')
        trunc_response = response[start_index+12:end_index]

        members = trunc_response.split('"name":"')[1:]

        res_list= []

        for member in members:
                player_tag = re.search('"hashtag":"(.+?)"', member).group(1)
                pl_score =  int(re.search('"powerLeagueSolo":(.+?),', member).group(1))
                res_list.append((player_tag, pl_score))

        df = pd.DataFrame.from_records(res_list, columns =['tag','pl_score'])
        df['tag'] = '#'+df['tag']
        
        res = club_df.merge(df, on='tag', how='inner')
        return res
