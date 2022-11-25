import brawlstats
import pandas as pd
from tqdm import tqdm
from datetime import date
import string
import argparse
import requests
import time
from pandasql import sqldf
import seaborn as sns
import warnings
import matplotlib.pyplot as plt
import numpy as np
import os
import dataframe_image as dfi
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from pl_mapping_dict import mapping_dict

warnings.filterwarnings("ignore")

c9_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=1839516291'
c9_brawlers_csv = 'output/c9/c9aurac_brawler_levels.csv'
c9_csv_output = 'output/c9/c9aurac_full_stats.png'
c9_output = './output/c9/c9aurac_brawler_levels_team.xlsx'
c9_team_averages_png = './output/c9/c9_team_averages.png'
c9_barchart = './output/c9/c9_barchart.jpg'

c6_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=233369826'
c6_brawlers_csv = 'output/c6/c6aurac_brawler_levels.csv'
c6_csv_output = 'output/c6/c6aurac_full_stats.png'
c6_output = './output/c6/c6aurac_brawler_levels_team.xlsx'
c6_team_averages_png = './output/c6/c6_team_averages.png'
c6_barchart = './output/c6/c6_barchart.jpg'

comparison = './output/comparison.csv'
comparison_c6_png = './output/c6/c6_comparison.png'
comparison_c9_png = './output/c9/c9_comparison.png'

def clean_string(s):
    try:
        return s.rstrip(' ')
    except:
        return s

def write_excel(df, output, clubname, color_scheme, na):

    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df = pd.concat([df.head(2), df]).reset_index(drop=True)
    dfStyler=df.style.set_properties(**{'text-align': 'center'})
    dfStyler=dfStyler.set_properties(subset=['brawlers_11'],**{'text-align': 'left'})
    dfStyler.to_excel(writer, index=False, sheet_name=clubname+' Brawler Levels')

    workbook = writer.book
    worksheet = writer.sheets[clubname+' Brawler Levels']

    header_format = workbook.add_format({
        "valign": "vcenter",
        "align": "center",
        "bg_color": color_scheme[0],
         "bold": True,
        'font_color': '#FFFFFF'
    })

    #add title
    title = clubname+" Brawler Levels"
    #merge cells
    format = workbook.add_format()
    format.set_font_size(25)
    format.set_font_color("#333333")

    subheader = time.strftime("%Y-%m-%d")
    worksheet.merge_range('A1:AS1', title, format)
    worksheet.merge_range('A2:AS2', subheader)
    
    worksheet.set_row(2, 15) # Set the header row height to 15
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(2, 2, 12)
    worksheet.set_column(7, 7, 70)

    for col_num, value in enumerate(df.columns.values):
        worksheet.write(2, col_num, value, header_format)

    bg = workbook.add_format({'bg_color':color_scheme[1]})

    first_row, last_row = 1, len(df)
    first_col, last_col= 0, 7
    worksheet.conditional_format(first_row, first_col, last_row-na, last_col, 
                                {'type': 'formula',
                                'criteria': 'MOD($B2,2)=0',
                                'format': bg})
    writer.save()

def map_int(num):
    try:
        return int(num)
    except:
        return ''

def truncate_brawlers(s, truncate_brawlers_num):
    s = s.split(', ')
    append_str = ''
    if len(s)>truncate_brawlers_num:
        append_str = ', ... '
    return ', '.join(s[:truncate_brawlers_num])+append_str


def read_csv(gsheet_url, brawler_levels_csv, output, clubname, color_scheme, truncate_brawlers_num=12):
    df = pd.read_csv(gsheet_url, usecols=[1,2])
    df = df.iloc[1:]
    df.columns=['player','team']
    df = df.dropna(subset=['team'])
    df['player'] = df['player'].map(clean_string)
    brawler_df = pd.read_csv(brawler_levels_csv)
    brawler_df['brawlers_11'] = brawler_df['brawlers_11'].map(lambda x: truncate_brawlers(x, truncate_brawlers_num))


    res = brawler_df.merge(df, on='player', how='left')
    na = res[res['team'].isna()]
    if len(na)>0:
        print('----',clubname,'----')
        print('Error for ',len(na),'members')
        print(na)

    res = res.sort_values(by=['team','player'], ascending=True).reset_index(drop=True)
    res = res[['player', 'team', 'tag', 'trophies', 'pl_score','pl_rank','level_9s', 'level_10s', 'level_11s','brawlers_11']]
    res['team'] = res['team'].map(map_int)
    write_excel(res, output, clubname, color_scheme, len(na))

    return res, na

