import pandas as pd
import os
from IPython.display import HTML
import itertools
import imgkit
import pandas.io.formats.style
from PIL import ImageOps, Image

##############
### Params ###
##############

best_brawlers = 12
images_dir = './brawler_images'
images_path = os.listdir(images_dir)
gamemodes_dir = './gamemode_images'

def clean_brawlers_string(s):
    try:
        return s.replace('\\n',' ')
    except:
        return s

def clean_brawler_name(brawler):
    if brawler=='8-Bit':
        return brawler
    elif brawler=='Mr.P':
        return 'Mr. P'
    elif 'Colonel' in brawler or 'Ruffs' in brawler:
        return 'Ruffs'
    else:
        return brawler.replace('-',' ')
    
def clean_string(s):
    try:
        s = s.split(', ')
        s = [(x.replace('%','')) for x in s]
        return ', '.join(s)
    except:
        return s

def round_string(s):
    try:
        s = s.split(', ')
        s = [str(int(float(x))) for x in s]
        return ', '.join(s)
    except:
        return s
    
def nth_repl(s, sub, repl, n):
    try:
        find = s.find(sub)
        # If find is not -1 we have found at least one match for the substring
        i = find != -1
        # loop util we find the nth or we find no match
        while find != -1 and i != n:
            # find + 1 means we start searching from after the last match
            find = s.find(sub, find + 1)
            i += 1
        # If i is equal to n we found nth match so replace
        if i == n:
            return s[:find] + repl + s[find+len(sub):]
        return s
    except:
        return s

def path_to_image_html(path, width='30'):
    return '<img src="'+ path + '" width="{}" >'.format(width)

def filter_brawler_df(min_usage_rank = 40, num_best_brawlers = 12):
    df = pd.read_csv('brawlers.csv')
    df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)
    df

    new_best_brawlers_list = []
    new_win_rates_list = []
    new_usage_rank_list = []
    for i in range(len(df)):
        temp_df = pd.DataFrame({'brawlers':df.iloc[i]['best_brawlers'].split(', '), 'win_rates': df.iloc[i]['win_rates'].split(', '), 'usage_rank':df.iloc[i]['usage_rank'].split(', ')})
        temp_df['usage_rank'] = temp_df['usage_rank'].map(int)
        temp_df = temp_df[temp_df['usage_rank']<= min_usage_rank].head(num_best_brawlers).reset_index(drop=True)
        brawlers = ', '.join(temp_df['brawlers'])
        win_rates = ', '.join(temp_df['win_rates'])
        temp_df['usage_rank'] = temp_df['usage_rank'].map(str)
        usage_rank = ', '.join(temp_df['usage_rank'])

        new_best_brawlers_list.append(brawlers)
        new_win_rates_list.append(win_rates)
        new_usage_rank_list.append(usage_rank)

    df['best_brawlers'] = new_best_brawlers_list
    df['win_rates'] = new_win_rates_list
    df['usage_rank'] = new_usage_rank_list

    return df
    
