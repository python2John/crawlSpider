# !/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import os
from urllib.parse import urljoin
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


def get_one_page(url,  flag='text'):        # 'text' 与 'content' 的选择 
    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            if flag == 'text':
                return r.text
            else:
                return r.content
        else:
            return None
    except RequestException:
        return None

def get_single_job592_url(init_url='', page=1):          
    init_url, page = 'https://www.job592.com/doc/hot.html?act=sou&pn={0}&order=hot', 74
    url = []
    resume_filter = ['空白', '英文', '多个']        
    for i in range(1, page+1):
        start_url =init_url.format(i)
        html = get_one_page(start_url)
        if html:
            soup = BeautifulSoup(html, 'lxml')
            resume_url = soup.find_all(attrs={'target':'_blank'})
            for tag in resume_url:
                if 'title' in str(tag):
                    title = tag.attrs['title']
                    for i in resume_filter:
                        if i in title:
                            break
                        url.append(urljoin(start_url, tag.attrs['href']))
    return list(set(url))


# def get_proxy():
    # try:
        # response = requests.get('http://localhost:5555/random')
        # if response.status_code == 200:
            # return response.text
    # except:
        # return None


def crawl_job592():  
    with open('all_url.txt', 'rt', encoding='utf-8') as f:
        urls = eval(f.read())
    resume_download_url = []

    options = webdriver.ChromeOptions()                    
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(chrome_options=options)
    wait = WebDriverWait(browser, 10)
    try:
        for num, url in enumerate(urls[:3]):
            browser.get(url)
            browser.add_cookie({'name':'Hm_lpvt_b223901e6b15b428097be0a23b026674', 'value':'1558840925'})
            browser.add_cookie({'name':'Hm_lvt_b223901e6b15b428097be0a23b026674', 'value':'1558107579,1558109538,1558109604,1558797658'})
            browser.add_cookie({'name':'JSESSIONID', 'value':'950F574AC0C5CA58D0E4CE9AE966EE56'})
            browser.add_cookie({'name':'mk592', 'value':'KnOv0wb_tv2uIX'})
            browser.add_cookie({'name':'rnapl', 'value':'f82df5f71436ccf32b1d4f41c458d000'})
            download_button_1 = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="downDoc-8"]')))
            download_button_1.click()
    
            browser.switch_to_window(browser.window_handles[1])
            download_button_2 = wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/div[2]/div/div[5]/div[1]/a')))
            download_button_2.click()
    
            file_url = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ui-tipbox-content > p > a')))
            print('{0}/{1}'.format(num+1, len(urls[:3])), file_url.get_attribute('href'), sep='    ')
            resume_download_url.append(file_url.get_attribute('href'))
            browser.close()
            browser.switch_to_window(browser.window_handles[0])
    finally:
        with open('resume_download_url.txt', 'wt', encoding='utf-8') as f1:
            f1.write(str(resume_download_url))
        print('{0}/{1} have done'.format(num+1, len(urls[:3])))
         
def url_to_file():
    with open('./resume_download_url.txt', 'rt', encoding='utf-8') as f:
         urls = eval(f.read())
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Cookie': 'mk592=KnOv0wb_tv2uIX; JSESSIONID=5A6367476EDD869AD916F9C5DA56E70F; Hm_lvt_b223901e6b15b428097be0a23b026674=1558109538,1558109604,1558797658,1558853616; rnapl=96412656cff7f20609640ed83ddf6fcd; Hm_lpvt_b223901e6b15b428097be0a23b026674=1558855106'
            }
    for num, url in enumerate(urls[:]):
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            with open('./download_resume/{0}.doc'.format(num+1), 'wb') as f1:
                f1.write(result.content)
        else:
            print('{0}/{1} have finished'.format(num, len(urls[:])))


if __name__ == '__main__':
    a1 = time.time()
    url_to_file()
    a2 = time.time()
    print('共花费了{0}秒'.format(a2-a1))