color_scheme = ["#951F06", "#f8dcdc"]

print('----- Generate Team Excel Workbook -----')
print('[Output] '+c9_output)

df1, na1  = read_csv(c9_sheet, c9_brawlers_csv, c9_output, 'C9', color_scheme)
df1 = df1.drop(columns=['brawlers_11'], axis=1)
df1 = df1.fillna('')
dfi.export(df1.style.hide_index(), c9_csv_output)
print('[Output] '+c9_csv_output)

team_q_standard = """
select team,
       count(*) as num_players,
       sum(trophies)/count(trophies) as avg_trophies,
       sum(level_11s)/count(level_11s) as avg_11s,
       ROUND(AVG(CASE WHEN pl_score <> 0 THEN pl_score ELSE NULL END),1) as avg_pl_score,
       group_concat(player) as players
       from df
       group by team
       order by avg_pl_score desc, avg_trophies desc
"""

def process_team(df_value):
    team_q = team_q_standard.replace('df',df_value)
    team1 = sqldf(team_q, globals()).fillna(0)
    team1['players'] = team1['players'].map(lambda x: x.replace(',', ', '))
    team1['rank'] = team1.index+1
    team1['avg_pl_score'] = team1['avg_pl_score']
    team1 = team1[['rank','players','team','num_players','avg_trophies','avg_11s','avg_pl_score']]
    team1['avg_pl_rank'] = team1['avg_pl_score'].map(lambda x: mapping_dict[int(x)])
    team1['avg_pl_score'] = team1['avg_pl_score'].astype('str')
    return team1

team1 = process_team('df1')

color_scheme2 = ["#072094", "#BBC3E8"]
df2, na2 = read_csv(c6_sheet, c6_brawlers_csv, c6_output, 'C6', color_scheme2)
df2 = df2.drop(columns=['brawlers_11'], axis=1)
df2 = df2.fillna('')
dfi.export(df2.style.hide_index(), c6_csv_output)

print('[Output] '+c6_output)
print('[Output] '+c6_csv_output)

team2 = process_team('df2')

def plot_bar(clubname, excel_file, sheetname, output_file):
    df = pd.read_excel(excel_file, sheet_name=sheetname,engine='openpyxl', skiprows=2)
    df = df.sort_values(by=['team','level_11s'])
    df['team'] = df['team'].map(lambda x: 'Team '+str(x))
    # sns.barplot(data=df, x="island", y="body_mass_g", hue="sex")
    fig, ax = plt.subplots(figsize=(20,10))
    sns.barplot(data=df, x="player", y="level_11s",hue='team', dodge=False)
    plt.xticks(rotation=90)
    mean = round(sum(df['level_11s']/len(df)),2)
    plt.axhline(y=np.nanmean(df.level_11s), color='red', linestyle='--', linewidth=2, label='Avg number of p11s = '+str(mean))
    plt.legend(loc='upper left')
    # plt.title(clubname+' Number of Power 11 Brawlers')
    for container in ax.containers:
        ax.bar_label(container)

    plt.savefig(output_file)
print('----- Generate Team Excel Workbook -----')

plot_bar('<C9>',c9_output,'C9 Brawler Levels', c9_barchart)
print('[Output] '+c9_barchart)

plot_bar('<C6>',c6_output,'C6 Brawler Levels', c6_barchart)
print('[Output] '+c6_barchart)


print('----- Converting to PNG -----')

