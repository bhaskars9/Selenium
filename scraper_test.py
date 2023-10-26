from includes.scraper import *
import json



file_name = 'config.json'

with open(file_name,'r') as json_file:
    config = json.load(json_file)



ws = WebScraper(config['paths'], config['name'])

ws.scrape_indeed(params = config['search_params'])

ws.save_artifact()

ws.email_results(config['email'])



















# selenium_config = config['selenium']
# email_config = config['email']
# search_config = config['search']






# ws.scrape_test('https://www.nseindia.com/market-data/live-market-indices')
# ws.scrape_test('https://www.nseindia.com/api/allIndices') 
# ws.scrape_test('https://www.nseindia.com/api/allIndices') 

# if(ws.driver.title == 'Resource not found'):
#     ws.driver.refresh()