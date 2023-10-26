from  includes.config import driver_path, brave_path, database_path
import pandas as pd
import json
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import sys
import argparse

from includes.utils import *
from includes.data_manager import *

file_name = sys.argv[1]
with open('configs/'+file_name, "r") as json_file:
    config = json.load(json_file)
    # print(config)

# Web Driver config
option = webdriver.ChromeOptions()
option.binary_location = config['brave_path']
driver = webdriver.Chrome(service=Service(config['driver_path']), options=option)

# setup DB
db = DatabaseManager(config['database_path'])
db.connect()
db.create_table()

params = {'q' : config['q'],'l' : config['l'],'fromage' :config['fromage'] }
url = parse_url('https://ca.indeed.com/jobs',params)
driver.get(url)
driver.maximize_window()

# let it load
wait(1)
# page refresh
driver.refresh()
# wait for 5 seconds
wait(3)


try:
    driver.find_element(By.CSS_SELECTOR,'div[class="true"]')\
        .find_element(By.CSS_SELECTOR,'button[aria-label="close"]').click()
    print("Popup found")
except Exception  as e:
    # check if its a desktop popup
    try:
        driver.find_element(By.CSS_SELECTOR,'div[id="mosaic-desktopserpjapopup"]')\
        .find_element(By.CSS_SELECTOR,'button[aria-label="close"]').click()
        print("desktop popup found")
    except:
            print("popup not found..")


job_postings = []

while (True):
    for j in driver.find_elements(By.CSS_SELECTOR,'div[class="job_seen_beacon"]'):
        # get basic data
        rec = indeed_parser(BeautifulSoup(j.get_attribute('outerHTML'), 'html.parser'))
        

        if(not db.job_exists(rec['link'])):
            # get the job description
            try:
                j.click()
                # print("posting clicked")
                # set variable
                wait(5)
                desc = driver.find_element(By.CSS_SELECTOR,'div[id="jobDescriptionText"]').text
                rec['desc'] = desc
                # print(desc)
                driver.execute_script("window.scrollBy(0, 150);")
            except Exception  as e:
                print("unable to click on posting")
            
            print(rec['title'])
            # new job posting
            job_postings.append(rec)
            db.insert_record(Job(rec['link'], rec['location'], rec['title'], rec['desc']))

    wait(1)
    
    try:
        nav = driver.find_element(By.CSS_SELECTOR,'nav[aria-label="pagination"]')
    except:
        # single page
        print('single page')
        break
    
    # click on next page if exists
    try:
        nav.find_element(By.CSS_SELECTOR,'a[aria-label="Next Page"]').click()
    except Exception  as e:
        # print("Element not found:", e)
        print('last page reached')
        print("That's the end, Happy applying :) ")
        break
    
    # wait for page to load
    wait(5)

save_artifact(job_postings, config)
wait(1000)