dfi.export(team1.style.hide_index(), c9_team_averages_png)
print('[Output] '+c9_team_averages_png)

dfi.export(team2.style.hide_index(), c6_team_averages_png)
print('[Output] '+c6_team_averages_png)

comparison_df = pd.read_csv(comparison)
cols_to_round = ['Avg 9s', 'Avg 9s','Avg 10s','Avg 11s','Stddev 11s','Avg PL Score']
for col in cols_to_round:
    comparison_df[col] = comparison_df[col].astype(str)

dfi.export(comparison_df.style.hide_index(),comparison_c6_png)
dfi.export(comparison_df.style.hide_index(),comparison_c9_png)

print('[Output] '+c9_team_averages_png)
print('[Output] '+c6_team_averages_png)


print('----- Formatting Image -----')

def add_margin(pil_img, top, right, bottom, left, color):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

def pad_add_text(image_path, margin, font_size, text_y, text_value, output_path, color, border_size):
    im = Image.open(image_path)
    im = add_margin(im, margin[0], margin[1], margin[2], margin[3], 'white')
    im = add_margin(im, border_size, border_size, border_size, border_size, color)
    
    W, H = im.size
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype('font/OpenSans-Bold.ttf', font_size)
    w, h = draw.textsize(text_value, font=font)

    draw.text(((W-w)/2, text_y), text_value, fill="black", font=font)
    im.save(output_path)
    print('[Format]', output_path)

def add_image(img1_path, img2_path, y_coord, resize_factor):
    img1 = Image.open(img1_path)
    img2 = Image.open(img2_path).convert("RGBA")
    
    if resize_factor!=1:
        width, height = img2.size
        img2 = img2.resize((int(width//resize_factor), int(height//resize_factor)))
    
    img1.paste(img2, (img1.size[0]-img2.size[0]-int(0.03*img1.size[0]), y_coord), mask = img2)
    img1.save(img1_path)


# Full Stats
pad_add_text(c9_csv_output, [80, 20, 20, 20], 45, 25, "<C9> Full Stats", c9_csv_output, 'maroon', 20)
pad_add_text(c6_csv_output, [80, 20, 20, 20], 45, 25, "<C6> Full Stats", c6_csv_output, 'navy', 20)

add_image(c9_csv_output, './misc_images/masters.png', 2, 8 )
add_image(c6_csv_output, './misc_images/masters.png', 2, 8 )

# Comparison
pad_add_text(comparison_c9_png, [93, 20, 20, 20], 40, 25, "<C9> & <C6> Comparison Stats", comparison_c9_png, 'maroon', 15)
pad_add_text(comparison_c6_png, [93, 20, 20, 20], 40, 25, "<C9> & <C6> Comparison Stats", comparison_c6_png, 'navy', 15)

add_image(comparison_c9_png, './misc_images/club_logo.png', 25, 6 )
add_image(comparison_c6_png, './misc_images/club_logo.png', 25, 6 )

# Barchart
pad_add_text(c9_barchart, [25, 0, 20, 0], 70, 40, "<C9> Number of Power 11 Brawlers", c9_barchart, 'maroon', 30)
pad_add_text(c6_barchart, [25, 0, 20, 0], 70, 40, "<C6> Number of Power 11 Brawlers", c6_barchart, 'navy', 30)

# add nita logo to barchart
add_image(c9_barchart, './misc_images/nita_brawler_levels.png', 50,1.5)
add_image(c6_barchart, './misc_images/nita_brawler_levels.png', 50,1.5)

# Team Averages
pad_add_text(c9_team_averages_png, [60, 20, 20, 20], 28, 20, "<C9> Team Averages", c9_team_averages_png, 'maroon', 8)
pad_add_text(c6_team_averages_png, [60, 20, 20, 20], 28, 20, "<C6> Team Averages", c6_team_averages_png, 'navy', 8)

add_image(c9_team_averages_png, './misc_images/rank.png', 15, 4)
add_image(c6_team_averages_png, './misc_images/rank.png', 15, 4)
