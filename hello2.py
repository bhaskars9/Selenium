from  includes.config import driver_path, brave_path, linked_db_path
import pandas as pd
from datetime import datetime as dt
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from includes.utils import *
from includes.data_manager_linkedin import *


# driver config
option = webdriver.ChromeOptions()
option.binary_location = brave_path
driver = webdriver.Chrome(service=Service(driver_path), options=option)

# setup DB
db = DatabaseManager(linked_db_path)
db.connect()
db.create_table()

# navigate to a web page
keywords = "azure data engineer"
# location = "CA"
driver.get(f'https://www.linkedin.com/jobs/search?keywords=Data%20Engineer&location=Canada&f_TPR=r86400&position=1&pageNum=0')

# let it load
wait(5)

job_postings = []

# while (True):
    # webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    
    # Get the page source HTML
page_source = driver.page_source

    # Create a Beautiful Soup object
    # soup = BeautifulSoup(page_source, 'html.parser')
    # close popup if it covers the screen
    # try:
    #     driver.find_element(By.CSS_SELECTOR,'div[aria-modal="true"]')\
    #         .find_element(By.CSS_SELECTOR,'button[aria-label="close"]').click()
    #     print("Popup found")
    # except Exception  as e:
    #     print("Popup not found")

    # scroll down do load
driver.execute_script("window.scrollBy(0, 4000);")
wait(5)
page_source = driver.page_source


    # Print job titles
    # c = 0
    # for div in driver.find_elements(By.CSS_SELECTOR,'ul.jobs-search__results-list > li'):
    #     print(c, div.find_element(By.CSS_SELECTOR,'h3.base-search-card__title').text)
    #     c +=1
    # print('*'*50)
    
    ## CONTINUE SCROLLING UNTIL YOU HIT END
    ## END1: YOU HAVE REACHED ALL JOBS FOR THIS SEARCH
    ## END2: CLICK ON SEE MORE JOBS => SCROLL => CLICK ON SEE MORE => UNTIL YOU REACH END1??
    # get soup obj of page
soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get jobs data
jobs = get_job_data_linkedin(soup)
    
    # print jobs titles
    # printjobs(driver)

    # parse job data, save to db
for j in jobs:
    rec = indeed_parser(j)
    # jk = rec['link'][33:]
    job_postings.append(rec)

        # if(not db.job_exists(jk)):
            # new job posting
            # job_postings.append(rec)
            # db.insert_record(Job(jk, rec['location'], rec['title']))


    
    # click on next page if exists
    # try:
    #     # next_page click
    #     driver.find_element(By.CSS_SELECTOR,'nav[aria-label="pagination"]')\
    #         .find_element(By.CSS_SELECTOR,'a[aria-label="Next Page"]').click()
    # except Exception  as e:
    #     # print("Element not found:", e)
    #     print("That's the end, Happy applying :) ")
    #     break
    
    # wait for page to load
wait(5)



# if(len(job_postings)):
#     # save to database
#     df = pd.DataFrame(job_postings)
#     name = dt.now().strftime(f"%y.%m.%d {role} {location} %I.%M.%S %p")
#     # write csv files
#     df.to_csv(f'artifacts/{name}.csv', index=False, header=True)
#     # send email
#     load_dotenv()
#     send_email({
#         'from' : os.environ.get("FROM"),
#         'to' : os.environ.get("TO"),
#         'role' : role,
#         'text' : name,
#         'jobs': job_postings
#     })

wait(1800)

