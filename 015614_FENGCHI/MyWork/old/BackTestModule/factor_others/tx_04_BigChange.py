########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
from xquant.factordata import FactorData
import copy
from BackTestModule.QuickFactorEvaluationBackTest import FactorBackTest
sys.path.append('/data/group/800319')
from dataApi import dividend
from dataApi import getData
from dataApi import indName
from dataApi import stockList
from dataApi import tradeDate
#############把日间参数变成日内参数#############
def change_day_to_inday(dataframe):
    ##获取一个日内参数
    start_time=dataframe.index[0]
    end_time=dataframe.index[-1]
    stock_df=list(dataframe.columns)
    min_date=getData.get_minute_1factor('close',start_datetime=start_time, end_datetime=end_time, minute_interval=1, code_list=stock_df,type='stock')
    min_date=min_date.reset_index()
    df_min=pd.DataFrame(None,columns=min_date.columns,index=min_date.index)
    df_min['date']=min_date['date']
    df_min['time']=min_date['time']
    df_min=df_min.drop(df_min[df_min['time']==925].index)
    df_min=df_min.drop(df_min[df_min['date']<start_time].index)
    ###先把日间的变成日内的############
    name=dataframe.index.name
    dataframe = dataframe.reset_index()
    if name is not None:
        dataframe.rename(columns={name:'date'}, inplace=True)
    else:
        dataframe.rename(columns={'index': 'date'}, inplace=True)
    dataframe['time']=925
    dataframe=dataframe.append(df_min)
    dataframe['datetime']=dataframe['date']*10000+dataframe['time']
    dataframe=dataframe.set_index('datetime').sort_index().fillna(method='ffill')
    dataframe=dataframe.drop(['date','time'],axis=1)
    return dataframe
######获取每日的池子###########
Start_time=20170101
End_time=20191231
###############获取回测股票池:：HS300,ZZ500,ZZ800,ZZ1000,ALL1800#####################
New_stock_pool=pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')
stock_all=list(New_stock_pool.columns)
####计算日内异动个股日间池子#####
#日间池子不能再继续筛选了，因为个股收益率一个月内位于后20%，很大程度上限制了换手率#
def cal_factor(New_stock_pool):
    stock_all = list(New_stock_pool.columns)
    trade_day = tradeDate.get_date_range(20161120, end_date=End_time, period='D', dividing_point=15)
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    high_day = getData.get_daily_1factor('high_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    low_day = getData.get_daily_1factor('low_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    ######获取池子前1个月涨幅最低的20%个股#####
    return_month=close_day/close_day.shift(20)-1
    return_month_rank=return_month.rank(pct=True,axis=1).shift(1)
    stock_choose=(return_month_rank<=0.2).shift(1).loc[20170101:]
    #####日内异动个股################
    ##最高价到收盘价振幅>5%##
    HighChange=(high_day/close_day-1>0.05)
    LowChange=(close_day/low_day-1>0.05)
    BigChange_day=(HighChange+LowChange).shift(1)
    stock_BigChange=New_stock_pool*stock_choose*BigChange_day.loc[20170101:]  #平均每日买入20只
    stock_BigChange = change_day_to_inday(stock_BigChange)
    stock_BigChange.to_hdf('/data/user/015624/factor_BigChange/stock_BigChange.h5', key='stock_BigChange')

cal_factor(New_stock_pool)
stock_BigChange = pd.read_hdf('/data/user/015624/factor_BigChange/stock_BigChange.h5','stock_BigChange')
##########最简单策略：开盘买入，第二天收盘卖出###########
##超额收益-0.0284%，超额胜率45.46%，盈亏比1.1727，持仓数量17个
#9:40之前买入：超额收益-0.0260%，超额胜率45.46%，盈亏比1.1751，持仓数量17个
stock_BigChange['time']=stock_BigChange.index%10000
stock_BigChange[stock_BigChange['time']>940]=0
stock_BigChange.drop('time',axis=1,inplace=True)

temp_factor_signal_1 = FactorBackTest(stock_BigChange)
temp_factor_signal_1.evaluation(24)
print(temp_factor_signal_1.evaluation_result.T)
temp_factor_signal_1.result_output(filename='Factor_BigChange',fileroot='/data/user/015624/factor_BigChange/')
