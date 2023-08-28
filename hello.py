from  includes.config import driver_path, brave_path, database_path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from includes.utils import *
from includes.data_manager import *


# driver config
option = webdriver.ChromeOptions()
option.binary_location = brave_path
driver = webdriver.Chrome(service=Service(driver_path), options=option)

# setup DB
db = DatabaseManager(database_path)
db.connect()
db.create_table()

# navigate to a web page
driver.get('https://ca.indeed.com/jobs?q=azure+data+engineer&fromage=7')

# let it load
wait(5)

job_postings = []

while (True):
    # webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    
    # Get the page source HTML
    page_source = driver.page_source

    # Create a Beautiful Soup object
    soup = BeautifulSoup(page_source, 'html.parser')
    # close popup if it covers the screen
    try:
        # driver.find_element(By.CSS_SELECTOR,'div[aria-modal="true"]').send_keys(Keys.ESCAPE).perform()
        
        # class = mosaic-provider-desktopserp-jobalert-popup
        # id = mosaic-desktopserpjapopup
        # aria-modal="true"

        driver.find_element(By.CSS_SELECTOR,'div[aria-modal="true"]')\
            .find_element(By.CSS_SELECTOR,'button[aria-label="close"]').click()
        print("Popup found")
    except Exception  as e:
        print("Popup not found")

    # scroll down do load
    driver.execute_script("window.scrollBy(0, 4000);")
    
    # get soup obj of page
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # get jobs data
    jobs = get_job_data(soup)
    
    # print jobs titles
    printjobs(driver)

    # parse job data, save to db
    for j in jobs:
            rec = indeed_parser(j)
            jk = rec['link'][33:]
            if(not db.job_exists(jk)):
                # new job posting
                job_postings.append(rec)
                db.insert_record(Job(jk, rec['location'], rec['title']))

    wait(5)

    
    # click on next page if exists
    try:
        # next_page click
        driver.find_element(By.CSS_SELECTOR,'nav[aria-label="pagination"]')\
            .find_element(By.CSS_SELECTOR,'a[aria-label="Next Page"]').click()
    except Exception  as e:
        # print("Element not found:", e)
        print("That's the end, Happy applying :) ")
        break
    
    # wait for page to load
    wait(5)


# pending work
# if(len(job_postings)):
#         # save to database
#         df = pd.DataFrame(job_postings)
#         name = dt.now().strftime(f"%y.%m.%d {role} {location} %I.%M.%S %p")
#         # write csv files
#         df.to_csv(f'indeed_data/{name}.csv', index=False, header=True)
#         # send email
#         load_dotenv()
#         send_email({
#             'from' : os.environ.get("FROM"),
#             'to' : os.environ.get("TO"),
#             'role' : role,
#             'text' : name,
#             'jobs': postings
#         })

wait(1800)


# driver.find_element(By.CSS_SELECTOR,'div.job_seen_beacon').click()

# driver.close()

# interact with page elements
# search_box = browser.find_element_by_name('q')
# search_box.send_keys('Selenium with Python')
# search_box.submit()

# close the browser window
# browser.quit()
