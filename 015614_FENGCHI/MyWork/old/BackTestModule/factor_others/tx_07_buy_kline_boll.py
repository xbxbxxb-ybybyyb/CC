########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
import copy
import gc
from xquant.factordata import FactorData
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
    if stock_df==['ZZ500']:
        min_date = getData.get_minute_1factor('close', start_datetime=start_time, end_datetime=end_time,
                                              minute_interval=1, code_list=stock_df, type='bench')
    else:
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
        dataframe.rename(columns={name: 'date'}, inplace=True)
    else:
        dataframe.rename(columns={'index': 'date'}, inplace=True)
    dataframe['time']=925
    dataframe=dataframe.append(df_min)
    dataframe['datetime']=dataframe['date']*10000+dataframe['time']
    dataframe=dataframe.set_index('datetime').sort_index().fillna(method='ffill')
    dataframe=dataframe.drop(['date','time'],axis=1)
    return dataframe
############将提取的日内格式变成单索引的日内格式#########
def set_format(factor_min,Start_time):
    factor_min = factor_min.reset_index()
    factor_min = factor_min.drop(factor_min[factor_min['date'] < Start_time].index)
    factor_min['datetime'] = factor_min['date'] * 10000 + factor_min['time']
    factor_min = factor_min.set_index('datetime')
    factor_min = factor_min.drop(['date', 'time'], axis=1)
    return factor_min
############日间效果简单测试：第一开开盘价买入，第二天收盘价卖出#############
def statistics_return(factor,close_day,open_day):
    return_stock=(close_day.shift(-1)/open_day-1)*factor
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    return win_rate,average_return
######获取每日的池子###########
Start_time=20170101
End_time=20191231
###############获取回测股票池:：HS300,ZZ500,ZZ800,ZZ1000,ALL1800#####################
New_stock_pool=pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')
stock_all=list(New_stock_pool.columns)
trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)

def cal_buy_factor(trade_day,stock_all):
    ##因子1：5分钟均线上穿10分钟均线，且超额收益分位数位于后30%
    excess_return_close=pd.read_hdf('/data/user/015624/Data_inday/excess_return_close.h5','excess_return_close') #相对于昨日的超额收益
    excess_return_rank=excess_return_close.rank(pct=True,axis=1)
    close_min=getData.get_minute_1factor('close_badj', start_datetime=201701010925, end_datetime=201912311500, minute_interval=1, code_list=stock_all, type='stock', diy_address=None)
    kline_5min=close_min.rolling(5).mean()
    kline_20min=close_min.rolling(20).mean()
    up=(kline_5min>kline_20min)
    up=set_format(up,Start_time)
    factor_kline=up*(excess_return_rank<=0.3)*(excess_return_rank>0.05)
    ###因子2：股价上穿日boll带中线
    stock_close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock',diy_address=None)
    middle_rail=stock_close_day.rolling(5).mean().shift(1)
    middle_rail_inday=change_day_to_inday(middle_rail.loc[20170101:])
    close_min=set_format(close_min,Start_time)
    factor_boll=(close_min>middle_rail_inday)*((close_min.shift(1)<middle_rail_inday))

    factor_kline_boll=(factor_kline*factor_boll)
    factor_kline_boll.to_hdf('/data/user/015624/factor_inday/factor_kline_boll.h5', key='factor_kline_boll')
    ###对比端：要买的个股都开盘就买
    factor_kline_boll['date'] = factor_kline_boll.index // 10000
    fator_allday = factor_kline_boll.groupby('date').sum()
    fator_allday[fator_allday > 1] = 1
    fator_allday = change_day_to_inday(fator_allday)
    fator_allday.to_hdf('/data/user/015624/factor_inday/fator_allday.h5', key='fator_allday')

##进行测试
factor_kline_boll=pd.read_hdf('/data/user/015624/factor_inday/factor_kline_boll.h5',key='factor_kline_boll')
temp_factor_signal = FactorBackTest(factor_kline_boll)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
temp_factor_signal.result_output(filename='factor_kline_boll',fileroot='/data/user/015624/factor_inday/')
gc.collect()

fator_allday=pd.read_hdf('/data/user/015624/factor_inday/fator_allday.h5', key='fator_allday')
temp_factor_signal = FactorBackTest(fator_allday)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
temp_factor_signal.result_output(filename='fator_kline_boll_allday',fileroot='/data/user/015624/factor_inday/')
gc.collect()