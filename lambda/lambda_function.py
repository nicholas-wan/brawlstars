import json
from get_data import *

def lambda_handler(event, context):
    tag = event['tag']
    
    return valid_player_tag(tag)
    
