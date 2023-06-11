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

map_csv = os.path.join(project_directory, 'maps','maps.csv')
brawler_data_csv = os.path.join(project_directory, 'maps','pro_battles.csv')
infographics_output_folder = os.path.join(project_directory, 'output','infographics')

############
### Main ###
############

num_best_brawlers=12

print('Generating Infographics')
# Generate Top 12 brawlers overall
def generate_infographics(num_best_brawlers, label):
    best_brawlers_df = get_best_brawlers(num_best_brawlers, label)
    for col in ['bestmap1','bestmap2','bestmap3']:
        best_brawlers_df[col] = best_brawlers_df[col].map(lambda x: x.title())
    print('Generating page 1')
    df_to_png(best_brawlers_df, os.path.join(infographics_output_folder, label+'_infographics1.png'))
    print('Generate page 1 complete')
    # Generate best brawlers for each map. Save in 2 seperate png
    cheatsheet = get_best_brawlers_map(num_best_brawlers, label)
    cheatsheet_part1 = cheatsheet.fillna('   ').head(9)
    cheatsheet_part2 = cheatsheet.fillna('   ').tail(len(cheatsheet)-9)
    print('Generating page 2 & 3')
    df_to_png(cheatsheet_part1, os.path.join(infographics_output_folder, label+'_infographics2.png'))
    df_to_png(cheatsheet_part2, os.path.join(infographics_output_folder, label+'_infographics3.png'))

    for i in [1,2,3]:
        info_path = 'output/infographics/'+label+'_infographics'+str(i)+'.png'
        copyright_apply(info_path, info_path,'@ZSilverZ')

    print('Complete for label:', label)

generate_infographics(num_best_brawlers, 'global')
generate_infographics(num_best_brawlers, 'regional')

for i in [1,2,3]:
    global_info = os.path.join(infographics_output_folder, 'global_infographics'+str(i)+'.png')
    pad_add_text(global_info, [40, 0, 0, 0], 35, 15, "GLOBAL", global_info, 'maroon', 10)

for i in [1,2,3]:
    regional_info = os.path.join(infographics_output_folder, 'regional_infographics'+str(i)+'.png')
    pad_add_text(regional_info, [40, 0, 0, 0], 35, 15, "ASIA PACIFIC", regional_info, 'navy', 10)

# add_image(global_info1, './misc_images/masters.png', 2, 8 )