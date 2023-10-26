from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd
from .data_manager import *
from .utils import *
from datetime import datetime as dt

# branch out to a new file components.py later
def close_notification_popup(driver):
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

def get_job_description(j, driver):
    try:
        j.click()
        # print("posting clicked")
        # wait for it to load description
        wait(5)
        desc = driver.find_element(By.CSS_SELECTOR,'div[id="jobDescriptionText"]').text
        return desc
        # print(desc)
    except Exception  as e:
        print("unable to click on posting",e)
        return 'NA'

def driver_snapshot(driver, name='snapshot'):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    file_name = dt.now().strftime(f" {name} %I%M%S")
    with open(f'{file_name}.html', 'w', encoding="utf-8") as f:
        f.write(soup.prettify())

def goto_nextpage(driver):
    # check navigation element
    try:
        nav = driver.find_element(By.CSS_SELECTOR,'nav[aria-label="pagination"]')
    except Exception as e:
        print('single page')
        # driver_snapshot(driver, 'single_page')
        return False
    
    # click on next page if exists
    try:
        nav.find_element(By.CSS_SELECTOR,'a[aria-label="Next Page"]').click()
        return True
    except Exception  as e:
        # driver_snapshot(driver,'lastpage')
        # print("Element not found:", e)
        print('last page reached')
        return False
    
            

class WebScraper:
    def __init__(self, config, name):
        self.config = config
        self.job_postings = []
        self.name = name
        # put option in init from Web Driver setup

    def scrape_test(self, url='https://www.google.com/'):
        # setup Web Driver
        option = webdriver.ChromeOptions()
        option.binary_location = self.config['brave_path']
        driver = webdriver.Chrome(service=Service(self.config['driver_path']), options=option)

        print(f'Session {driver.session_id} started')
        try:
            driver.get(url)
            print(driver.title)
            wait(10)
            driver.quit()
        except Exception as e:
            print(e)

    def scrape_indeed(self, params):
        """
        params : (dict)
        """
        # setup Web Driver
        option = webdriver.ChromeOptions()
        option.binary_location = self.config['brave_path']
        driver = webdriver.Chrome(service=Service(self.config['driver_path']), options=option)

        # setup DB
        db = DatabaseManager(self.config['database_path'])
        db.connect()
        db.create_table()

        # setup URL
        url = parse_url('https://ca.indeed.com/jobs',params)
        
        # start 
        driver.get(url)
        driver.maximize_window()
        wait(1)
        driver.refresh()
        wait(3)
        close_notification_popup(driver)

        while (True):
            for j in driver.find_elements(By.CSS_SELECTOR,'div[class="job_seen_beacon"]'):
                # parse basic data
                rec = indeed_parser(BeautifulSoup(j.get_attribute('outerHTML'), 'html.parser'))
                # imitate human activity
                driver.execute_script("window.scrollBy(0, 150);")
                if(not db.job_exists(rec['link'])):
                    rec['desc'] = get_job_description(j, driver)
                    # print(rec['title'])
                    self.job_postings.append(rec)
                    db.insert_record(Job(rec['link'], rec['location'], rec['title'], rec['desc']))
            wait(2)

            if(not goto_nextpage(driver)): 
                print("That's the end, Happy applying :) ")
                break
                

        driver.quit()
    
    def save_artifact(self, name=''):
        if(len(self.job_postings)>0):
            df = pd.DataFrame(self.job_postings)
            if(name==''): name = self.name
            file_name = dt.now().strftime(f"%y.%m.%d {name} %I.%M.%S %p")
            df.to_csv(self.config['artifacts_path'] + '/' + file_name + '.csv', index=False, header=True)
        else:
            print('no new jobs to store')
    
    def email_results(self, params, text=''):    
        if(len(self.job_postings)>0):
            send_email({
                'from' : params['from_email'],
                'to' : params['to_email'],
                'role' : self.name,
                'text' : text,
                'jobs': self.job_postings
            })
        else:
            print('no new jobs to mail')
    
    def clear_postings(self):
        self.job_postings = []

