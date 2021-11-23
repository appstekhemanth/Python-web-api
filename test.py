import pandas as pd
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from base64 import b64decode

import lxml
import json
import os
import argparse

import requests
import urllib
import urllib3
from urllib3.exceptions import InsecureRequestWarning

import datetime
import time
from pathlib import Path

urllib3.disable_warnings(InsecureRequestWarning)
data = pd.read_excel(r'C:\\Users\\Sanjay\\Desktop\\Store_data.xlsx')
data = pd.DataFrame(data["producttype"].unique(), columns=['producttype'])
data['producttype'] = data['producttype'].str.replace(
    '"', 'inch').str.replace('/', '-').str.replace('*', 'x').str.replace(':', ' ')
root = (r'C://Users//Sanjay//Desktop//google//')
dirlist = pd.DataFrame([item for item in os.listdir(
    root) if os.path.isdir(os.path.join(root, item))])
df = pd.DataFrame([x[0]
                   for x in os.walk(r'C://Users//Sanjay//Desktop//google//')])
for i in dirlist:
    for k, j in enumerate(data["producttype"]):
        if i == j:
            data.drop(data.producttype.index[k], axis=0, inplace=True)


pending_products = []
index = 0
products = iter(data["producttype"].unique().tolist())
for product in products:
    index += 1
    if not os.path.isdir(r'C://Users//Sanjay//Desktop//google//'+product):
        Path(r'C://Users//Sanjay//Desktop//google//' +
             product).mkdir(parents=True, exist_ok=True)
    time.sleep(1)
    searchword1 = '+'.join(product.split())
    searchurl = 'https://www.google.co.in/search?q={}&source=lnms&tbm=isch'.format(
        searchword1)

    dirs = searchword1

    chromedriver = 'C://chromedriver.exe'

    # print(os.path.dirname(dirs))
    # if not os.path.exists(dirs):
    #     os.mkdir(dirs)

    t0 = time.time()
    ################################################################################

    try:
        driver = webdriver.Chrome(chromedriver)
    except Exception as e:
        print(f'No found chromedriver in this environment.')
        print(f'Install on your machine. exception: {e}')
        sys.exit()

    driver.set_window_size(1280, 1024)
    driver.get(searchurl)
    time.sleep(1)

    print(f'Getting you a lot of images. This may take a few moments...')

    element = driver.find_element_by_tag_name('body')

    for i in range(30):
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.3)
    try:
        driver.find_element_by_css_selector(
            '#islmp > div > div > div > div.WYR1I > span').click()
        for i in range(50):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)
    except:
        for i in range(10):
            element.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.3)

    print(f'Reached end of page.')
    time.sleep(0.5)

    elements = driver.find_elements_by_xpath('//div[@id="islrg"]')
    page_source = elements[0].get_attribute('innerHTML')
    # page_source = requests.get(searchurl)
    soup = BeautifulSoup(page_source, 'lxml')
    into_class = soup.find(
        'div', attrs={'class': 'islrc', 'jsname': 'r5xl4'})

    lis = []
    length = []
    try:
        count = 0
        for i, j in enumerate(into_class.find_all('img')):
            if count != 10:
                length.append(
                    len([ele for ele in product.lower().split() if(ele in j['alt'].lower())]))
                count += 1
            else:
                break
    except:
        pending_products.append(product)
        next(products, 'No Products found')

    if length:
        for j in [i for i in range(len(length)) if length[i] == max(length)]:
            if into_class.find_all('img')[j].get('src'):
                lis.append(into_class.find_all('img')[j].get('src'))
            elif into_class.find_all('img')[j].get('data-src'):
                lis.append(into_class.find_all('img')[j].get('src'))

    count = 0
    for img_str in lis:
        if "data:image/jpeg;base64," in img_str:
            # Delete the previous "data:image/jpeg;base64,"
            img_str = img_str.split(",")[-1]
            # Replace "%0A" with a newline
            img_str = img_str.replace("%0A", '\n')
            img_data = b64decode(img_str)  # b64decode decoding
            with open('C://Users//Sanjay//Desktop//google//{}//{}_{}.jpeg'.format(product, product, count), 'wb') as fout:
                fout.write(img_data)
                fout.close()
        count += 1

    if count == 0:
        for img_str in lis:
            if "https://" or 'http://' in img_str:
                img_data = requests.get(img_str).content
                with open('C://Users//Sanjay//Desktop//google//{}//{}_{}.jpeg'.format(product, product, count), 'wb') as fout:
                    fout.write(img_data)
                    fout.close()
                count += 1
    driver.close()

    if count == 0:
        pending_products.append(product)
    #################################################################################
    t1 = time.time()
    total_time = t1 - t0
    print(f'\n')
    print(f'Download completed. [Successful count = {count}].')
    print(f'Total time is {str(total_time)} seconds.')
    print(index)
    # break
