"""
本爬虫是爬取网贷天眼的P2P舆情信息-问题平台信息
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
CHECK_DATE_END = settings.CHECK_DATE_END
CHECK_DATE_START = settings.CHECK_DATE_START
# CHECK_DATE_START = datetime.now() - timedelta(days=30)
HOME_URL = 'https://www.p2peye.com'
BASE_URL = 'https://www.p2peye.com/platform/wenti/'
# BASE_URL = 'https://www.p2peye.com/platform/wenti_30/'
COUNT_STOP_POINT = 0


def parse(url):
    global COUNT_STOP_POINT
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    trs = html.xpath('//table[@class="ui-table"]/tbody//tr')
    columns = ['网页链接','标题','平台网址','平台名称','曝光原因','发布时间']
    posts = []
    for tr in trs:
        fall_date = tr.xpath('./td[position() = 2]/text()')[0]
        print(fall_date)
        if CHECK_DATE_START <= datetime.strptime(fall_date,'%Y-%m-%d') <= CHECK_DATE_END:
            sec = randint(1,5)
            print('睡眠中：',sec)
            sleep(sec)
            platform = tr.xpath('.//td[position() = 1]/a/@title')[0]
            link = 'https:' + tr.xpath('.//td[position() = 1]/a/@href')[0]
            reason = tr.xpath('.//td[position() = 5]/text()')[0]
            print(platform,link,reason)
            domain, full_name = parse_detail(link + '/beian/')
            if domain != '无':
                values = [link,full_name,domain,platform,reason,fall_date]
                posts.append(dict(zip(columns,values)))
        else:
            COUNT_STOP_POINT += 1

        if COUNT_STOP_POINT >= 10:
            break
    return posts


def parse_detail(url):
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    full_name = html.xpath('//div[@class="kv borderTop0"]/div[@class="v"]/text()')[0]
    try:
        texts = html.xpath('//div[@class="kvs kvs_baxx"]//div[@class="v"]//text()')
        domain = texts[0]
    except Exception as e:
        print(e)
        domain = '无'
    return domain,full_name


def main():
    posts = parse(BASE_URL)
    if len(posts) >= 1:
        df_posts = pd.DataFrame(posts)
        df_posts = df_posts[['网页链接','标题','平台网址','平台名称','曝光原因','发布时间']][df_posts['平台网址'] != '无'].copy()
        df_posts.to_excel(SAVE_PATH + '网贷天眼' + REPORT_DATE + '.xlsx', encoding='utf-8')
    else:
        print('网贷天眼无数据！')


if __name__ == '__main__':
    main()

