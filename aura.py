import brawlstats
import pandas as pd
from tqdm import tqdm
from datetime import date
import string
import argparse
import requests
import time

c9_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=1839516291'
c9_brawlers_csv = 'output/c9aurac_brawler_levels.csv'
c9_output = 'output/c9aurac_brawler_levels_team.xlsx'

c6_sheet = 'https://docs.google.com/spreadsheets/d/10PciVdfZCxNesRQEBSfdrC9E9zx_t1ZCrJUVtyEaiZ0/gviz/tq?tqx=out:csv&gid=233369826'
c6_brawlers_csv = 'output/c6aurac_brawler_levels.csv'
c6_output = 'output/c6aurac_brawler_levels_team.xlsx'

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
df1, na1  = read_csv(c9_sheet, c9_brawlers_csv, c9_output, 'C9', color_scheme)

color_scheme2 = ["#072094", "#BBC3E8"]
df2, na2 = read_csv(c6_sheet, c6_brawlers_csv, c6_output, 'C6', color_scheme2)