import pandas as pd
import os
from IPython.display import HTML
import itertools
import imgkit
import pandas.io.formats.style
from PIL import ImageOps, Image, ImageDraw, ImageFont

##############
### Params ###
##############

project_directory = os.getcwd()
best_brawlers = 12
images_dir = os.path.join(project_directory, 'maps/brawler_images')
images_path = os.listdir(images_dir)
gamemodes_dir = os.path.join(project_directory, 'maps/gamemode_images')
brawler_data_csv = os.path.join(project_directory, 'maps/pro_battles.csv')

def clean_brawlers_string(s):
    try:
        return s.replace('\\n',' ').replace('-',' ')
    except:
        return s

def clean_brawler_name(brawler):
    brawler = brawler.replace('-',' ')
    return brawler
    
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
    return '<img src="file:///'+ path + '" width="{}" >'.format(width)

def filter_brawler_df(num_best_brawlers = 12):
    df = pd.read_csv(brawler_data_csv)
    df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)
    df

    new_best_brawlers_list = []
    new_win_rates_list = []
    new_use_rates_list = []
    for i in range(len(df)):
        temp_df = pd.DataFrame({'brawlers':df.iloc[i]['best_brawlers'].split(', '), 'win_rates': df.iloc[i]['win_rates'].split(', '), 'use_rates':df.iloc[i]['use_rates'].split(', ')})
        brawlers = ', '.join(temp_df['brawlers'])
        win_rates = ', '.join(temp_df['win_rates'])
        use_rates = ', '.join(temp_df['use_rates'])

        new_best_brawlers_list.append(brawlers)
        new_win_rates_list.append(win_rates)
        new_use_rates_list.append(use_rates)

    df['best_brawlers'] = new_best_brawlers_list
    df['win_rates'] = new_win_rates_list
    df['use_rates'] = new_use_rates_list

    return df
    
def get_best_brawlers(num_best_brawlers, label):
    df = filter_brawler_df()
    df = df[df['label']==label].reset_index(drop=True)
    df = df[['best_brawlers']]
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
        df['brawler_names'] = df['brawlers']
        df['brawlers'] = df['brawlers'].map(lambda x: images[x])
        return df

    df = pd.DataFrame.from_dict([brawlers_freq]).T.reset_index()
    df = print_dataframe(df)
    df.columns = ['brawlers','frequency','brawler_names']

    rates = calculate_rates()
    df = df.merge(rates, on='brawler_names', how='left')

    df2 = pd.DataFrame.from_dict([brawlers]).T.reset_index()
    df2 = print_dataframe(df2)

    def get_best_maps():
        df = pd.read_csv(brawler_data_csv)[['map','best_brawlers','win_rates']]
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
        df = pd.read_csv(brawler_data_csv)[['gamemodes','map']]
        return dict(zip(df['map'], df['gamemodes']))

    gamemode_dict = get_gamemode_dict()

    df4['mode1'] = df4['best_map1'].map(lambda x: images[gamemode_dict[x]])
    df4['mode2'] = df4['best_map2'].map(lambda x: images[gamemode_dict[x]])
    df4['mode3'] = df4['best_map3'].map(lambda x: images[gamemode_dict[x]])
    
    df4 = df4[['brawlers','frequency','score','overall_win_rate','overall_use_rate','mode1','best_map1','mode2','best_map2','mode3','best_map3']]
    df4.columns = ['brawlers','freq','weighted_score','overall_win_rate','overall_use_rate','1','bestmap1','2','bestmap2','3','bestmap3']
    df4 = df4.sort_values(by=['freq', 'weighted_score'], ascending=False).reset_index(drop=True)
    df4.index+=1

    df4['brawlers'] = df4['brawlers'].map(lambda x: path_to_image_html(x, width=40))
    for num in [str(x) for x in range(1, 4)]:
        df4[num] = df4[num].map(lambda x: path_to_image_html(x, width=30))

    df4.columns = ['brawlers','freq','weighted_score','overall_win_rate','overall_use_rate','','bestmap1','','bestmap2','','bestmap3']

    return df4

