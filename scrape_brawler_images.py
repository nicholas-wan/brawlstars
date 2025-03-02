from selenium import webdriver
import os
import pandas as pd
from selenium.webdriver.common.by import By
from tqdm import tqdm
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--chrome_headless', '-c', choices=['yes','no'], default='yes', type=str, help='yes for headless chrome browser else no')

args = parser.parse_args()

if args.chrome_headless=='yes':
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options = options)
else:
    driver = webdriver.Chrome()

driver.get("https://brawlify.com/brawlers/")
    
elems = driver.find_elements(By.TAG_NAME, "img")
links = [elem.get_attribute('src') for elem in elems]
links = [x for x in links if 'brawler-bs' in x]

headers ={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
print('Downloading brawler images to')
for i in tqdm(range(len(links))):
    url = links[i] 
    fname = os.path.join('maps/brawler_images',links[i].split('/')[-1])
    res = requests.get(url,headers=headers)
    if not os.path.exists(fname):
        with open(fname, 'wb') as f:
            f.write(res.content)
print('Complete')