"""
本爬虫是爬取网贷天眼的P2P舆情信息-论坛信息
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
HOME_URL = 'https://www.p2peye.com'
BASE_URL = 'https://www.p2peye.com/forum-60-%d.html?type=0'

COUNT_STOP_POINT = 0
FIRST_YESTERDAY = 0
COUNT_STOP_POINT_2 = 0

def get_date_regex(date_start, date_end):
    days = (date_end - date_start).days
    return [str(date_start + timedelta(i))[5:10] for i in range(days + 1)]

def parse(url):
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    content_divs = html.xpath('//ul[@class="ui-tabskin-body ui-forumlist"]//li')
    posts = []
    regex = get_date_regex(CHECK_DATE_START,CHECK_DATE_END)
    global COUNT_STOP_POINT
    global FIRST_YESTERDAY
    global COUNT_STOP_POINT_2
    for content_div in content_divs:
        datex = content_div.xpath('.//div[@class="ui-forumlist-info"]//span[last()]/text()')[0][:5]
        print(datex)
        if FIRST_YESTERDAY == 0:
            COUNT_STOP_POINT_2 += 1
            if COUNT_STOP_POINT_2 >= 10:
                break
            if datex in regex:
                FIRST_YESTERDAY = 1
        if FIRST_YESTERDAY == 1:
            if COUNT_STOP_POINT < 10:
                if datex in regex:
                    link = HOME_URL + content_div.xpath('.//div[@class="ui-forumlist-title"]/a/@href')[0]
                    post = parse_detail(link)
                    if post is not None:
                        posts.append(post)
                else:
                    COUNT_STOP_POINT += 1
            else:
                break
        sleep(randint(1,5))
    return posts


def parse_detail(url):
    resp = requests.get(url,headers=HEADERS)
    text = resp.text
    html = etree.HTML(text)
    disclosure_table = html.xpath('//table[@summary="分类信息"]//tr')
    mark = ['平台名称','平台网址','曝光原因']
    if len(disclosure_table) > 0:
        title = html.xpath('//span[@id="thread_subject"]/text()')[0]
        post_time = html.xpath('//ul[@class="ui-article-hd-info-detail-msg"]//em/text()')[0]
        mer_name = '无描述'
        link = '无描述'
        reason = '无描述'
        for tr in disclosure_table:
            key = re.sub(r'\W','',tr.xpath('./th/text()')[0])
            if key == mark[0]:
                mer_name = tr.xpath('./td/text()')[0]
            elif key == mark[1]:
                try:
                    link = tr.xpath('./td/a/@href')[0]
                except:
                    link = tr.xpath('./td/text()')[0]
            elif key == mark[2]:
                reason = tr.xpath('./td/text()')[0]
        post = {
            '网页链接':url,
            '标题':title,
            '平台网址': link,
            '平台名称': mer_name,
            '曝光原因': reason,
            '发布时间':post_time,
        }
        print(post)
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
    if df_posts.shape[0] >= 1:
        df_posts = df_posts[['网页链接', '标题', '平台网址', '平台名称', '曝光原因', '发布时间']].copy()
        df_posts.to_excel(SAVE_PATH + '网贷天眼论坛' + REPORT_DATE + '.xlsx', encoding='utf-8')
    else:
        print('网贷天眼论坛无数据!')


if __name__ == '__main__':
    main()