def get_best_brawlers_map(num_best_brawlers, label):
    df = filter_brawler_df()
    df = df[df['label']==label].reset_index(drop=True)
    df['best_brawlers'] = df['best_brawlers'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))
    df['win_rates'] = df['win_rates'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))
    df['use_rates'] = df['use_rates'].map(lambda x: ', '.join(x.split(', ')[:num_best_brawlers]))

    df['best_brawlers'] = df['best_brawlers'].map(clean_brawlers_string)
        
    columns = [str(x) for x in list(range(1,best_brawlers+1))]
        
    df[columns] = df['best_brawlers'].str.split(', ', best_brawlers-1, expand=True)

    for col in columns+['gamemodes']:
        df[col] = df[col].map(images)

    df = df.drop(['best_brawlers'],axis=1)
    df['win_rates'] = df['win_rates'].map(clean_string)
    df['win_rates'] = df['win_rates'].map(round_string)
    df['win_rates'] = df['win_rates'].map(lambda s: nth_repl(s, ", ","<br>",best_brawlers/3))
    df['use_rates'] = df['use_rates'].map(clean_string)
    df['use_rates'] = df['use_rates'].map(lambda s: nth_repl(s, ", ","<br>",best_brawlers/3))
    df = df[['gamemodes','map']+columns+['win_rates','use_rates','num_battles']]
    df = df.rename(columns={'num_battles':'n_battles'})
    df['map'] = df['map'].map(lambda x: x.title())
    df.index += 1

    for col in columns+['gamemodes']:
        df[col] = df[col].map(lambda x: path_to_image_html(x, width=35))
    return df

def get_images_dict():
    df = pd.read_csv(brawler_data_csv)

    images = {}
    for image in images_path:
        images[str.lower(clean_brawler_name(image.replace('.png','')))] = os.path.join(images_dir, image)
        
    list_of_gamemodes = df['gamemodes']

    for gamemode in list_of_gamemodes:
        fname = gamemode.replace(' ','-')+'.png'
        images[str.lower(gamemode)] = os.path.join(gamemodes_dir, fname)

    return images

images = get_images_dict()

def calculate_rates():
    df = pd.read_csv(os.path.join(project_directory, 'battle_logs/battle_logs.csv'))

    res = []
    unique_brawlers = set(df['brawler_name'])
    for brawler in unique_brawlers:
        temp_df = df[df['brawler_name']==brawler]
        victories = len(temp_df[temp_df['battle.result']=='victory'])
        win_rate = victories / len(temp_df)
        win_rate = str(round(win_rate*100,1))+'%'
        use_rate = len(temp_df) / len(df)
        use_rate = str(round(use_rate*100,1))+'%'
        res.append({'brawler_names':str.lower(brawler), 'overall_win_rate':win_rate,'overall_use_rate':use_rate})

    res = pd.DataFrame(res)
    return res

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
    print('Writing Image for:', output_png)
    html_file=os.path.join(project_directory, 'temp.html')
    write_to_html_file(df, filename=html_file)
    imgkit.from_file(html_file, output_png, options=options)
    if 'infographics1.png' in output_png:
        img = Image.open(output_png)
        w, h = img.size
        img.crop((0,0,w-130,h)).save(output_png)

    os.remove(html_file)
    print('Complete, image saved to:', output_png)


def copyright_apply(input_image_path,
                   output_image_path,
                   text):
    photo = Image.open(input_image_path)
    
    #Store image width and height
    w, h = photo.size
    
    # make the image editable
    drawing = ImageDraw.Draw(photo)
    font = ImageFont.truetype("font/OpenSans-Bold.ttf", 18)
    
    #get text width and height
    text = text + " "
    text_w, text_h = drawing.textsize(text, font)
    
    pos = w - text_w, (h - text_h) - 10
    
    c_text = Image.new('RGB', (text_w, (text_h)), color = '#000000')
    drawing = ImageDraw.Draw(c_text)
    
    drawing.text((0,0), text, fill="#ffffff", font=font)
    c_text.putalpha(100)
   
    photo.paste(c_text, pos, c_text)
    photo.save(output_image_path)
    
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

