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

warnings.filterwarnings("ignore")

c9_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=1839516291'
c9_brawlers_csv = 'output/c9/c9aurac_brawler_levels.csv'
c9_output = './output/c9/c9aurac_brawler_levels_team.xlsx'
c9_team_averages_png = './output/c9/c9_team_averages.png'
c9_barchart = './output/c9/c9_barchart.jpg'

c6_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=233369826'
c6_brawlers_csv = 'output/c6/c6aurac_brawler_levels.csv'
c6_output = './output/c6/c6aurac_brawler_levels_team.xlsx'
c6_team_averages_png = './output/c6/c6_team_averages.png'
c6_barchart = './output/c6/c6_barchart.jpg'

comparison = './output/comparison.csv'
comparison_c6_png = './output/c6/comparison.png'
comparison_c9_png = './output/c9/comparison.png'

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
    res = res[['player', 'team', 'tag', 'trophies', 'level_9s', 'level_10s', 'level_11s','brawlers_11']]
    res['team'] = res['team'].map(map_int)
    write_excel(res, output, clubname, color_scheme, len(na))

    return res, na

color_scheme = ["#951F06", "#f8dcdc"]

print('----- Generate Team Excel Workbook -----')
print('[Output] '+c9_output)

df1, na1  = read_csv(c9_sheet, c9_brawlers_csv, c9_output, 'C9', color_scheme)

team1_q = """
select team,
       sum(trophies)/count(trophies) as avg_trophies,
       sum(level_11s)/count(level_11s) as avg_11s,
       group_concat(player) as players
       from df1
       group by team
       order by avg_trophies desc, avg_11s desc
"""
team1 = sqldf(team1_q, globals())
team1['players'] = team1['players'].map(lambda x: x.replace(',', ', '))
team1['rank'] = team1.index+1
team1 = team1[['rank','players','team','avg_trophies','avg_11s']]

color_scheme2 = ["#072094", "#BBC3E8"]
df2, na2 = read_csv(c6_sheet, c6_brawlers_csv, c6_output, 'C6', color_scheme2)

print('[Output] '+c6_output)

team2_q = """
select team,
       sum(trophies)/count(trophies) as avg_trophies,
       sum(level_11s)/count(level_11s) as avg_11s,
       group_concat(player) as players
       from df2
       group by team
       order by avg_trophies desc, avg_11s desc
"""
team2 = sqldf(team2_q, globals())
team2['players'] = team2['players'].map(lambda x: x.replace(',', ', '))
team2['rank'] = team2.index+1
team2 = team2[['rank','players','team','avg_trophies','avg_11s']]

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

def pad_add_text(image_path, margin, font_size, text_xy, text_value, output_path, color, border_size):
    im = Image.open(image_path)
    im = add_margin(im, margin[0], margin[1], margin[2], margin[3], 'white')
    im = add_margin(im, border_size, border_size, border_size, border_size, color)
    im_new = ImageDraw.Draw(im)
    font = ImageFont.truetype('font/OpenSans-Bold.ttf', font_size)
    im_new.text((text_xy[0], text_xy[1]), text_value, font = font, fill =(0,0,0))
    im.save(output_path)
    print('[Format]', output_path)

# Comparison
pad_add_text(comparison_c9_png, [93, 20, 20, 20], 40, (270, 25), "<C9> & <C6> Comparison Stats", comparison_c9_png, 'maroon', 15)
pad_add_text(comparison_c6_png, [93, 20, 20, 20], 40, (270, 25), "<C9> & <C6> Comparison Stats", comparison_c6_png, 'navy', 15)

# Barchart
pad_add_text(c9_barchart, [25, 20, 20, 20], 70, (455, 40), "<C9> Number of Power 11 Brawlers", c9_barchart, 'maroon', 30)
pad_add_text(c6_barchart, [25, 20, 20, 20], 70, (455, 40), "<C6> Number of Power 11 Brawlers", c6_barchart, 'navy', 30)

# Team Averages
pad_add_text(c9_team_averages_png, [40, 20, 20, 20], 22, (200, 12), "<C9> Team Averages", c9_team_averages_png, 'maroon', 8)
pad_add_text(c6_team_averages_png, [40, 20, 20, 20], 22, (200, 12), "<C6> Team Averages", c6_team_averages_png, 'navy', 8)
