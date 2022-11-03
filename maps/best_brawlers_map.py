from selenium import webdriver
import os
import pandas as pd
from selenium.webdriver.common.by import By
from tqdm import tqdm
import argparse
from cheatsheet_utils import *
import undetected_chromedriver as uc

parser = argparse.ArgumentParser()
parser.add_argument('--refresh_maps', '-rm', choices=['yes','no'], default='no', type=str, help='yes to obtain the latest maps, else no')
parser.add_argument('--refresh_stats', '-s', choices=['yes','no'], default='no', type=str, help='yes to obtain the latest stats, else no')
parser.add_argument('--generate_infographics', '-g', choices=['yes','no'], default='yes', type=str, help='yes to obtain the latest infographics')
parser.add_argument('--num_best_brawlers', '-n', default=12, type=int, help='Enter the number of best brawlers to find out the statistics for')
parser.add_argument('--chrome_headless', '-c', choices=['yes','no'], default='yes', type=str, help='yes for headless chrome browser else no')
parser.add_argument('--min_usage_rank', '-m', default=40, type=float, help='minimum use rate. rank #')

args = parser.parse_args()

##############
### Params ###
##############
refresh_maps = args.refresh_maps 
refresh_stats = args.refresh_stats 
generate_infographics = args.generate_infographics
num_best_brawlers = args.num_best_brawlers # Lists out the best brawlers
min_usage_rank = args.min_usage_rank

############
### Main ###
############

def initialize_uc_driver():
    options = webdriver.ChromeOptions() 
    options.headless = True
    options.add_argument("start-maximized")
    driver = uc.Chrome(options=options)
    return driver

def initialize_driver():
    if args.chrome_headless=='yes':
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        driver = webdriver.Chrome(options = options)
    else:
        driver = webdriver.Chrome()
    return driver

if refresh_maps=='yes':
    driver = initialize_driver()
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
    if len(df)==18:
        df.to_csv('./map_urls.csv', index=False)
        print('Saved csv to map_urls.csv')
    else:
        print('Error with maps')
        print(df)

if refresh_stats=='yes':
    print('Refreshing data for best brawlers for each Map')
    df = pd.read_csv('./map_urls.csv')
    df['map'] = df['url'].map(lambda x: x.split('/')[-1].replace('-',' '))

    best_brawler_list = []
    win_rates_list = []
    usage_rank_list = []
    num_brawlers_list = []
    filter_list = []

    def scrape_info(url, filter_trophies, threshold=53):
        driver = initialize_uc_driver()
        if filter_trophies=='600+':
            url+='/600%2B'
        driver.get(url)

        stats = [x.text for x in driver.find_elements(By.CLASS_NAME,"row")]
        stats = [y for y in stats if y!='']
        stats = stats[2:]
        stats = stats[0].split('\n')

        brawlers = stats[::7]
        win_rates = stats[2::7]
        usage_rank = stats[5::7]
        usage_rank = [int(y.replace('#','')) for y in usage_rank]

        res = pd.DataFrame({'brawlers':brawlers, 'win_rates':win_rates, 'usage_rank':usage_rank}).sort_values(by=['win_rates'], ascending=False)
        num_brawlers = len(res)
        best_brawlers = list(res['brawlers'])
        win_rates = list(res['win_rates'])
        usage_rank = list(res['usage_rank'])
        driver.quit()
        return best_brawlers, win_rates, usage_rank, num_brawlers

    for i in tqdm(range(len(df))):
        best_brawlers, win_rates, usage_rank, num_brawlers = scrape_info(df.iloc[i]['url'], filter_trophies='600+')
        filter_value = '600+'
        if win_rates==[]:
            print('[Retrying]:',df.iloc[i]['map'], '[num_brawlers]:',num_brawlers)
            new_best_brawlers, new_win_rates, new_usage_rank, new_num_brawlers = scrape_info(df.iloc[i]['url'], filter_trophies='', threshold=0)
            if new_num_brawlers > num_brawlers:
                best_brawlers = new_best_brawlers
                win_rates = new_win_rates
                usage_rank = new_usage_rank
                num_brawlers = new_num_brawlers
                filter_value =''

        best_brawler_list.append(best_brawlers)
        win_rates_list.append(win_rates)
        usage_rank_list.append(usage_rank)
        num_brawlers_list.append(num_brawlers)
        filter_list.append(filter_value)

    res_df = df.copy()

    res_df['best_brawlers'] = best_brawler_list
    res_df['win_rates'] = win_rates_list
    res_df['usage_rank'] = usage_rank_list
    res_df['num_brawlers'] = num_brawlers_list
    res_df['filter'] = filter_list

    res_df = res_df[['gamemodes','map','best_brawlers','win_rates','usage_rank','num_brawlers','filter']]
    res_df['best_brawlers'] = res_df['best_brawlers'].map(lambda x: ', '.join(x))
    res_df['win_rates'] = res_df['win_rates'].map(lambda x: ', '.join(x))
    res_df['usage_rank'] = res_df['usage_rank'].map(lambda x: ', '.join([str(y) for y in x]))

    res_df.to_csv('./brawlers.csv', index=False)
    print(res_df)

if generate_infographics=='yes':
    print('Generating Infographics')
    # Generate Top 12 brawlers overall
    best_brawlers_df = get_best_brawlers(num_best_brawlers)
    df_to_png(best_brawlers_df, 'infographics/infographics1.png')

    # Generate best brawlers for each map. Save in 2 seperate png
    cheatsheet = get_best_brawlers_map(num_best_brawlers)
    cheatsheet_part1 = cheatsheet.fillna('   ').head(9)
    cheatsheet_part2 = cheatsheet.fillna('   ').tail(len(cheatsheet)-9)
    df_to_png(cheatsheet_part1, 'infographics/infographics2.png')
    df_to_png(cheatsheet_part2, 'infographics/infographics3.png')

    # Generate Checklist for a specific team
    checklist_df = get_best_brawlers_checklist(best_brawlers_df, 'c9')#, team_tags = team_tags_tribe)
    df_to_png(checklist_df, 'infographics/infographics_checklist_team5.png')

    # Generate Checklist for tribe
    checklist_df = get_best_brawlers_checklist(best_brawlers_df, 'c9', team_tags = team_tags_tribe_c9)
    df_to_png(checklist_df, 'infographics/infographics_checklist_team2.png')
