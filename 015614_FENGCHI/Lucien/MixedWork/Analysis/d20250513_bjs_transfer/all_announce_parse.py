import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import re

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.textdata import NewsData
from tqdm import tqdm
from MixedWork.GreyStockGenerator import IO

nd = NewsData()
s = FactorData()
path_user = '/data/user/015614/daily/灰名单生成/黑名单/'
path_group = '/data/group/800463/stock_list/'
# ST预警股票黑名单：当前年度，发布可能ST警示的股票，在预计年报发布前10天。

# 读取日期
# date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'),-1)[0] #该日开盘前早上运行
import sys
if len(sys.argv) < 2:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    # date = '20250102'
else:
    date = sys.argv[1]
# date = '20250415'
date_dt = pd.to_datetime(date)
lastdate = s.tradingday(date, -2)[0]  # 上一交易日
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 1)  # 上一年度
last_year_period = last_year + '1231'  # 上一年度报告期
# last_year_period = '20231231'  # 上一年度报告期    # 20250103：防止年初读取不到公告，读取内容为空
last_year_last_month_dt = pd.to_datetime(last_year + '1201')  # 公告读取区间

# 读取基本数据
data = IO.read_data([last_year_period, date], columns=['close']
                    , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
stock_list = data['close'].unstack().columns  # 股票列表

info_list = []
start_date = s.tradingday(date, -5)[0]  # 上一交易日
for stock in tqdm(stock_list):
    if stock[-2:] not in ['SZ', 'SH', 'BJ']:
        continue
    info = nd.getAnnouncement([stock], str(last_year_period), str(date))
    if len(info) == 0:
        continue

    info = info[info['PUBDATE'] >= last_year_last_month_dt]
    info = info.rename(columns={'PUBDATE': 'dt'})
    info['Ticker'] = stock
    info['newsID'] = info['ORIGINALCODE'].astype(str)
    info = info[['dt', 'Ticker', 'TEXTTITLE', 'newsID']]
    info_list.append(info)
news_info = pd.concat(info_list, ignore_index=True)
news_info = news_info.sort_values(['Ticker', 'dt'])
news_info.to_pickle('/data/user/015614/junkData/news_all.pkl')
print(len(news_info))
news_info = pd.read_pickle('/data/user/015614/junkData/news_all.pkl')

# 筛选标题
news_info = news_info[news_info['TEXTTITLE'].apply(lambda x: type(x) == str and ('立案' in x or '违规担保' in x))]
print(len(news_info))
newID_list = news_info['newsID'].map(int).tolist()
nd = NewsData()
if len(newID_list) == 0:
    news_bodies_df = pd.DataFrame()
else:
    news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]

tuishi_set = set()
for idx in range(len(news_bodies_df)):
    row = news_bodies_df.iloc[idx]
    news_body = news_bodies_df.iloc[idx]['CONTENT']
    news_body = news_body.replace('\r', '').replace('\n', '').replace(' ', '')  # 去除换行符空白00符
    for text in news_body.split('。'):
        if '退市风险' in text:
            stock_code = news_info.iloc[idx]['Ticker']
            dt = news_info.iloc[idx]['dt']
            title = news_info.iloc[idx]['TEXTTITLE']
            tuishi_set.add((dt, stock_code, title))

print(stock_code)
