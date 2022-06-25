from selenium import webdriver
import os
import pandas as pd
from selenium.webdriver.common.by import By
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--refresh', '-r', choices=['yes','no'], default='no', type=str, help='yes to obtain the latest stats, else no')
parser.add_argument('--num_best_brawlers', '-n', default=8, type=int, help='Enter the number of best brawlers to find out the statistics for')
parser.add_argument('--chrome_headless', '-c', choices=['yes','no'], default='yes', type=str, help='yes for headless chrome browser else no')
parser.add_argument('--min_use_rates', '-m', default=1, type=float, help='minimum use rate. Range from 1-100')

args = parser.parse_args()

##############
### Params ###
##############
refresh = args.refresh # Set to True if you wish to obtain fresh data
num_best_brawlers = args.num_best_brawlers # Lists out the best brawlers
headless = args.chrome_headless # Use a headless chrome browser for scraping
min_use_rates = args.min_use_rates

############
### Main ###
############

if headless=='yes':
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options)
else:
    driver = webdriver.Chrome()

if refresh=='yes':
    driver.get('https://brawlify.com/league/')
    print('Refreshing Map URLs with the updated Power League Maps')
    elems = driver.find_elements(By.XPATH, "//a[@href]")

    links = [elem.get_attribute('href') for elem in elems]
    gamemodes = [x for x in links if 'gamemodes' in x]    
    gamemodes = [x for x in gamemodes if 'detail' in x]
    gamemodes = [x.split('/')[-1].replace('-',' ') for x in gamemodes]

    links = [x for x in links if 'map' in x]
    links = [x for x in links if 'detail' in x]

    df = pd.DataFrame({'gamemodes':gamemodes, 'url':links[:18]})
    df.to_csv('./map_urls.csv', index=False)
    print('Saved csv to map_urls.csv')

df = pd.read_csv('./map_urls.csv')
df['visit_links'] = df['url'].map(lambda x: x+'/600%2B')
df['map'] = df['url'].map(lambda x: x.split('/')[-1].replace('-',' '))

best_brawler_list = []
win_rates_list = []
use_rates_list = []

for i in tqdm(range(len(df))):
    driver.get(df.iloc[i]['visit_links'])
    brawlers = driver.find_elements(By.XPATH,"//tr/td/img")
    brawlers = [x.get_attribute('title') for x in brawlers]

    values = driver.find_elements(By.XPATH,"//tr/td")
    values = [x.text for x in values]
    values = [x for x in values if x!='']

    win_rates, use_rates, mvp_rates = values[::3], values[1::3], values[2::3]

    res = pd.DataFrame({'brawlers':brawlers, 'win_rates':win_rates, 'use_rates':use_rates})
    res['use_rates'] = res['use_rates'].map(lambda x: float(x.replace('%','')))
    res = res[res['use_rates']>min_use_rates].reset_index(drop=True)
    res['use_rates'] = res['use_rates'].map(lambda x: str(x)+'%')

    best_brawler_list.append(list(res.head(num_best_brawlers)['brawlers']))
    win_rates_list.append(list(res.head(num_best_brawlers)['win_rates']))
    use_rates_list.append(list(res.head(num_best_brawlers)['use_rates']))

res_df = df.copy()

res_df['best_brawlers'] = best_brawler_list
res_df['win_rates'] = win_rates_list
res_df['use_rates'] = use_rates_list
    
res_df = res_df[['gamemodes','map','best_brawlers','win_rates','use_rates']]
res_df['best_brawlers'] = res_df['best_brawlers'].map(lambda x: ', '.join(x))
res_df['win_rates'] = res_df['win_rates'].map(lambda x: ', '.join(x))
res_df['use_rates'] = res_df['use_rates'].map(lambda x: ', '.join(x))

res_df.to_csv('./best_brawlers.csv', index=False)
print(res_df)

driver.close()