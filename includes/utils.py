from selenium.webdriver.common.by import By
import time

def wait(t):
    time.sleep(t)

def printjobs(driver):
    # Print job titles
    for div in driver.find_elements(By.CSS_SELECTOR,'div.job_seen_beacon'):
        print(div.find_element(By.CSS_SELECTOR,'h2.jobTitle').text)
    print('*'*50)

def get_job_data(html):
    """
    returns elements containing job data
    
    Args:
        html (BeautifulSoup): html page to search
        
    Returns:
        list: list of job elements
    """
    return html.find_all('div',{'class':'job_seen_beacon'})

def indeed_parser(elem):
    """
    parses job data from given element
    
    Args:
        elem (BeautifulSoup): element containg job post data
        
    Returns:
        job (dict): list of job elements, next page
    """
    job = {
        'title': elem.find('h2',{'class':'jobTitle'}).get_text(),
        'company': elem.find('span',{'class':'companyName'}).get_text(),
        'location': elem.find('div',{'class':'companyLocation'}).get_text(),
        'link': 'https://ca.indeed.com/viewjob?jk='+elem.find('a',{'class':'jcs-JobTitle'})['data-jk'],
    }
    try:
        job['salary'] = elem.find('svg',{'aria-label':'Salary'}).parent.get_text()
    except AttributeError as err:
        job['salary'] = 'NA'
    try:
        job['job_type'] = elem.find('svg',{'aria-label':'Job type'}).parent.get_text()
    except AttributeError as err:
        job['job_type'] = 'NA'
    return job


