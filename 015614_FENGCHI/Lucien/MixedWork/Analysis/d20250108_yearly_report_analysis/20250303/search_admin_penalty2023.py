# coding: utf-8
# Author：fengchi863
# Date ：2025/3/4 15:13

"""
解析全部上市公司同时包含“行政处罚”和“告知书”字样的公告，解析正文，包含“虚假记载”的内容，筛选此类个股，计算到发布“决定书”的概率和时间跨度；
"""
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

import sys
if len(sys.argv) < 2:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
    # date = '20250102'
else:
    date = sys.argv[1]
# date = '20230430'
date_dt = pd.to_datetime(date)
lastdate = s.tradingday(date, -2)[0]  # 上一交易日
year = lastdate[:4]  # 当前年度
last_year = str(int(year) - 2)  # 上一年度
# last_year_period = last_year + '1231'  # 上一年度报告期
last_year_period = '20231231'  # 上一年度报告期    # 20250103：防止年初读取不到公告，读取内容为空
last_year_last_month_dt = pd.to_datetime(last_year + '1201')  # 公告读取区间

# 读取基本数据
data = IO.read_data([last_year_period, date], columns=['close']
                    , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
stock_list = data['close'].unstack().columns  # 股票列表
# stock_list = stock_list

info_list = []
for stock in tqdm(stock_list):
    if stock[-2:] not in ['SZ', 'SH', 'BJ']:
        continue
    # if stock[-2:] in ['BJ']:
    #     print(1)
    info = nd.getAnnouncement([stock], str(20230101), str(20231231))
    # nd.getAnnouncement(['000040.SZ'], '20231231', '20240523')
    if len(info) == 0:
        continue

    info = info[info['PUBDATE'] >= last_year_last_month_dt]
    info = info.rename(columns={'PUBDATE': 'dt'})
    info['Ticker'] = stock
    info['newsID'] = info['ORIGINALCODE'].astype(str)
    info = info[['dt', 'Ticker', 'TEXTTITLE', 'newsID']]
    info_list.append(info)
news_info = pd.concat(info_list, ignore_index=True)

# news_info.to_pickle('/data/user/015614/junkData/news_info20250306.pkl')
# news_info = pd.read_pickle('/data/user/015614/junkData/news_info20250306.pkl')

# 处理公告数据
news_info_st1 = news_info[news_info['TEXTTITLE'].apply(lambda x: type(x) == str and '行政处罚' in x and '告知书' in x)]
news_info_st1 = news_info_st1.sort_values(['Ticker', 'dt'])
stock_date1 = news_info_st1[['Ticker', 'dt']].copy()
stock_date1 = stock_date1.rename(columns={'dt': 'st_warning'})  # 可能风险警示的日期
stock_date1['month_later'] = stock_date1['st_warning'].apply(lambda x: x + dt.timedelta(days=31))  # 截止日期

from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date, get_trade_date_interval
from xquant.factordata import FactorData
fd = FactorData()
date_list = get_date_range(20201201, 20250228)
date_str_list = list(map(lambda x: str(x), date_list))
stock_list = list(stock_list)
daily_data = fd.get_factor_value('Basic_factor', factor_names=['pre_close_badj', 'close_badj', 'open_badj', 'high_badj', 'stpt', 'mdc_maxpx', 'adjfactor', 'maxupordown'], mddate=date_str_list, stock=stock_list)
# 统计被ST的可能
st_df = daily_data['stpt'].unstack()
raw_st_df = st_df.copy()
st_df = st_df.fillna(0).applymap(int) - st_df.fillna(0).applymap(int).shift(1)
st_df.index = st_df.index.map(int)
raw_st_df = raw_st_df.fillna(0).applymap(int)
raw_st_df.index = raw_st_df.index.map(int)
def judge(st_df, stock_code, date_list):
    return st_df.loc[date_list, stock_code].sum() > 0

# 对可能提到截止日期的股票单独处理
newID_list = news_info_st1['newsID'].map(int).tolist()
nd = NewsData()
if len(newID_list) == 0:
    news_bodies_df = pd.DataFrame()
else:
    news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]

fake_notice_list = []
for idx in range(len(news_bodies_df)):
    fake_flag = False
    row = news_bodies_df.iloc[idx]
    _dt = stock_date1.loc[stock_date1.iloc[idx].name, 'st_warning']
    stock_code = stock_date1.loc[stock_date1.iloc[idx].name, 'Ticker']
    news_body = news_bodies_df.iloc[idx]['CONTENT']
    news_body = news_body.replace('\r', '').replace('\n', '').replace(' ', '')
    for text in news_body.split('。'):
        text = text.replace('没有虚假记载', '')
        text = text.replace('不存在任何虚假记载', '')
        if '虚假记载' in text:
            fake_flag = True
            break
    dt_int = int(_dt.strftime('%Y%m%d'))
    has_st = judge(st_df, stock_code, get_date_range(dt_int, get_pre_trade_date(dt_int, -3)))
    already_st = judge(raw_st_df, stock_code, get_date_range(get_pre_trade_date(dt_int, 10), get_pre_trade_date(dt_int, 3)))
    if fake_flag:
        fake_notice_list.append(pd.Series([_dt, stock_code, row[0], has_st, already_st]))
    else:
        continue

