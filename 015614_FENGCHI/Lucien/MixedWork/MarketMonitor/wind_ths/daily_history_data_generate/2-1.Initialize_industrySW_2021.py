# coding: utf-8
# Author：fengchi863
# Date ：2022/8/26 8:31

import datetime as dt
import os
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from tqdm import tqdm
s = FactorData()

# 初始化参数
path = '/data/user/015614/daily/basic/basic_wind_sw_history_everyday/'
path_block = path + 'BlockData/'
path_industry = path + 'IndustryData/'
os.makedirs(path_industry, exist_ok=True)
DATE_MAX = '20991231'
# begin_date = '20220815'
# begin_date = '20150101'
begin_date = '20211213'
now_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]

# 获取交易日期列表
date_df = pd.DataFrame()
date_df['dt'] = s.tradingday(begin_date, now_date)
date_df['dt'] = pd.to_datetime(date_df['dt'])

# 申万行业指数代码和wind指数代码对应表
IndexContrastSector = s.get_factor_value('WIND_IndexContrastSector')
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDEXCODE'].str.endswith('.SI')]
IndexContrastSector = IndexContrastSector[IndexContrastSector['S_INFO_INDUSTRYCODE'].str.startswith('760')]
IndexContrastSector = IndexContrastSector[['S_INFO_INDUSTRYCODE', 'S_INFO_INDEXCODE']]
IndexContrastSector.set_index('S_INFO_INDUSTRYCODE', inplace=True)

# 读取行业指数成分股进出记录
AShareSWIndustriesClass = s.get_factor_value('WIND_AShareSWNIndustriesClass')
AShareSWIndustriesClass['REMOVE_DT'] = AShareSWIndustriesClass['REMOVE_DT'].fillna(DATE_MAX)  # 如果未调出，为缺失值，替换为极大值
AShareSWIndustriesClass = AShareSWIndustriesClass[['SW_IND_CODE', 'S_INFO_WINDCODE', 'ENTRY_DT', 'REMOVE_DT']]
AShareSWIndustriesClass.columns = ['industry', 'Ticker', 'indt', 'outdt']
for dtcol in ['indt', 'outdt']:
    AShareSWIndustriesClass[dtcol] = pd.to_datetime(AShareSWIndustriesClass[dtcol])

AShareSWIndustriesClass2 = AShareSWIndustriesClass.copy()
AShareSWIndustriesClass2['industry'] = AShareSWIndustriesClass2['industry'].apply(lambda x: x[:6].ljust(16, '0'))
AShareSWIndustriesClass2['industry'] = AShareSWIndustriesClass2['industry'].apply(lambda x: IndexContrastSector.loc[x, 'S_INFO_INDEXCODE'] if x in IndexContrastSector.index else np.nan)
AShareSWIndustriesClass2 = AShareSWIndustriesClass2.dropna(subset=['industry'])

# 读取股票基本资料中的退市时间
AShareDescription = s.get_factor_value('WIND_AShareDescription')
AShareDescription['S_INFO_DELISTDATE'] = pd.to_datetime(AShareDescription['S_INFO_DELISTDATE'].fillna(DATE_MAX))
AShareDescription.set_index('S_INFO_WINDCODE', inplace=True)
AShareDescription.loc['689009.SH', 'S_INFO_DELISTDATE'] = pd.to_datetime(DATE_MAX)

"""对于申万二级行业，不考虑K线是否有无
# 读取行业指数行情数据
ccpt_daily_data1 = s.get_factor_value('WIND_ASWSIndexEOD', TRADE_DT=['>=' + begin_date, '<=' + "20171231"],  S_INFO_WINDCODE="like'8%.SI'",
                                     factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'])
ccpt_daily_data2 = s.get_factor_value('WIND_ASWSIndexEOD', TRADE_DT=['>=' + "20180101", '<=' + "20201231"],  S_INFO_WINDCODE="like'8%.SI'",
                                     factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'])
ccpt_daily_data3 = s.get_factor_value('WIND_ASWSIndexEOD', TRADE_DT=['>=' + "20210101", '<=' + now_date],  S_INFO_WINDCODE="like'8%.SI'",
                                     factors=['TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_HIGH', 'S_DQ_LOW', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'])
ccpt_daily_data = pd.concat([ccpt_daily_data1, ccpt_daily_data2, ccpt_daily_data3], axis=0)
ccpt_daily_data.columns = ['dt', 'industry', 'high', 'low', 'close', 'amt']
ccpt_daily_data['dt'] = pd.to_datetime(ccpt_daily_data['dt'])

ccpt_daily_data = ccpt_daily_data[ccpt_daily_data['industry'].isin(industry_members['industry'].unique())]
# 指数发布时间（k线图第一个正常的日子）
tem = ccpt_daily_data[(ccpt_daily_data['high'] - ccpt_daily_data['low']) > 0]
index_dt1 = tem.sort_values('dt').groupby('industry')['dt'].first()
"""

# 筛选在行业指数集合内的指数
industry_members = AShareSWIndustriesClass2.copy()

level = 2
industry_members.to_pickle(path_industry + 'SW2021_Industry_members' + str(level) + '.pkl')
industry_list = industry_members['industry'].unique()
for sw_code in tqdm(industry_list):
    # view_bar(n, len(industry_list), sw_code)
    member = industry_members[industry_members['industry'] == sw_code]
    d_list = []
    for i in range(len(member)):
        Ticker = member.iloc[i]['Ticker']
        indate = member.iloc[i]['indt']
        outdate = member.iloc[i]['outdt']
        d = date_df[date_df['dt'] >= indate]  # 20191201去除，20191202加入，为了避免20191202数量减少过多，改为>=
        d = d[d['dt'] <= outdate]
        try:
            d = d[d['dt'] <= AShareDescription.loc[Ticker, 'S_INFO_DELISTDATE']]  # 把股票退市后的数据删掉
        except:
            Ticker = '920' + Ticker[3:]
            d = d[d['dt'] <= AShareDescription.loc[Ticker, 'S_INFO_DELISTDATE']]
        d['Ticker'] = Ticker
        d_list.append(d)
    data = pd.concat(d_list, ignore_index=True).drop_duplicates()
    data[sw_code] = 1
    """对于申万二级行业，不考虑K线是否有无
    if industry in index_dt1.index:
        data = data[data['dt'] >= index_dt1.loc[industry]]  # 将指数公布前的数据删除
    """
    data = data[data['dt'] >= pd.to_datetime('2021-12-13')] # 2021-12-13申银万国发布新的指数正式运行公告
    data.set_index(['dt', 'Ticker'], inplace=True)
    os.makedirs(path_block + 'sw2021_each_block/', exist_ok=True)
    data.to_pickle(path_block + 'sw2021_each_block/' + sw_code + '.pkl')  # 把二级行业指数加入到概念板块中
