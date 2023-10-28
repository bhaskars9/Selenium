from selenium.webdriver.common.by import By
import time
import boto3
from datetime import datetime as dt
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import pandas as pd

################## common functions ##################

def wait(t):
    time.sleep(t)

def parse_url(base_url,params):
    if hasattr(params, "items"):
        l = []
        for k, v in params.items():
            if(v!=''):
                k = k.replace(' ', '+')
                v = v.replace(' ', '+')
                l.append(k+'='+v)
        l = '&'.join(l)
        return base_url+'?'+l
    else:
        return ''

def send_email(params):
    SENDER = params['from'] # must be verified in AWS SES Email
    RECIPIENT = params['to'] # must be verified in AWS SES Email

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    AWS_REGION = "us-east-1"

    # The subject line for the email.
    SUBJECT = f"Apply to {len(params['jobs'])} {params['role']} jobs"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = params['text']
                
    # Create the HTML body of the email dynamically.
    # BODY_HTML = f"<html><head></head><body><h1>{params['text']}</h1>"
    BODY_HTML = f"<html><head></head><body><h1></h1>"
    for job in params['jobs']:
        title = job["title"]
        company = job["company"]
        location = job["location"]
        url = job["link"]
        anchor_tag = f"<a href='{url}'>{title}</a>"
        BODY_HTML += f"<p>{anchor_tag}, {company} - {location}</p>"
    BODY_HTML += f"<br><p>PS: Good Luck \U0001f600</body></html>"
    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=AWS_REGION)

    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
        
                        'Data': BODY_HTML
                    },
                    'Text': {
        
                        'Data': BODY_TEXT
                    },
                },
                'Subject': {

                    'Data': SUBJECT
                },
            },
            Source=SENDER
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def save_artifact(job_postings, config):
    """
    job_postings : (list) 
    config: (dict) parameters
    """

    if(len(job_postings)):
        df = pd.DataFrame(job_postings)
        location = config['l']
        name = config['name'].replace('.json','')
        unique_file_name = dt.now().strftime(f"%y.%m.%d {name} {location} %I.%M.%S %p")
        df.to_csv(f'artifacts/{unique_file_name}.csv', index=False, header=True)

        send_email({
            'from' : config['from_email'],
            'to' : config['to_email'],
            'role' : name,
            'text' : unique_file_name,
            'jobs': job_postings
        })


####################### indeed functions ###################################
def printjobs(driver):
    # Print job titles
    for div in driver.find_elements(By.CSS_SELECTOR,'div.job_seen_beacon'):
        print(div.find_element(By.CSS_SELECTOR,'h2.jobTitle').text)
    print('*'*50)

def get_job_data(html):
    """
    returns elements containing job data from Indeed
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
    title = elem.find('h2',{'class':'jobTitle'}).get_text()
    link = 'https://ca.indeed.com/viewjob?jk='+elem.find('a',{'class':'jcs-JobTitle'})['data-jk']

    company_info = elem.find('div',{'class':'company_location'})
    company = company_info.find('span',{'data-testid':'company-name'}).get_text()
    location = company_info.find('div',{'data-testid':'text-location'}).get_text()
    job = {
        'title': title,
        'company': company,
        'location': location,
        'link': link,
        'desc': ''
    }
    try:
        job['salary'] = elem.find('div',{'class':'metadata salary-snippet-container'}).get_text()
    except AttributeError as err:
        job['salary'] = 'NA'
    try:
        job['job_type'] = elem.find('svg',{'aria-label':'Job type'}).parent.get_text()
    except AttributeError as err:
        job['job_type'] = 'NA'
    return job


################## linkedin functions #######################################
def printjobs_linkedin(driver):
    # Print job titles
    for div in driver.find_elements(By.CSS_SELECTOR,'class.base-search-card__info'):
        print(div.find_element(By.TAG_NAME, "h3").text.strip())
    print('*'*50)

def get_job_data_linkedin(html):
    """
    returns elements containing job data from linkedin search page
    
    Args:
        html (BeautifulSoup): html page to search
        
    Returns:
        list: list of job elements
    """
    return html.find('ul', {'class':'jobs-search__results-list'}).find_all('li')

def linkedin_parser(elem):
    """
    parses job data from given element
    
    Args:
        elem (BeautifulSoup): element containg job post data
        
    Returns:
        job (dict): list of job elements, next page
    """
    title = item.find('h3').text.strip()
    company = item.find('a', class_='hidden-nested-link')
    location = item.find('span', class_='job-search-card__location')
    parent_div = item.parent
    entity_urn = parent_div['data-entity-urn']
    job_posting_id = entity_urn.split(':')[-1]
    job_url = 'https://www.linkedin.com/jobs/view/'+job_posting_id+'/'
    job = {
            'title': title,
            'company': company.text.strip().replace('\n', ' ') if company else '',
            'location': location.text.strip() if location else '',
            'date': date,
            'job_url': job_url,
        }
    # job = {
    #     'title': elem.find('h3',{'class':'jobTitle'}).get_text(),
    #     'company': elem.find('span',{'class':'companyName'}).get_text(),
    #     'location': elem.find('div',{'class':'companyLocation'}).get_text(),
    #     'link': 'https://ca.indeed.com/viewjob?jk='+elem.find('a',{'class':'jcs-JobTitle'})['data-jk'],
    # }
    try:
        job['salary'] = elem.find('svg',{'aria-label':'Salary'}).parent.get_text()
    except AttributeError as err:
        job['salary'] = 'NA'
    try:
        job['job_type'] = elem.find('svg',{'aria-label':'Job type'}).parent.get_text()
    except AttributeError as err:
        job['job_type'] = 'NA'
    return job

