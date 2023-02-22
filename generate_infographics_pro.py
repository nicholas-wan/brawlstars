import os
import pandas as pd
from tqdm import tqdm
import argparse

import sys
sys.path.append('maps')
from cheatsheet_utils import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    ##############
    ### Params ###
    ##############
    map_urls_csv = './maps/map_urls.csv'
    brawler_data_csv = './maps/pro_battles.csv'
    infographics_output_folder = './output/infographics'

    ############
    ### Main ###
    ############
    num_best_brawlers=12

    print('Generating Infographics')
    # Generate Top 12 brawlers overall
    best_brawlers_df = get_best_brawlers(num_best_brawlers)
    best_brawlers_df['bestmap1'] = best_brawlers_df['bestmap1'].map(lambda x: x.capitalize())
    best_brawlers_df['bestmap2'] = best_brawlers_df['bestmap2'].map(lambda x: x.capitalize())
    best_brawlers_df['bestmap3'] = best_brawlers_df['bestmap3'].map(lambda x: x.capitalize())
    df_to_png(best_brawlers_df, os.path.join(infographics_output_folder, 'infographics1.png'))

    # Generate best brawlers for each map. Save in 2 seperate png
    cheatsheet = get_best_brawlers_map(num_best_brawlers)
    cheatsheet_part1 = cheatsheet.fillna('   ').head(9)
    cheatsheet_part2 = cheatsheet.fillna('   ').tail(len(cheatsheet)-9)
    df_to_png(cheatsheet_part1, os.path.join(infographics_output_folder, 'infographics2.png'))
    df_to_png(cheatsheet_part2, os.path.join(infographics_output_folder, 'infographics3.png'))