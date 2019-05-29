# !/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from requests.exceptions import RequestException
import re
from bs4 import BeautifulSoup
from lxml import etree
from pyquery import PyQuery as pq


def get_one_page(url):
    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                'Host': 'maoyan.com'
                }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
        else:
            return None
    except RequestException:
        return None


def parse_by_regex(html):
    pattern = (
      '<dd>.*?<img data-src="(.*?)".*?board-item-content.*?'
    + 'title="(.*?)".*?<p class="star">(.*?)</p>.*?'
    + '<p class="releasetime">(.*?)</p>.*?'
    + 'score.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>'
    )

    pattern = re.compile(pattern, re.S)
    item = re.findall(pattern, html)
    return item

def parse_by_bs4(html): 
    soup = BeautifulSoup(html, 'lxml')
    board_wrapper = soup.select('.board-wrapper dd')
    for dd in board_wrapper:
        img_src = dd.select('.board-img')[0].attrs['data-src']
        title = dd.select('.name')[0].text
        star = dd.select('.star')[0].text.strip()
        releasetime = dd.select('.releasetime')[0].text
        score_integer = dd.select('.integer')[0].text
        score_fraction = dd.select('.fraction')[0].text
        print(img_src, title, star, releasetime, float(score_integer + score_fraction), sep='\n', end='\n\n')

def parse_by_xpath(html):
    html = etree.HTML(html)
    board_wrapper = html.xpath('//dl[@class="board-wrapper"]//dd')
    for dd in board_wrapper:
        yield{
                'img_src': dd.xpath('.//img[@class="board-img"]/@data-src'),
                'title': dd.xpath('.//a[@class="image-link"]/@title'),
                'star': dd.xpath('.//p[@class="star"]/text()')[0].strip(),
                'releasetime': dd.xpath('.//p[@class="releasetime"]/text()'),
                'score': float(''.join(dd.xpath('.//p[@class="score"]//text()')))
        }

def parse_by_pq(html):
    html = pq(html)
    items = html('.board-wrapper dd').items()
    for item in items:
        yield{
                'img_src': item('.board-img').attr('data-src'),
                'title': item('.image-link').attr.title,
                'star': item('.star').text(),
                'releasetime': item('.releasetime').text(),
                'score': item('.score').text()
        }
    

def main():
    url = 'https://maoyan.com/board/4?offset=0' 
    html = get_one_page(url)
    pq_content = parse_by_pq(html)

    for i in pq_content:
        print(i, end='\n\n')


if __name__ == '__main__':
    main()


