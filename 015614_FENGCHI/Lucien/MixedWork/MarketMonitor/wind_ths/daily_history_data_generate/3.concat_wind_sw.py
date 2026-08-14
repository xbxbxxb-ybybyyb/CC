# coding: utf-8
# Author：fengchi863
# Date ：2022/8/26 13:24

import sys
sys.path.append('/data/user/015614/Lucien')

import pandas as pd
import numpy as np
import os
from dataApi import tradeDate, stockList
from tqdm import tqdm
import time
import datetime as dt
from xquant.factordata import FactorData
from LucienUtil.FileUtil import FileUtil
from LucienUtil.SpeedUtil import SpeedUtil

"""
其中用到的表，AIndexDescription每天9:00、18:00、20:00有个更新，这个时间要避开一下，否则可能取到的Wind概念数量不对
"""

"""首先进行剔除，再拼接，减小时间消耗"""
# 剔除的概念
drop_concept_list = [# 100成分股以上
                     '小市值','融资融券','纳入富时罗素','标普道琼斯中国','成交主力','股票质押','纳入MSCI','专精特新','可转债',
                     '行业龙头','微盘股','专精特新企业','员工持股','基金重仓','破净','私募重仓','机构调研','基金重仓(季调)',
                     '减持','近期减持','小盘成长','大盘股','三新','5G应用','借壳上市','长三角','核心资产','珠三角','举牌',
                     '一线龙头','股权转让','可转债预案','华为平台','高送转','科技龙头','股权激励','资源股','业绩爆雷','养老金',
                     '浦东新区','消费电子产业','肺炎主题','双循环','文化传媒主题','央企','5G','节能环保','碳中和','新基建',
                     '外贸','深圳','合资企业','军民融合','国产化创新','社保重仓','分拆上市',
                     # 100成分股以下
                     '双创100','中小创蓝筹','扭亏','券商重仓','白马股','护城河','地方国企','国家队','最小市值','证金',
                     '高盈利成长股','限售解禁','即将解禁','QFII重仓','国家大基金','高送转预期','A50','沪伦通','增持',
                     '债转股','高瓴资本','QFII重仓(最新)','摘帽','保底增持','中概股回归','机构大额卖出','机构大额买入',
                     '信托重仓']
drop_concept_formatted = '|'.join(drop_concept_list)

fd = FactorData()
wind_concept = fd.get_factor_value('WIND_AIndexDescription', S_INFO_WINDCODE="like'884%'")
wind_concept['S_INFO_NAME'] = wind_concept['S_INFO_NAME'].str.replace('指数', '')
wind_concept = wind_concept[wind_concept['CHANGE_HISTORY'].astype(str).str.contains('概念')]  # 筛选概念、题材
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
wind_concept = wind_concept[~wind_concept['S_INFO_NAME'].str.contains(drop_concept_formatted)]
filter_col = ['S_INFO_WINDCODE', 'S_INFO_CODE', 'S_INFO_NAME']
wind_concept = wind_concept[filter_col]
wind_concept_list = wind_concept['S_INFO_WINDCODE'].tolist()
FileUtil.save_list2pkl(wind_concept_list, '/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/', '最新2015至今全量Wind列表.pkl')
code_concept_dict = wind_concept[['S_INFO_WINDCODE', 'S_INFO_NAME']].set_index('S_INFO_WINDCODE').to_dict()['S_INFO_NAME']

# 筛选其中是WI的板块
t1 = time.time()
block_path = '/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/each_block/'
wind_concept_file_list = list(filter(lambda x: x[:-4] in wind_concept_list, os.listdir(block_path)))
sw2_concept_file_list = list(filter(lambda x: 'SI' in x, os.listdir(block_path)))
sw2_concept_list = list(map(lambda x: x[:-4], sw2_concept_file_list))
FileUtil.save_list2pkl(sw2_concept_list, '/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/', '最新2015至今全量申万二级行业列表.pkl')

# today_date = int(fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0])
today_date = 20241024   # TODO：每次重跑这里要改
today_date = 20250510   # TODO：每次重跑这里要改
yesterday_date = fd.tradingday(dt.datetime.now().strftime('%Y%m%d'), -2)[0]
# date_list = tradeDate.get_date_range(20240513, 20240831)
date_list = tradeDate.get_date_range(20160101, today_date)
# date_list = tradeDate.get_date_range(20241015, today_date)
has_appear_stk_list = list(map(lambda x: stockList.trans_int2windcode(x), stockList.get_all_stock_ever_appear(today_date)))

file_list = wind_concept_file_list + sw2_concept_file_list
concept_list = list(map(lambda x: x[:-4], file_list))

"""第三种方式的并行化版本"""
def concat_block(date):
    value_list = list()
    t2 = time.time()
    for fname in file_list:
        data = pd.read_pickle(block_path + fname)
        data2 = data.reindex(index=pd.MultiIndex.from_product([[pd.to_datetime(str(date))], has_appear_stk_list]), fill_value=0)
        data_values = data2.values
        value_list.append(data_values)
    print('本轮耗时：', time.time() - t2)  # 基本每轮90秒
    # t2 = time.time()
    value_res = np.concatenate(value_list, axis=1)
    # print('拼接耗时：', time.time() - t2)    # 时间忽略不计，0.057秒
    res = pd.DataFrame(value_res, index=has_appear_stk_list, columns=concept_list)
    os.makedirs('/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/daily_Wind&SW/', exist_ok=True)
    res.to_pickle('/data/user/015614/daily/basic/basic_wind_sw_history_everyday/BlockData/daily_Wind&SW/' + f'{date}.pkl')

def parallel_concat_block(_date_list):
    pbar = tqdm(range(len(_date_list)))
    for idx in pbar:
        date = _date_list[idx]
        pbar.set_description('并行生成中|%s' % date)
        concat_block(date)

t1 = time.time()
SpeedUtil.multiprocess(20, parallel_concat_block, date_list)
print('耗时：', time.time() - t1)