fake_info = pd.concat(fake_notice_list, axis=1, ignore_index=True).T
fake_info = fake_info.rename({0: 'dt', 1: 'Ticker', 2: '告知书CONT', 3: '告知书就ST', 4: '告知书时已经是ST'}, axis=1)

#%% 查找决定书发布日期
news_info_st2 = news_info[news_info['TEXTTITLE'].apply(lambda x: type(x) == str and '行政处罚' in x and '决定书' in x)]

newID_list = news_info_st2['newsID'].map(int).tolist()
nd = NewsData()
if len(newID_list) == 0:
    news_bodies_df = pd.DataFrame()
else:
    news_bodies_df = nd.getAnnouncementContent(newID_list).loc[newID_list]


fake_decision_list = []
for idx in range(len(news_bodies_df)):
    row = news_bodies_df.iloc[idx]
    _dt = news_info_st2.iloc[idx]['dt']
    stock_code = news_info_st2.iloc[idx]['Ticker']
    news_body = news_bodies_df.iloc[idx]['CONTENT']
    news_body = news_body.replace('\r', '').replace('\n', '').replace(' ', '')
    for text in news_body.split('。'):
        if '其他风险警示' in text:
            st_flag = True
            break
    dt_int = int(_dt.strftime('%Y%m%d'))
    if stock_code == '600603.SH':
        print(1)
    has_st = judge(st_df, stock_code, get_date_range(dt_int, get_pre_trade_date(dt_int, -3)))
    fake_decision_list.append(pd.Series([_dt, stock_code, row[0], has_st]))

fake_decision = pd.concat(fake_decision_list, axis=1, ignore_index=True).T
fake_decision = fake_decision.rename({0: 'dt2', 1: 'Ticker', 2: '决定书CONT', 3: '决定书才风险警示'}, axis=1)

merge_df = pd.merge(fake_info, fake_decision, how='left', on=['Ticker'])
merge_df = merge_df[['dt', 'dt2', 'Ticker', '告知书就ST', '告知书时已经是ST', '决定书才风险警示']]

check = merge_df.sort_values(['Ticker', 'dt2']).drop_duplicates('Ticker', keep='first')

check[(check['告知书就ST']==False) & (check['决定书才风险警示']==True) & (check['告知书时已经是ST']==False)]   # 4个
check[(check['告知书就ST']==True) & (check['决定书才风险警示']==False) & (check['告知书时已经是ST']==False)]   # 13个
check[(check['告知书就ST']==False) & (check['决定书才风险警示']==False) & (check['告知书时已经是ST']==True)]   # 11个
check[(check['告知书就ST']==False) & (check['决定书才风险警示']==False) & (check['告知书时已经是ST']==False)]   # 15个
check[(check['决定书才风险警示'].isna())]   # 8个 发布了告知书到现在没有发布决定书，多数为退市个股，也有部分最近刚发布告知书
check[(check['告知书时已经是ST']==True)].shape
check[(check['告知书就ST']==True)].shape
check.shape # 51个

check2 = check[(check['告知书就ST']==False) & (check['告知书时已经是ST']==False)]
def get_date_interval(date1, date2):
    date1 = int(date1.strftime('%Y%m%d'))
    date2 = int(date2.strftime('%Y%m%d'))
    days = get_trade_date_interval(date1, date2)
    return -days

check2['时间跨度'] = check2[['dt', 'dt2']].apply(lambda x: get_date_interval(x['dt'], x['dt2']), axis=1)
check2['时间跨度'].describe()


#%% 统计策略内的表现
europa_df = pd.read_hdf('/data/group/800463/project/project1_prod/LabelProfit_fixnew/001/LabelProfit_zt_twap_0.10_2000_300_SH250_SZ20.h5')
start, end = 20200101, 20250306
basic = IO.read_data([start,end],alt='/data/group/800463/project/project1_prod/left_v2310/Basic_zt_test/Basic_zt_001.h5')
label = IO.read_data([start,end],alt='/data/group/800463/project/project1_prod/left_v2310/Label_zt_test/Label_zt_001.h5')
all_df = basic.join(label)
filter_df = all_df[(all_df['ZT_Time'] >= 93000000) & (all_df['ZT_Time'] <= 143000000) & (all_df['open_is_zt'] == 0)
                   & (all_df['T_o2pre'] >= -0.05) & (all_df['after_not_ul_len'] > 10) & (all_df['pre_close'] >= 2)
                   & (all_df['high_price'] < (all_df['trigger_price'])) & (all_df['last_is_zt'] == 0)].copy()

europa_df = europa_df.loc[filter_df.index]
europa_df = europa_df.reset_index()
europa_df['trade_date'] = europa_df['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))

ress = pd.DataFrame()
for idx in range(len(check2)):
    row = check2.iloc[idx]
    date1 = int(row['dt'].strftime('%Y%m%d'))
    date2 = int(row['dt2'].strftime('%Y%m%d'))
    stock_code = row['Ticker']
    date_list = get_date_range(date1, date2)
    tmp = europa_df.query(f'Ticker == "{stock_code}" and trade_date in {date_list}')
    tmp['行政处罚公告日'] = date1
    tmp['行政处罚决定日'] = date2
    ress = pd.concat([ress, tmp])

#%% 统计策略样本情况
ress.shape
ress2 = ress[['dt', 'Ticker',
              '行政处罚公告日', '行政处罚决定日',
              'pct_t', 'pct_t1', 'pct', 'trade_date']]
ress2['pct'].describe()