def get_best_brawlers(num_best_brawlers):
    df = filter_brawler_df()[['best_brawlers']]
    df['best_brawlers'] = df['best_brawlers'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))
    df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)

    brawlers = {}
    brawlers_freq = {}
    for i in range(len(df)):
        brawlers_list = df.iloc[i]['best_brawlers'].split(', ')
        for j in range(len(brawlers_list)):
            if brawlers_list[j] not in brawlers:
                brawlers[brawlers_list[j]] = len(brawlers_list)-j 
                brawlers_freq[brawlers_list[j]] = 1
            else:
                brawlers[brawlers_list[j]] += len(brawlers_list)-j 
                brawlers_freq[brawlers_list[j]]+=1
        
    def print_dataframe(df):
        df.columns = ['brawlers','score']
        df = df.sort_values(by=['score'],ascending=False).reset_index(drop=True)
        df.index+=1
        df['brawlers'] = df['brawlers'].map(lambda x: images[x])
        return df

    df = pd.DataFrame.from_dict([brawlers_freq]).T.reset_index()
    df = print_dataframe(df)
    df.columns = ['brawlers','frequency']

    df2 = pd.DataFrame.from_dict([brawlers]).T.reset_index()
    df2 = print_dataframe(df2)

    def get_best_maps():
        df = pd.read_csv('brawlers.csv')[['map','best_brawlers','win_rates']]
        df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)
        df['best_brawlers'] = df['best_brawlers'].str.split(', ')
        df['win_rates'] = df['win_rates'].str.split(', ')
        brawler_set = sorted(list(set(list(itertools.chain(*df['best_brawlers'])))))

        brawler_map_dict = {}
        for brawler in brawler_set:
            best_maps = []
            for i in range(len(df)):
                best_brawlers = df.iloc[i]['best_brawlers']
                win_rates = df.iloc[i]['win_rates']
                mapname = df.iloc[i]['map']
                if brawler in best_brawlers:
                    best_maps.append([mapname, win_rates[best_brawlers.index(brawler)]])
            brawler_map_dict[brawler] = best_maps

        brawler_map_dict
        df = pd.DataFrame(brawler_set)
        df.columns = ['brawlers']
        df['best_maps'] = df['brawlers'].map(lambda x:brawler_map_dict[x])
        df['best_maps'] = df['best_maps'].map(lambda x: sorted(x, key=lambda y:y[1])[::-1][:3])
        df['best_maps'] = df['best_maps'].map(lambda x: ', '.join([y[0] for y in x]))
        df['brawlers'] = df['brawlers'].map(lambda x: images[x])
        return df

    best_maps = get_best_maps()

    df3 = df.merge(df2, on=['brawlers']).head(num_best_brawlers)
    df4 = df3.merge(best_maps, on=['brawlers'])

    columns = ['best_map1', 'best_map2','best_map3']
    df4[columns] = df4['best_maps'].str.split(', ', expand=True)
    df4 = df4.drop(['best_maps'],axis=1)

    def get_gamemode_dict():
        df = pd.read_csv('brawlers.csv')[['gamemodes','map']]
        return dict(zip(df['map'], df['gamemodes']))

    gamemode_dict = get_gamemode_dict()

    df4['mode1'] = df4['best_map1'].map(lambda x: images[gamemode_dict[x]])
    df4['mode2'] = df4['best_map2'].map(lambda x: images[gamemode_dict[x]])
    df4['mode3'] = df4['best_map3'].map(lambda x: images[gamemode_dict[x]])
    
    df4 = df4[['brawlers','frequency','score','mode1','best_map1','mode2','best_map2','mode3','best_map3']]
    df4.columns = ['brawlers','freq','weighted_score','1','bestmap1','2','bestmap2','3','bestmap3']
    df4 = df4.sort_values(by=['freq', 'weighted_score'], ascending=False).reset_index(drop=True)
    df4.index+=1

    # Overall usage rank
    def get_usage_rank(best_brawler_list):
        df = pd.read_csv('brawlers.csv')
        dict_list = []
        for i in range(len(df)):
            dict_list.append(dict(zip(df.iloc[i]['best_brawlers'].split(', '), df.iloc[i]['usage_rank'].split(', '))))

        avg_list = []
        for brawler in best_brawler_list:
            sum_of_ranks = 0
            for d in dict_list:
                sum_of_ranks+= int(d[brawler])
            avg_list.append(int(sum_of_ranks/len(dict_list)))
           
        return avg_list
    df4['avg_usage_rank'] = get_usage_rank(list(df4['brawlers'].map(lambda x: os.path.basename(x).replace('.png',''))))

    df4['brawlers'] = df4['brawlers'].map(lambda x: path_to_image_html(x, width=40))
    for num in [str(x) for x in range(1, 4)]:
        df4[num] = df4[num].map(lambda x: path_to_image_html(x, width=30))

    df4.columns = ['brawlers','freq','weighted_score','','bestmap1','','bestmap2','','bestmap3','avg_usage_rank']

    return df4

def get_best_brawlers_map(num_best_brawlers):
    df = filter_brawler_df()
    df['best_brawlers'] = df['best_brawlers'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))
    df['win_rates'] = df['win_rates'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))
    df['usage_rank'] = df['usage_rank'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))

    df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)
        
    columns = [str(x) for x in list(range(1,best_brawlers+1))]
        
    df[columns] = df['best_brawlers'].str.split(', ', best_brawlers-1, expand=True)

    for col in columns+['gamemodes']:
        df[col] = df[col].map(images)

    df = df.drop(['best_brawlers'],axis=1)
    df['win_rates'] = df['win_rates'].map(clean_string)
    df['win_rates'] = df['win_rates'].map(round_string)
    df['win_rates'] = df['win_rates'].map(lambda s: nth_repl(s, ", ","<br>",best_brawlers/3))
    df['usage_rank'] = df['usage_rank'].map(clean_string)
    df['usage_rank'] = df['usage_rank'].map(lambda s: nth_repl(s, ", ","<br>",best_brawlers/3))
    df = df.rename(columns={"num_brawlers": "n"})
    df = df[['gamemodes','map']+columns+['win_rates','usage_rank','n']]
    df.index += 1

    for col in columns+['gamemodes']:
        df[col] = df[col].map(lambda x: path_to_image_html(x, width=35))
    return df

