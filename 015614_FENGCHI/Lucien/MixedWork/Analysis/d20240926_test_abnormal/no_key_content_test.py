# coding: utf-8
# Author：fengchi863
# Date ：2024/9/26 11:06

import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
from xquant.factordata import FactorData
from MixedWork.GreyStockGenerator import IO
import datetime as dt
s = FactorData()

nowdate = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
nextdate = nowdate
date = s.tradingday(nextdate, -1)[0]
lastdate = s.tradingday(date, -2)[0]

f_data = IO.read_data([s.tradingday(date, -50)[0], date], columns=['close', 'adjfactor'],
                      alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

all_sample = list(f_data['close'].unstack().columns)

from xquant.textdata import NewsData

nd = NewsData()
all_sample = list(filter(lambda x: not str(x).endswith('BJ'), all_sample))

data_info = nd.getAnnouncement(all_sample, str(20240901), str(date))

data_info = data_info.rename(columns={'PUBDATE': 'dt'})
data_info['Ticker'] = data_info['STOCK']
data_info = data_info.reset_index().set_index(['dt', 'Ticker']).sort_index()
data_info = data_info[data_info['TEXTTITLE'].apply(lambda x: x != None)]

jyfxts_warning = data_info[['ORIGINALCODE', 'TEXTTITLE']][
data_info['TEXTTITLE'].apply(lambda x: ('风险' in x) & ('回复' not in x) & \
                                       ('回复函' not in x) & ('复函' not in x) & \
                                       ('回函' not in x))]
jyfxts_warning['jyfxts_indicator'] = 1

newsBody = nd.getAnnouncementContent(jyfxts_warning['ORIGINALCODE'].map(str).tolist())
jyfxts_warning2 = jyfxts_warning.reset_index().set_index('ORIGINALCODE').join(newsBody, how='left').set_index(['dt', 'Ticker'])

jyfxts_warning2 = jyfxts_warning2.reset_index()
jyfxts_warning2_count = jyfxts_warning2.groupby('dt').count()
jyfxts_warning2['na'] = jyfxts_warning2['CONTENT'].isna().astype(int)
jyfxts_warning2_na_count = jyfxts_warning2.groupby('dt')['na'].sum()

print(jyfxts_warning2)

