#!/bin/bash 
python_path=/opt/anaconda3/envs/brawlstars/bin/python

cd /Users/nick/Desktop/brawlstars
$python_path -u top_pl_players.py >> logs/top_pl_players.txt ;
$python_path -u generate_infographics_pro.py >> logs/generate_infographics_pro.txt