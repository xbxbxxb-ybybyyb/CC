# coding: utf-8
# Author：fengchi863
# Date ：2024/8/17 15:41

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from dataApi import tradeDate
from MixedWork.GreyStockGenerator import IO

s = FactorData()
from tqdm import tqdm

date_list = tradeDate.get_date_range(20230101, 20240820)
path_user = '/data/user/015614/daily/灰名单生成/异常波动历史测试V20240817/'

rolling_period = 1
nowdate = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
# nowdate = str(20240820)
nextdate = nowdate
date = s.tradingday(nextdate, -2)[0]
lastdate = s.tradingday(date, -2)[0]

f_data = IO.read_data([s.tradingday(date, -50)[0], date], columns=['close', 'adjfactor'],
                      alt='/data/group/800080/warehouse_event/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

all_sample = list(f_data['close'].unstack().columns)

from xquant.textdata import NewsData

nd = NewsData()
ycbd_tot = pd.DataFrame(columns=['dt', 'Ticker', 'id', 'ycbd_indicator']).set_index(['dt', 'Ticker'])
jyfxts_tot = pd.DataFrame(columns=['dt', 'Ticker', 'id', 'jyfxts_indicator']).set_index(['dt', 'Ticker'])
all_sample = list(filter(lambda x: not str(x).endswith('BJ'), all_sample))
# for stock in all_sample:
#     print(stock)
#     data_info = nd.getNewsInfoByStockCode(stock[:~2], data_source='TNEWS')
#     data_info = data_info[data_info['textcategory'].astype('str').str.startswith('2')]
#     if len(data_info) == 0:
#         continue
#
#     data_info = data_info.rename(columns={'pubdate': 'dt'})
#     data_info['Ticker'] = stock
#     data_info = data_info.reset_index().set_index(['dt', 'Ticker']).sort_index()
#     data_info = data_info[data_info['texttitle'].apply(lambda x: x != None)]
#
#     if len(data_info) != 0:
#         data_info = data_info.loc[pd.Timestamp(s.tradingday(date, -730)[0]):, ]
#         ycbd_warning = data_info[['id', 'texttitle']][
#             data_info['texttitle'].apply(lambda x: (('异常波动' in x) | ('异动' in x)) & ('回复' not in x) & \
#                                                    ('回复函' not in x) & ('复函' not in x) & \
#                                                    ('回函' not in x) & ('补充' not in x) & ('说明' not in x) & ('海外' not in x))]
#         ycbd_warning['ycbd_indicator'] = 1
#         jyfxts_warning = data_info[['id', 'texttitle']][
#             data_info['texttitle'].apply(lambda x: ('风险' in x) & ('回复' not in x) & \
#                                                    ('回复函' not in x) & ('复函' not in x) & \
#                                                    ('回函' not in x))]
#         jyfxts_warning['jyfxts_indicator'] = 1
#         if len(ycbd_warning) != 0:
#             ycbd_tot = pd.concat([ycbd_tot, ycbd_warning[['id', 'ycbd_indicator']]])
#         if len(jyfxts_warning) != 0:
#             for index, row in jyfxts_warning.iterrows():
#                 tt = row['texttitle']
#                 id = row['id']
#                 newsBody = nd.getNewsBody([str(id)])
#                 if len(newsBody) == 0:
#                     jyfxts_warning.loc[index, 'jyfxts_indicator'] = 0
#                 else:
#                     if ('交易风险' in tt) & ('撤销' not in tt):
#                         jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
#                     else:
#                         newsBody = newsBody.reset_index()['newsBody'].loc[0]
#                         if ('交易' in newsBody) & (('涨停' in newsBody) | ('偏离' in newsBody)):
#                             jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
#                         else:
#                             jyfxts_warning.loc[index, 'jyfxts_indicator'] = 0
#             jyfxts_warning = jyfxts_warning[jyfxts_warning['jyfxts_indicator'] == 1]
#             jyfxts_tot = pd.concat([jyfxts_tot, jyfxts_warning[['id', 'jyfxts_indicator']]])

data_info = nd.getAnnouncement(all_sample, str(20221001), str(date))

data_info = data_info.rename(columns={'PUBDATE': 'dt'})
data_info['Ticker'] = data_info['STOCK']
data_info = data_info.reset_index().set_index(['dt', 'Ticker']).sort_index()
data_info = data_info[data_info['TEXTTITLE'].apply(lambda x: x != None)]

ycbd_warning = data_info[['ORIGINALCODE', 'TEXTTITLE']][
            data_info['TEXTTITLE'].apply(lambda x: (('异常波动' in x) | ('异动' in x)) & ('回复' not in x) & \
                                                   ('回复函' not in x) & ('复函' not in x) & \
                                                   ('回函' not in x) & ('补充' not in x) & ('说明' not in x) & ('海外' not in x))]
ycbd_warning['ycbd_indicator'] = 1

jyfxts_warning = data_info[['ORIGINALCODE', 'TEXTTITLE']][
data_info['TEXTTITLE'].apply(lambda x: ('风险' in x) & ('回复' not in x) & \
                                       ('回复函' not in x) & ('复函' not in x) & \
                                       ('回函' not in x))]
jyfxts_warning['jyfxts_indicator'] = 1

newsBody = nd.getAnnouncementContent(jyfxts_warning['ORIGINALCODE'].map(str).tolist())
jyfxts_warning = jyfxts_warning.reset_index().set_index('ORIGINALCODE').join(newsBody, how='left').set_index(['dt', 'Ticker'])

for index, row in jyfxts_warning.iterrows():
    tt = row['TEXTTITLE']
    if ('交易风险' in tt) & ('撤销' not in tt):
        jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
    else:
        news_content = row['CONTENT']
        if ('交易' in news_content) & (('涨停' in news_content) | ('偏离' in news_content)):
            jyfxts_warning.loc[index, 'jyfxts_indicator'] = 1
        else:
            jyfxts_warning.loc[index, 'jyfxts_indicator'] = 0

jyfxts_warning = jyfxts_warning[jyfxts_warning['jyfxts_indicator'] == 1]
jyfxts_tot = jyfxts_warning

ycbd_tot = ycbd_warning.reset_index()
ycbd_tot['dt_old'] = ycbd_tot['dt']
ycbd_tot['dt'] = ycbd_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
ycbd_tot = ycbd_tot.set_index(['dt', 'Ticker']).sort_index()
ycbd_tot = ycbd_tot.loc[~ycbd_tot.index.duplicated(keep='first')].sort_index()

jyfxts_tot = jyfxts_tot.reset_index()
jyfxts_tot['dt_old'] = jyfxts_tot['dt']
jyfxts_tot['dt'] = jyfxts_tot['dt'].apply(lambda x: pd.Timestamp(s.tradingday(x.strftime('%Y%m%d'), 1)[0]))
jyfxts_tot = jyfxts_tot.set_index(['dt', 'Ticker']).sort_index()
jyfxts_tot = jyfxts_tot.loc[~jyfxts_tot.index.duplicated(keep='first')].sort_index()

ycbd_tot.to_pickle('/data/user/015614/daily/灰名单生成/中间数据/ycbd_tot_20240820.pkl')
jyfxts_tot.to_pickle('/data/user/015614/daily/灰名单生成/中间数据/jyfxts_tot_20240820.pkl')
