# coding: utf-8
# Author：fengchi863
# Date ：2024/2/29 11:00

import datetime as dt

import numpy as np
import pandas as pd
from xquant.factordata import FactorData

s = FactorData()
from LucienUtil import IO
from xquant.marketdata import MarketData
mdp = MarketData()
import sys
import time
import os

t1 = time.time()
if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    date = '20240228'# # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('current date = %s' % date)

# 只查找最近10天的缺失
last10days = list(map(lambda x: x[:4] + '-' + x[4:6] + '-' + x[6:8], s.tradingday(date, -10)))

jup_conceptFile = '/data/group/800463/fengc/daily/concept/jupiter_concept.h5'
eur_conceptFile = '/data/group/800463/fengc/daily/concept/europa_concept.h5'
jup_concept = pd.read_hdf(jup_conceptFile).reset_index()
jup_concept['发生日期'] = jup_concept['dt'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
jup_concept.set_index(['发生日期', 'Ticker'], inplace=True)

eur_concept = pd.read_hdf(eur_conceptFile).reset_index()
eur_concept['发生日期'] = eur_concept['dt'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d'))
eur_concept.set_index(['发生日期', 'Ticker'], inplace=True)

# 测试了这种方案还是无法直接保留表格原格式的情况下改变其中一个sheet页
def add_jup_concept(target_fpath, col='概念名称'):
    df = pd.read_excel(target_fpath, sheet_name='累计买入明细')
    lost_concept_index = df.iloc[-200:][df.iloc[-200:][col].isna()].index
    df.loc[lost_concept_index, '概念名称'] = df.loc[lost_concept_index, ['发生日期', '证券代码']].apply(lambda x:
                        eur_concept.loc[(x['发生日期'], x['证券代码']), '概念名称'] if (x['发生日期'], x['证券代码']) in eur_concept.index else '', axis=1)
    # TODO：保存数据，探索只覆盖这一个sheet页的方式
    writer = pd.ExcelWriter(target_fpath, engine='openpyxl', mode='a')
    df.to_excel(writer, sheet_name='累计买入明细')
    writer.save()
    writer.close()


# 给jupiter、europa、metis策略添加概念列
add_jup_concept(target_fpath='/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/Europa成交记录-20240228-test.xlsx')