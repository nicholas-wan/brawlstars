# Author: ZSilverZ
# Date: 24 June 2022
# Python Version: 3.7
# Python Libraries Required: brawlstats, tqdm, pandas


import brawlstats
import pandas as pd
from tqdm import tqdm
from datetime import date
import string
import argparse

today = date.today()

# Insert your Brawl Stars Developer's API Key into a file in the same directory 'api_key.txt'
with open("api_key.txt",'r') as f:
    token = f.read()

client = brawlstats.Client(token)

tag = '2YQUPUYJ'

player = client.get_player(tag)