# coding: utf-8
# Author：fengchi863
# Date ：2022/8/24 14:38

"""
获取所有Wind概念指数的成分股数据，并格式化Wind概念指数成分股，以每个指数为文件名保存他的成分股
"""

import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import multiprocessing
import os
import shutil
import warnings

import pandas as pd
from xquant.factordata import FactorData
from tqdm import tqdm
import time
from LucienUtil.SpeedUtil import SpeedUtil

warnings.filterwarnings("ignore")
fd = FactorData()

# 初始化参数
parallel_num = 20
path = '/data/user/015614/daily/basic/basic_wind_sw_history4/'
path_block = path + 'BlockData/'
DATE_MAX = '20991231'
# begin_date = '20220815'
begin_date = '20150101'
now_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
yes_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -2)[0]
now_dt = pd.to_datetime(now_date)
yes_dt = pd.to_datetime(yes_date)
# if os.path.exists(path_block):
#     shutil.rmtree(path_block)
os.makedirs(path_block, exist_ok=True)
os.makedirs(path_block + 'each_block/', exist_ok=True)

t1 = time.time()
# 读取指数成分股数据
print(f'1、读取Wind概念当天的成分股数据...{time.time() - t1}')
member99 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='<20160101', F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member0 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20160101", '<=' + "20161231"], F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member00 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20170101", '<=' + "20171231"], F_INFO_WINDCODE="like'884%'")  # 进出记录需要取全部时间区间，数量超过上限分为两部分。
member01 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20180101", '<=' + "20181231"], F_INFO_WINDCODE="like'884%'")
member02 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20190101", '<=' + "20191231"], F_INFO_WINDCODE="like'884%'")
member03 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20200101", '<=' + "20201231"], F_INFO_WINDCODE="like'884%'")
member1 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20210101", '<=' + "20211231"], F_INFO_WINDCODE="like'884%'")
member2 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE=['>=' + "20220101", '<=' + "20221231"], F_INFO_WINDCODE="like'884%'")
member3 = fd.get_factor_value('WIND_AIndexMembersWIND', S_CON_INDATE='>=20230101', F_INFO_WINDCODE="like'884%'")
wind_member = pd.concat([member99, member0, member00, member01, member02, member03, member1, member2, member3], ignore_index=True)
wind_member['S_CON_OUTDATE'] = wind_member['S_CON_OUTDATE'].fillna(DATE_MAX)  # 如果未调出，为缺失值，替换为极大值
wind_member = wind_member[['F_INFO_WINDCODE', 'S_CON_WINDCODE', 'S_CON_INDATE', 'S_CON_OUTDATE', 'OPDATE']].astype(str)
wind_member.columns = ['block', 'Ticker', 'indt', 'outdt', 'opdt']
wind_member = wind_member[wind_member['Ticker'].str.endswith(('.SZ', '.SH'))]
wind_member = wind_member[wind_member['Ticker'].str.startswith(('0', '3', '6'))]
for dtcol in ['indt', 'outdt', 'opdt']:
    wind_member[dtcol] = pd.to_datetime(wind_member[dtcol])
# wind_member.to_pickle(path_block + 'wind_member.pkl')   # 列indt outdt opdt block Ticker block表示概念（源于孙少森）

# 获取交易日期列表
date_df = pd.DataFrame()
date_df['dt'] = fd.tradingday(begin_date, now_date)
date_df['dt'] = pd.to_datetime(date_df['dt'])

# 读取股票基本资料中的退市时间
AShareDescription = fd.get_factor_value('WIND_AShareDescription')
AShareDescription['S_INFO_DELISTDATE'] = pd.to_datetime(AShareDescription['S_INFO_DELISTDATE'].fillna(DATE_MAX))
AShareDescription.set_index('S_INFO_WINDCODE', inplace=True)
AShareDescription.loc['689009.SH', 'S_INFO_DELISTDATE'] = pd.to_datetime(DATE_MAX)

