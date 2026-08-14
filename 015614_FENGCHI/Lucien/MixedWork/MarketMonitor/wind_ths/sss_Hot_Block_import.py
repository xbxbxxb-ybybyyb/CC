# coding: utf-8
# Author：fengchi863
# Date ：2022/8/26 8:33

import os
import numpy as np
from model_eval.multifactor.IO import IO
import pandas as pd
import datetime as dt
# from Hot_Block_Fun import *
from datetime import timedelta
from xquant.factordata import FactorData
s=FactorData()


#初始化参数
# path='/data/user/018107/Database/'
# path_block=path+'BlockData/'
# path_record='/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
# path_param='/data/group/800463/param/param/'
# path_black='/data/user/018107/黑名单/'
# now_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]
# last_date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -2)[0]#最新成交记录文件的日期
# day=pd.to_datetime(now_date)
# last_week_begin= day - timedelta(days=day.weekday()) + timedelta(days=0, weeks=-1)
# last_week_begin=s.tradingday(last_week_begin.strftime('%Y%m%d'), 1)[0]
# last_week_end= day - timedelta(days=day.weekday()) + timedelta(days=4, weeks=-1)
# last_week_end=s.tradingday(last_week_end.strftime('%Y%m%d'), -1)[0]
# last_year_period=str(int(now_date[:4])-1)+'1231' #上一年度年底
#
# #读取Jupiter&Europa买入记录
# jupiter_file=path_record+'jupiter成交记录-%s.xlsx'%last_week_end
# Europa_file=path_record+'Europa成交记录-%s.xlsx'%last_week_end
# jupiter_record = pd.read_excel(jupiter_file,sheet_name = '累计买入明细')
# Europa_record = pd.read_excel(Europa_file,sheet_name = '累计买入明细')
# record=pd.merge(jupiter_record[['发生日期','证券代码','成交金额']],Europa_record[['发生日期','证券代码','成交金额']],how='outer',on=['发生日期','证券代码'])
# record['成交金额']=record['成交金额_x'].fillna(0)+record['成交金额_y'].fillna(0)
# record['发生日期']=pd.to_datetime(record['发生日期'])
# record=record[['发生日期','证券代码','成交金额']]
# record.columns=['dt','Ticker','amt']
# record=record.set_index(['dt','Ticker']).sort_index()
#
# #读取Jupiter&Europa卖出记录
# jupiter_file=path_record+'jupiter成交记录-%s.xlsx'%last_date
# Europa_file=path_record+'Europa成交记录-%s.xlsx'%last_date
# jupiter_record = pd.read_excel(jupiter_file,sheet_name = '累计卖出明细')
# Europa_record = pd.read_excel(Europa_file,sheet_name = '累计卖出明细')
# record1=pd.merge(jupiter_record[['买入日期','证券代码','卖出日期','卖出金额']],Europa_record[['买入日期','证券代码','卖出日期','卖出金额']],how='outer',on=['买入日期','证券代码'],suffixes=['_j','_e'])
# record1[['卖出日期_j','卖出日期_e','卖出金额_j','卖出金额_e']]=record1[['卖出日期_j','卖出日期_e','卖出金额_j','卖出金额_e']].fillna('').astype(str)
# # record1=record1.apply(get_tot_selldt,axis=1)
# record1['买入日期']=pd.to_datetime(record1['买入日期'])
# record1=record1[['买入日期','证券代码','selldt','sellp']]
# record1.columns=['dt','Ticker','selldt','sellp']
# record1=record1.set_index(['dt','Ticker']).sort_index()
# record['selldt']=record1['selldt']
# record['sellp']=record1['sellp']
#
#
# #读取股票名称
# name_data = IO.read_data([last_year_period, last_week_end],columns=['STOCK_NAME'],
#                          alt='/data/group/800080/warehouse/prod/FCD/CHINA_STOCK/DAILY/SUNTIME/FCD_CHINA_STOCK_DAILY_SUNTIME.h5')
# name_data = name_data.groupby(['dt', 'Ticker']).first()

#读取概念板块名称
AIndexDescription=s.get_factor_value('WIND_AIndexDescription',S_INFO_WINDCODE="like'884%'")
AIndexDescription['S_INFO_NAME']=AIndexDescription['S_INFO_NAME'].str.replace('指数','')
AIndexDescription=AIndexDescription[AIndexDescription['CHANGE_HISTORY'].astype(str).str.contains('概念')]
AIndexDescription=AIndexDescription[~AIndexDescription['S_INFO_NAME'].str.contains('退市|板|全A|新股|振幅|低价|高价|点位贡献|重组|定增|回购|预增|龙虎榜|领涨龙头|金股|精选|中非合作|国资|台资|陆股通')]
AIndexDescription=AIndexDescription[~AIndexDescription['CHANGE_HISTORY'].astype(str).str.contains('停用')]

#读取行业板块名称
IndexContrastSector=s.get_factor_value('WIND_IndexContrastSector')
IndexContrastSector=IndexContrastSector[IndexContrastSector['S_INFO_INDEXCODE'].str.endswith('.SI')]
IndexContrastSector=IndexContrastSector[IndexContrastSector['S_INFO_INDUSTRYCODE'].str.startswith('760')]

#合并
AIndexDescription=AIndexDescription[['S_INFO_WINDCODE','S_INFO_NAME']]
AIndexDescription.columns=['block_code','block_name']
IndexContrastSector=IndexContrastSector[['S_INFO_INDEXCODE','S_INFO_INDUSTRYNAME']]
IndexContrastSector.columns=['block_code','block_name']
block_name=pd.concat(([AIndexDescription,IndexContrastSector]),axis=0,ignore_index=True)

#读取板块数据
def view_bar(num, tot, s):
    import sys
    rate = (num + 1) / tot
    rate_num = (int(rate * 100))
    n = rate_num // 3
    r = '\r[%s>%s]%d%%-%s' % ('=' * n, '-' * (33 - n), rate_num, s)
    sys.stdout.write(r)
    sys.stdout.flush()
    if rate == 1:
        print('\n')

d_list=[]
file_list=os.listdir(path_block + 'each_block')
for n, f in enumerate(file_list):
    view_bar(n, len(file_list), f)
    if f[:-4] in block_name['block_code'].unique():#筛选有效板块
        d=pd.read_pickle(path_block+'each_block/'+f)
        d=d.query('@last_year_period<=dt<=@last_week_end')
        if len(d)>0:
            d_list.append(d)
member=pd.concat(d_list, axis=1)
print('成分股合并完成')

#选择成分股数量在5-100之间，有行情的概念板块
block_num = member.query('dt==@last_week_end').sum()
block_num = block_num[(block_num > 5) & (block_num < 100)]
ccpt_daily_data = s.get_factor_value('WIND_AIndexWindIndustriesEOD', TRADE_DT=[last_week_end], S_INFO_WINDCODE="like'884%'")
ccpt_daily_data_valid = ccpt_daily_data[(ccpt_daily_data['S_DQ_HIGH'] - ccpt_daily_data['S_DQ_LOW']) > 0]
block0_list = [i for i in block_num.index if i in ccpt_daily_data_valid['S_INFO_WINDCODE'].unique()]
block_list = [i for i in member.columns if i in block0_list or 'SI' in i]
member = member[block_list]

