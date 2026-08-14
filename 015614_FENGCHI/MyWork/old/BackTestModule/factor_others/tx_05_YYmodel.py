########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
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
######获取每日的池子###########
Start_time=20170101
End_time=20191231
###############获取回测股票池:：HS300,ZZ500,ZZ800,ZZ1000,ALL1800#####################
New_stock_pool=pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')
stock_all=list(New_stock_pool.columns)
def cal_factor_YY(New_stock_pool):
    stock_all = list(New_stock_pool.columns)
    ######获取每日的收盘价，最高点，最低点#######
    trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)
    open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    high_day = getData.get_daily_1factor('high_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    low_day = getData.get_daily_1factor('low_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)

    #######第一根必须是中阴线或者长阴线：跌幅4%以上##################
    daily_return=close_day/close_day.shift(1)-1
    daily_return=(daily_return<-0.04).shift(2)
    #######第二根必须有下影线，高开且下影线跌破昨收，上影线不能太长########
    ## 最低价<昨日收盘价，开盘价>昨日收盘价；最高价<前一天开盘价
    daily_Kline_result=(low_day<close_day.shift(1))*(open_day>close_day.shift(1))*(high_day<open_day.shift(1))
    daily_Kline_result=daily_Kline_result.shift(1)
    #######今天K线必须高开：今日开盘价>昨日收盘价
    open_high=(open_day>close_day.shift(1))
    ####把满足条件的个股加入到池子中####
    stock_choice=(daily_return*daily_Kline_result*open_high*New_stock_pool).loc[20170101:]
    stock_choice_min = change_day_to_inday(stock_choice)
    stock_choice_min.to_hdf('/data/user/015624/factor_YY/stock_YY.h5','stock_YY')

cal_factor_YY(New_stock_pool)
stock_YY=pd.read_hdf('/data/user/015624/factor_YY/stock_YY.h5','stock_YY')
###开盘买入（9:40前买入）
##-3% 超额收益-0.1083%，超额胜率43.49%，盈亏比1.1625，信号比率0.0308%
##-4% 超额收益-0.0430%，超额胜率45.73%，盈亏比1.1369，信号比率0.0163%
##-3% 低于开盘价买入：超额收益-10.75%，超额胜率43.53%，盈亏比1.161，信号比率0.0305%
##-4% 低于开盘价买入：超额收益-0.0367%，超额胜率45.86%，盈亏比1.138，信号比率0.0162%
trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)
close_min = getData.get_minute_1factor('close', start_datetime=Start_time, end_datetime=End_time, minute_interval=1,
                                           code_list=stock_all, type='stock')
close_min = close_min.reset_index()
close_min = close_min.drop(close_min[close_min['date'] < Start_time].index)
close_min['datetime'] = close_min['date'] * 10000 + close_min['time']
close_min = close_min.set_index('datetime')
close_min = close_min.drop(['date', 'time'], axis=1)
open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
open_day_min=change_day_to_inday(open_day.loc[20170101:])
factor=(close_min<open_day_min)*stock_YY*1

factor['time']=factor.index%10000
factor[factor['time']>940]=0
factor.drop('time',axis=1,inplace=True)

temp_factor_signal = FactorBackTest(factor)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
temp_factor_signal.result_output(filename='Factor_YY',fileroot='/data/user/015624/factor_YY/')


