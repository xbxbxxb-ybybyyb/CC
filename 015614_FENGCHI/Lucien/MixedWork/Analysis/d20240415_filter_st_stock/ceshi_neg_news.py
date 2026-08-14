# coding: utf-8
# Author：fengchi863
# Date ：2024/4/17 14:18

import datetime as dt
import re
import os
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData

from MixedWork.GreyStockGenerator import IO

nd = NewsData()
s = FactorData()
path_user = '/data/user/015614/daily/灰名单生成/黑名单/20240417测试/'
os.makedirs(path_user, exist_ok=True)
# ST预警股票黑名单：当前年度，发布可能ST警示的股票，在预计年报发布前10天。

# 读取日期
date = '20240201'
# date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
lastdate = s.tradingday(date, -2)[0]  # 上一交易日
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '1231'  # 上一年度报告期
last_year_last_month_dt = pd.to_datetime(last_year + '1201')  # 公告读取区间

info_list = []
info = nd.getNegNewsByTime(last_year_period, date)
