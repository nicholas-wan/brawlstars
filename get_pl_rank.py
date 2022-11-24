import pandas as pd 
import requests
import re
import concurrent.futures
import os
import time

from pl_mapping_dict import mapping_dict

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:12.0) Gecko/20100101 Firefox/12.0'}

test_url = 'https://brawlstats.com/profile/2GV02VVQR'

# Note that cloudfare has a rate limit of 1200 requests per 5 mins
def get_pl_rank(tag):
    attempts = 0
    while attempts <= 5:
        try:
            brawlstars_url = 'https://brawlstats.com/profile/'
            tag = tag.replace('#','')
            url = brawlstars_url + tag
            response = requests.get(url, headers=headers).text
            solo_pl = re.search('<img src="https://cdn.brawlstats.com/ranked-ranks/ranked_ranks_l_(.+?).png" class="DPUFH-EhiGBBrkki4Gsaf"', response).group(1)
            return (tag, int(solo_pl))
        except:
            pass
            attempts+=1
    print('Error getting PL rank')
    return (tag, -1)

def get_pl_rank_club(original_df):
        if 'highest_pl_rank_score' not in original_df.columns:
                tags = list(original_df['tag'])
                res = []
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        # Start the load operations and mark each future with its URL
                        # future_to_url = {executor.submit(get_pl_rank, tag, header): (tag, header) for (tag, header) in params}
                        future_to_url = {executor.submit(get_pl_rank, tag) for tag in tags}
                        for future in concurrent.futures.as_completed(future_to_url):
                                data = future.result()
                                res.append(data)
                res_df = pd.DataFrame.from_records(res, columns =['tag','highest_pl_rank_score'])
                print(res_df)
                res_df['highest_pl_rank'] = res_df['highest_pl_rank_score'].map(lambda x: mapping_dict[x])
                res_df['tag'] = '#'+res_df['tag']
                df = original_df.merge(res_df, on='tag')
                return df
        else:
                return original_df



