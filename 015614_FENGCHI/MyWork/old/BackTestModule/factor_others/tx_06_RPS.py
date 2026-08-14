########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
import copy
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
    dataframe=dataframe.reset_index()
    dataframe.rename(columns={'index':'date'}, inplace=True)
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
#####计算RPS因子####
def cal_RPS(n,m,New_stock_pool):
    ########定义参数########
    stock_all = list(New_stock_pool.columns)
    ######获取每日的收盘价，最高点，最低点#######
    trade_day = tradeDate.get_date_range(20161115, end_date=End_time, period='D', dividing_point=15)
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock',
                                          diy_address=None)
    Vol_day = getData.get_daily_1factor('volume', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)

    ####过去涨跌幅分位数####
    return_5=(close_day/close_day.shift(n)-1).shift(1).rank(pct=True,axis=1)
    return_20_5=(close_day/close_day.shift(m-n)-1).shift(n+2).rank(pct=True,axis=1,ascending=False)
    ####量比####
    Vol_day_5=Vol_day.rolling(n).sum()
    Vol_day_20_5=Vol_day.rolling(m-n).sum()
    AMT_rate=((Vol_day_5/Vol_day_20_5.shift(n+1)).rank(pct=True,axis=1)).shift(1).loc[20170101:]
    ####阳线比例####
    Red=(open_day<close_day)
    Red=Red.rolling(n).sum()
    Red_rank=Red.rank(pct=True,axis=1,method='max').shift(1).loc[20170101:]

    #########对三个因子进行排列组合，获取最优################
    factor_example = ((return_5 > 0.8).loc[20170101:])
    ###获取2017-2019年三年的开盘价和收盘价
    close_day = getData.get_daily_1factor('close_badj', date_list=list(factor_example.index), code_list=stock_all,
                                          type='stock', diy_address=None)
    open_day = getData.get_daily_1factor('open_badj', date_list=list(factor_example.index), code_list=stock_all,
                                         type='stock', diy_address=None)
    high_day = getData.get_daily_1factor('high_badj', date_list=list(factor_example.index), code_list=stock_all,
                                         type='stock', diy_address=None)
    low_day = getData.get_daily_1factor('low_badj', date_list=list(factor_example.index), code_list=stock_all,
                                        type='stock', diy_address=None)
    AMT_day = getData.get_daily_1factor('amt', date_list=list(factor_example.index), code_list=stock_all, type='stock',
                                        diy_address=None)
    can_buy = (abs(high_day - low_day) > 0.00001) * (AMT_day > 0) * (
                round(close_day.shift(1) * 0.9, 2) + 0.01 <= open_day) * (
                          round(close_day.shift(1) * 1.1, 2) >= open_day)  # 非一字板，非停牌,非开盘跌停
    Factor_RPS = pd.DataFrame(0, index=factor_example.index, columns=factor_example.columns)
    list_range = [1, 0.8, 0.6, 0.4, 0.2, 0]
    for t1 in range(1, len(list_range)):
        for t2 in range(1, len(list_range)):
            for t3 in range(1, len(list_range)):
                for t4 in range(1, len(list_range)):
                    factor = (return_5 >= list_range[t1]) * (return_5 <= list_range[t1 - 1]) * \
                             (return_20_5 >= list_range[t2]) * (return_20_5 <= list_range[t2 - 1]) * \
                             (AMT_rate >= list_range[t3]) * (AMT_rate <= list_range[t3 - 1])*\
                             (Red_rank >= list_range[t4]) * (Red_rank <= list_range[t4 - 1])
                    factor = (factor * New_stock_pool * can_buy).loc[20170101:]
                    win_rate, average_return = statistics_return(factor,close_day,open_day)
                    if win_rate > 0.5 and average_return > 0.001:
                        print(t1, t2, t3,t4)
                        print('win_rate:', win_rate, 'average_return:', average_return)
                        Factor_RPS = Factor_RPS + factor
    Factor_RPS.to_hdf('/data/user/015624/factor_RPS/Factor_RPS.h5', key='Factor_RPS')

cal_RPS(5,20,New_stock_pool)
Factor_RPS = pd.read_hdf('/data/user/015624/factor_RPS/Factor_RPS.h5','Factor_RPS')
RPS_inday=change_day_to_inday(Factor_RPS)
##买一天测试：超额收益-0.364%，胜率44.20%，盈亏比1.218，持仓34个
##低于开盘价买入：超额收益-0.0497%，胜率44.44%，盈亏比1.1882，持仓30个
##开盘买到9点40：超额收益-0.0339%，胜率44.21%，盈亏比1.220，持仓34个
##开盘9：40开始买：超额收益-0.0324%，胜率44.45%，盈亏比1.208，持仓34个

RPS_inday['time']=RPS_inday.index%10000
RPS_inday[RPS_inday['time']>940]=0
RPS_inday.drop('time',axis=1,inplace=True)

temp_factor_signal_1 = FactorBackTest(RPS_inday)
temp_factor_signal_1.evaluation(24)
print(temp_factor_signal_1.evaluation_result.T)
temp_factor_signal_1.result_output(filename='Factor_RPS',fileroot='/data/user/015624/factor_RPS/')