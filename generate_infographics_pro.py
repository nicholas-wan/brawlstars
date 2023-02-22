import os
import pandas as pd
from tqdm import tqdm
import argparse

import sys
project_directory = os.getcwd()
sys.path.append(os.path.join(project_directory, 'maps'))

from cheatsheet_utils import *

##############
### Params ###
##############

map_urls_csv = os.path.join(project_directory, 'maps/map_urls.csv')
brawler_data_csv = os.path.join(project_directory, 'maps/pro_battles.csv')
infographics_output_folder = os.path.join(project_directory, 'output/infographics')

############
### Main ###
############
num_best_brawlers=12

print('Generating Infographics')
# Generate Top 12 brawlers overall
best_brawlers_df = get_best_brawlers(num_best_brawlers)
for col in ['bestmap1','bestmap2','bestmap3']:
    best_brawlers_df[col] = best_brawlers_df[col].map(lambda x: x.title())
print('Generating page 1')
df_to_png(best_brawlers_df, os.path.join(infographics_output_folder, 'infographics1.png'))
print('Generate page 1 complete')
# Generate best brawlers for each map. Save in 2 seperate png
cheatsheet = get_best_brawlers_map(num_best_brawlers)
cheatsheet_part1 = cheatsheet.fillna('   ').head(9)
cheatsheet_part2 = cheatsheet.fillna('   ').tail(len(cheatsheet)-9)
print('Generating page 2 & 3')
df_to_png(cheatsheet_part1, os.path.join(infographics_output_folder, 'infographics2.png'))
df_to_png(cheatsheet_part2, os.path.join(infographics_output_folder, 'infographics3.png'))
print('Complete')