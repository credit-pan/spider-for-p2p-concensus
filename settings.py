import numpy as np
import pandas as pd
import os
from datetime import datetime,timedelta

"""自己设置请求头"""
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
}

"""自己设置路径"""
# 主路径
PATH = 'Y:/P2P舆情监控/'
# 保存爬取文件的路径
SAVE_PATH = PATH + '爬取文件/'
# 比对后文件的路径（该上传程序不包含比对部分）
TARGET_PATH = PATH + '目标文件/'
REPORT_DATE = str(datetime.now())[0:10]
CHECK_DATE = str(datetime.now() - timedelta(days=1))[0:10]
CHECK_DATE_END = datetime.strptime(CHECK_DATE,'%Y-%m-%d')
CHECK_DATE_START = CHECK_DATE_END # - timedelta(days=1)