# 获取指数发布日期
AIndexDescription0 = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
AIndexDescription0 = AIndexDescription0[['S_INFO_WINDCODE', 'S_INFO_LISTDATE']]
AIndexDescription0.columns = ['block', 'list_dt']
AIndexDescription0['list_dt'] = pd.to_datetime(AIndexDescription0['list_dt'])
AIndexDescription0.set_index('block', inplace=True)

# 根据指数k线图计算发布日期
ccpt_daily_data1 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + begin_date, '<=' + "20161231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data2 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20170101", '<=' + "20171231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data22 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20180101", '<=' + "20181231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data3 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20190101", '<=' + "20191231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data4 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20200101", '<=' + "20201231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data5 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20210101", '<=' + "20211231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data6 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20220101", '<=' + "20221231"], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data7 = fd.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=['>=' + "20230101", '<=' + now_date], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data = pd.concat([ccpt_daily_data1, ccpt_daily_data2, ccpt_daily_data22, ccpt_daily_data3, ccpt_daily_data4, ccpt_daily_data5, ccpt_daily_data6, ccpt_daily_data7], axis=0)
ccpt_daily_data = ccpt_daily_data[(ccpt_daily_data['S_DQ_HIGH'] - ccpt_daily_data['S_DQ_LOW']) > 0][['TRADE_DT', 'S_INFO_WINDCODE']]
ccpt_daily_data.columns = ['dt', 'block']
ccpt_daily_data['dt'] = pd.to_datetime(ccpt_daily_data['dt'])
AIndexDescription = ccpt_daily_data.sort_values(['block', 'dt']).groupby('block')[['dt']].first()
AIndexDescription.columns = ['list_dt']
AIndexDescription['delist_dt'] = ccpt_daily_data.sort_values(['block', 'dt']).groupby('block')[['dt']].last()
print('总耗时', time.time() - t1)  # 20150101-20220902 查询耗时377秒=8min

# 并行化生成板块数据
def save_block(block):
    member = wind_member[wind_member['block'] == block]
    d_list = []
    for i in range(len(member)):
        Ticker = member.iloc[i]['Ticker']
        indate = member.iloc[i]['indt']
        outdate = member.iloc[i]['outdt']
        d = date_df[date_df['dt'] > indate]
        d = d[d['dt'] <= outdate]
        d = d[d['dt'] <= AShareDescription.loc[Ticker, 'S_INFO_DELISTDATE']]  # 把股票退市后的数据删掉
        d['Ticker'] = Ticker
        d_list.append(d)
    block_member = pd.concat(d_list, ignore_index=True).drop_duplicates()
    block_member[block] = 1

    # 删除指数发布前的日期
    if block in AIndexDescription.index:
        list_dt = AIndexDescription.loc[block, 'list_dt']
        delist_dt = AIndexDescription.loc[block, 'delist_dt']
    elif block in AIndexDescription0.index:
        list_dt = AIndexDescription0.loc[block, 'list_dt']
        delist_dt = yes_dt
    else:
        print('Warning Miss ' + block)
        list_dt = member['opdt'].min()
        delist_dt = yes_dt
    block_member = block_member[(block_member['dt'] >= list_dt) & (block_member['dt'] <= delist_dt)]

    # 保存数据
    if len(block_member) > 0:
        block_member.set_index(['dt', 'Ticker'], inplace=True)
        block_member.to_pickle(path_block + 'each_block/' + block + '.pkl')

def parallel_save_block(wind_concept_list):
    pbar = tqdm(range(len(wind_concept_list)))
    for idx in pbar:
        wind_concept = wind_concept_list[idx]
        pbar.set_description('并行生成中|%s' % wind_concept)
        save_block(wind_concept)

t1 = time.time()
SpeedUtil.multiprocess(20, parallel_save_block, list(wind_member['block'].unique()))
print('耗时：', time.time() - t1)  # 20150101-20220902 拼接耗时1598秒