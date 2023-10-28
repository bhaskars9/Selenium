import json
from datetime import datetime as dt
import sys
from includes.scraper import *
from includes.utils import path_exists


file_path = sys.argv[1]
    
if (not os.path.exists(file_path)):
    sys.exit('File or Folder Doesn\'t exists. path =',file_path)

# read json file
with open(file_path, "r") as json_file:
    config = json.load(json_file)

# create webscraper instance
ws = WebScraper(config['paths'], config['name'])

# scrape indeed from a pool of search parameters
for params in config['search_params']:
    ws.scrape_indeed(params=params)

# save local file copy
ws.save_artifact()

# notify new postings (optional, requires aws ses, ) 
ws.email_results(config['email'])
