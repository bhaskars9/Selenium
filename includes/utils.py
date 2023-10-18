from selenium.webdriver.common.by import By
import time
import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

def wait(t):
    time.sleep(t)

def printjobs(driver):
    # Print job titles
    for div in driver.find_elements(By.CSS_SELECTOR,'div.job_seen_beacon'):
        print(div.find_element(By.CSS_SELECTOR,'h2.jobTitle').text)
    print('*'*50)


def printjobs_linkedin(driver):
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

def get_job_data_linkedin(html):
    """
    returns elements containing job data from linkedin search page
    
    Args:
        html (BeautifulSoup): html page to search
        
    Returns:
        list: list of job elements
    """
    return html.find('ul', {'class':'jobs-search__results-list'}).find_all('li')

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

def linkedin_parser(elem):
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