def get_images_dict():
    df = pd.read_csv('brawlers.csv')

    images = {}
    for image in images_path:
        images[clean_brawler_name(image.replace('.png',''))] = os.path.join(images_dir, image)
        
    list_of_gamemodes = df['gamemodes']

    for gamemode in list_of_gamemodes:
        fname = gamemode.replace(' ','-')+'.png'
        images[gamemode] = os.path.join(gamemodes_dir, fname)

    return images

images = get_images_dict()

team_tags_silver = ['#C9LR0R0V','#UCY09URC','#2YQUPUYJ'] #C9 - Silver, Blue, Hogg
team_tags_tribe_c6 = ['#V8VRPRYQ','#89GV9UG9Q','#C29RQJLU'] # C6 Tribe
team_tags_tribe_c9 = ['#2PR80P8CU','#9C0UUJVJ','#J2RLUJP2'] # C9 Tribe

def get_best_brawlers_checklist(best_brawlers_df, club, team_tags = ['#C9LR0R0V','#UCY09URC','#2YQUPUYJ']):
    if club=='c9':
        players = pd.read_csv('../output/c9aurac_brawler_levels.csv')
    else:
        players = pd.read_csv('../output/c6aurac_brawler_levels.csv')

    players = players[players['tag'].isin(team_tags)][['player','level_11s','brawlers_11']].reset_index(drop=True)

    df = best_brawlers_df.copy()[['brawlers','freq','weighted_score']].reset_index(drop=True)
    df['names'] = df['brawlers'].map(lambda x:os.path.basename(x).replace('.png',''))
    df['names'] = df['names'].map(lambda x:x.upper())
    df = df.set_index('names')
    player_list = list(players['player'])
    for player_name in player_list:
        df[player_name]=''
        brawler_list = list(players[players['player']==player_name]['brawlers_11'])[0].split(', ')
        for brawler in brawler_list:
            if brawler in df.index:
                df.at[brawler, player_name]=1
    df = df.reset_index(drop=True)
    df.index+=1
    return df

def write_to_html_file(df, title='', filename='out.html'):
    '''
    Write an entire dataframe to an HTML file with nice formatting.
    '''

    result = '''
<html>
<head>
<style>
    body {
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    }
    table {
      border: none;
      border-collapse: collapse;
      border-spacing: 0;
      color: black;
      font-size: 12px;
      table-layout: fixed;
    }
    thead {
      border-bottom: 1px solid black;
      vertical-align: bottom;
    }
    tr, th, td {
      text-align: right;
      vertical-align: middle;
      padding: 0.5em 0.5em;
      line-height: normal;
      white-space: normal;
      max-width: none;
      border: none;
    }
    th {
      font-weight: bold;
    }
    tbody tr:nth-child(odd) {
      background: #f5f5f5;
    }
</style>
</head>
<body>
    '''
    result += '<h2> %s </h2>\n' % title
    if type(df) == pd.io.formats.style.Styler:
        result += df.render()
    else:
        result += df.to_html(classes='wide', escape=False)
    result += '''
</body>
</html>
'''
    with open(filename, 'w') as f:
        f.write(result)
    return result

options = {
  "enable-local-file-access": None
}

def df_to_png(df, output_png):
    write_to_html_file(df, filename='temp.html')
    imgkit.from_file('temp.html', output_png, options=options)
    if output_png == 'infographics/infographics1.png':
        img = Image.open(output_png)
        border = (0, 0, 260, 0) # left, top, right, bottom
        img = ImageOps.crop(img, border)
        img.save(output_png)
        
    if output_png == 'infographics/infographics_checklist_team5.png':
        img = Image.open(output_png)
        border = (0, 0, 625, 0) # left, top, right, bottom
        img = ImageOps.crop(img, border)
        img.save(output_png)
            
    if output_png == 'infographics/infographics_checklist_team2.png':
        img = Image.open(output_png)
        border = (0, 0, 580, 0) # left, top, right, bottom
        img = ImageOps.crop(img, border)
        img.save(output_png)

    os.remove('temp.html')
    print('Complete, image saved to:', output_png)