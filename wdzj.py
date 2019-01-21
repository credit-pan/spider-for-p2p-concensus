"""
本爬虫是爬取网贷之家的P2P舆情信息
"""
import requests
from lxml import etree
import numpy as np
import pandas as pd
from urllib import request
import os
import re
from datetime import datetime,timedelta
from random import randint
from time import sleep
import settings

HEADERS = settings.HEADERS
PATH = settings.PATH
SAVE_PATH = settings.SAVE_PATH
REPORT_DATE = settings.REPORT_DATE
CHECK_DATE = settings.CHECK_DATE
BASE_URL = 'https://bbs.wdzj.com/forum-110-%d.html?orderby=create_time'
COUNT_STOP_POINT = 0


def parse(url):
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    content_divs = html.xpath('//div[@class="detail-ul-list"]//li')
    posts = []
    global COUNT_STOP_POINT
    for content_div in content_divs:
        if COUNT_STOP_POINT < 10:
            datex = content_div.xpath('.//div[@class="clearfix"]//span/a/text()')[0]
            print(datex)
            if str(datetime.strptime(datex,'%Y/%m/%d'))[0:10] == CHECK_DATE:
                link = content_div.xpath('.//div[@class="theme-txt fleft"]/a/@href')[0]
                print(link)
                post = parse_detail(link)
                if post is not None:
                    posts.append(post)
            elif datetime.strptime(datex,'%Y/%m/%d') < datetime.strptime(CHECK_DATE,'%Y-%m-%d'):
                COUNT_STOP_POINT += 1
        sleep(randint(1,5))
    return posts


def parse_detail(url):
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    disclosure_table = html.xpath('//div[@class="post-pub-txt mb12"]//table[@class="post-tab"]//tr')
    print(len(disclosure_table),type(disclosure_table))
    mark = ['平台名称', '平台链接', '曝光原因']
    if len(disclosure_table) > 0:
        try:
            title = html.xpath('//div[@class="post-pub-txt mb12"]//h1[@class="context-title"]/text()')[0]
        except:
            title = 'missing'
        try:
            # post_time = html.xpath('//div[@class="post-pub-txt mb12"]/div[@class="post-time"]/span/text()')[0]
            post_time = html.xpath('//div[@class="post-info-l"]/span[positions()=2]/text()')[0][:10]
            print(post_time)
            # post_time = re.search(r'(\d{4}/\d{2}/\d{2} \d{2}:\d{2})',post_time)
            # post_time = post_time.group()
        except:
            post_time = 'missing'
        mer_name = '无描述'
        link = '无描述'
        reason = '无描述'
        for i,tr in enumerate(disclosure_table):
            if i >= 1:
                key = re.sub(r'\W','',tr.xpath('.//td[position() = 1]/text()')[0])
                value = tr.xpath('.//td[position() = 2]/text()')[0]
                if key == mark[0]:
                    mer_name = value
                elif key == mark[1]:
                    link = value
                elif key == mark[2]:
                    reason = value
        post = {
            '网页链接':url,
            '标题':title,
            '平台网址': link,
            '平台名称': mer_name,
            '曝光原因': reason,
            '发布时间':post_time,
        }
        return post
    else:
        return None


def main():
    # 爬取：获取url,逐个爬取url
    urls = [BASE_URL% (i + 1) for i in range(20)]
    posts = []
    for url in urls:
        if COUNT_STOP_POINT < 10:
            post = parse(url)
            posts.extend(post)
    df_posts = pd.DataFrame(posts)
    df_posts = df_posts[
        ['网页链接','标题','平台网址','平台名称','曝光原因','发布时间']].copy()
    df_posts.to_excel(SAVE_PATH + '网贷之家' + REPORT_DATE + '.xlsx',encoding='utf-8')


if __name__ == '__main__':
    main()
