# !/usr/bin/env python
# -*- coding:utf-8 -*-


import re
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


def get_one_page(url):
    try:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive',
                'Host': 'www.dianping.com',
                'Cookie': '_lxsdk_cuid=1677c04beb7c8-0175d4bfe0d576-47e1039-100200-1677c04beb7c8; _lxsdk=1677c04beb7c8-0175d4bfe0d576-47e1039-100200-1677c04beb7c8; _hc.v=1f8027ab-5caa-576c-db34-e2fe4508dd5d.1543973945; s_ViewType=10; cy=219; cye=dongguan; _lx_utm=utm_source%3DBaidu%26utm_medium%3Dorganic; Hm_lvt_e6f449471d3527d58c46e24efb4c343e=1558492858,1558626656; _lxsdk_s=16afc02ce9f-29c-a93-e39%7C%7C52',
                'Upgrade-Insecure-Requests': '1'
        }
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r.text
        else:
            return None
    except RequestException:
        return None

def numbers(num_url, num_css_url):
    num_str_content = requests.get(num_url).text
    num_css_content = requests.get(num_css_url).text

    soup = BeautifulSoup(num_str_content, 'lxml')
    num_str = soup.find_all(name='text')
    num_str = [i.text for i in num_str]

    b = re.findall('\s*\.(af.*?)\{background:\s*\-(.*?)\.0px\s*\-(.*?)\.0px;\}', num_css_content, re.S)
    rows1 = [int(i[2]) for i in b]
    rows2 = sorted(list(set(rows1)))     # [14, 52, 86, 132]
    cols1 = [int(i[1]) for i in b]
    cols2 = sorted(list(set(cols1)))     # 按等差数列来看(过滤掉不符合等差的值)，最小项为 8，最大值为 582，公差为 14，共 42 个
    b = [i for i in b if (int(i[1])-8) % 14 == 0]
    results, nums = [], []
    for i in b:
        results.append(i[0])
        if int(i[2]) == rows2[0]:
            nums.append(num_str[0][int((int(i[1]) - 8) /14)])
        if int(i[2]) == rows2[1]:
            nums.append(num_str[1][int((int(i[1]) - 8) /14)])
        if int(i[2]) == rows2[2]:
            nums.append(num_str[2][int((int(i[1]) - 8) /14)])
        if int(i[2]) == rows2[3]:
            nums.append(num_str[3][int((int(i[1]) - 8) /14)])
    temp = zip(results, nums)
    changedict = {}
    for flag, num in temp:
        changedict.update({'<d class="{flag}"></d>'.format(flag=flag):num})

    # changedict.update({'&nbsp;':' '})
    changedict.update({'\xa0':' '})
    return changedict

def change(dic, text):
    for key, value in dic.items():
        text = text.replace(key, value)
    return text

def score(url, changedict):
    html = get_one_page(url)
    if html:
        soup = BeautifulSoup(html, 'lxml')
        
        inf = {}
        # inf['tel']=re.findall(r'</span> (.*?) </p>',change(changedic,str(soup.find('p',class_='expand-info tel'))))[0]
        # inf['review']=re.findall(r'> (.*?) 条评论',change(changedic,str(soup.find('span',id='reviewCount'))))[0]
        
        info = soup.find_all(attrs={'class':'brief-info'})
        comment_score = info[0].find(attrs={'id':'comment_score'}).find_all(attrs={'class':'item'})

        inf['reviewCount'] = change(changedict, ''.join(map(str, info[0].find(attrs={'id':'reviewCount'}).children)))
        inf['avgPriceTitle'] = change(changedict, ''.join(map(str, info[0].find(attrs={'id':'avgPriceTitle'}).children)))
        inf['kouwei_score'] = change(changedict, ''.join(map(str, comment_score[0].children)))
        inf['huanjing_score'] = change(changedict, ''.join(map(str, comment_score[1].children)))
        inf['service_score'] = change(changedict, ''.join(map(str, comment_score[2].children)))
        inf['tel'] = change(changedict, ''.join(list(map(str, soup.find(attrs={'class':'expand-info tel'}).children))[2:]))
        print(inf)

    else:
        print('已多次请求，IP限频，暂时解决可到浏览器刷新网址，按操作通过验证中心')
    

if __name__ == '__main__': 
    url = 'http://www.dianping.com/shop/17213595'
    num_url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/a168a2721d3791f068a6174ba719bb58.svg'
    num_css_url = 'http://s3plus.meituan.net/v1/mss_0a06a471f9514fc79c981b5466f56b91/svgtextcss/554ebd27bc8118a34eb112aa67a54f04.css'

    changedict = numbers(num_url, num_css_url)
    score(url, changedict)
        
