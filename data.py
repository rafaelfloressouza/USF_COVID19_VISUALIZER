from bs4 import BeautifulSoup
import requests
from word2number import w2n
import pandas as pd
from datetime import datetime


def get_number(text):
    try:
        return w2n.word_to_num(text)
    except Exception as e:
        return 1


def parser(text):
    text = text.lower().split()
    num = get_number(text[0])
    if 'tampa' in text and ('student' in text or 'students' in text or 'student-employee:' in text):
        return 'Tampa', 'Student', num
    elif 'tampa' in text and ('employee' in text or 'employees' in text):
        return 'Tampa', 'Employee', num
    elif 'st.' in text and ('student' in text or 'students' in text):
        return 'St. Pete', 'Student', num
    elif 'st.' in text and ('employee' in text or 'employees' in text):
        return 'St. Pete', 'Employee', num
    elif ('health' in text or 'medical' in text) and (
            'employee' in text or 'employees' in text or 'resident' in text or 'residents' in text):
        return 'Health', 'Employee', num
    elif ('health' in text or 'medical' in text) and ('student' in text or 'students' in text):
        return 'Health', 'Student', num
    elif 'sarasota-manatee' in text and ('student' in text or 'students' in text or 'student-employee:' in text):
        return 'Sarasota Manatee', 'Student', num
    elif 'sarasota-manatee' in text and ('employee' in text or 'employees' in text):
        return 'Sarasota Manatee', 'Employee', num
    else:
        return -1, -1, -1


def get_data():
    '''Returns a data frame with COVID-19 Data scraped from USF's COVID-19 website and'''
    url = "https://www.usf.edu/coronavirus/updates/usf-cases.aspx"
    response = requests.get(url)
    pageContent = response.content
    soup = BeautifulSoup(pageContent, 'html.parser')
    dataDiv = soup.find('div', {'class': 'article-body'})

    # Get all the available dates
    datesTag = dataDiv.find_all('h3')
    datesText = []
    for date in datesTag:
        datesText.append(date.get_text())

    # Get all the data regarding cases
    data_dict = {'dates': [], 'locations': [], 'occupations': [], 'cases': []}
    casesTag = dataDiv.find_all('ul')
    for case, date in zip(casesTag, datesText):
        dailyContent = case.find_all('li')
        for text in dailyContent:
            location, occupation, num_cases = parser(text.get_text())
            data_dict['locations'].append(location)
            data_dict['occupations'].append(occupation)
            data_dict['cases'].append(num_cases)
            data_dict['dates'].append((date + ' ' + str(datetime.today().year)).title())

    df = pd.DataFrame(data_dict)
    df = df.reindex(index=df.index[::-1])
    return df.groupby(['dates', 'locations', 'occupations'], sort=False, as_index=False).sum()
