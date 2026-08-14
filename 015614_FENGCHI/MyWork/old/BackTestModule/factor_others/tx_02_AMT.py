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
###############获取回测股票池:：HS300,ZZ500,ZZ800,ZZ1000,ALL1800#####################
def get_stock_list(pool,Start_time,End_time):
    if pool=='HS300' or pool=='ZZ500' or pool=='ZZ1000':
        stock_pool= pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5',pool).loc[Start_time:End_time]
    elif pool=='ZZ800':
        stock_pool_500 = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'ZZ500').loc[Start_time:End_time]
        stock_pool_300 = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', 'HS300').loc[Start_time:End_time]
        stock_500 = pd.DataFrame(index=stock_pool_500.index,columns=list(set(stock_pool_300.columns.append(stock_pool_500.columns))))
        stock_500[stock_pool_500.columns] = stock_pool_500
        stock_500 = stock_500.fillna(0)
        stock_300 = pd.DataFrame(index=stock_pool_500.index,columns=list(set(stock_pool_300.columns.append(stock_pool_500.columns))))
        stock_300[stock_pool_300.columns] = stock_pool_300
        stock_300 = stock_300.fillna(0)
        stock_pool = stock_300 + stock_500
    elif pool=='ALL1800':
        stock_pool = getData.get_daily_1factor('common_stock_list').loc[Start_time:End_time]
    else:
        stock_pool=pd.DataFrame(None)
    return stock_pool
Start_time=20170101
End_time=20191231
stock_pool=get_stock_list('ZZ800',Start_time,End_time)
#########计算日间成交量大于常规成交量时的收益数据#########
def get_DailyData(n,Start_time,End_time,stock_pool):
    ##获取日间后复权收盘价，日成交量
    trade_day = tradeDate.get_date_range(20161201, end_date=End_time, period='D', dividing_point=15)
    stock_all = list(set(stock_pool.columns.tolist()))
    ###计算个股收益
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    return_day=close_day/close_day.shift(1)-1
    #定义上成交量和下成交量
    AMT_day = getData.get_daily_1factor('amt', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    AMT_day=AMT_day.replace(0,np.nan)
    AMT_mean=pd.DataFrame(index=AMT_day.index,columns=AMT_day.columns)
    AMT_std=pd.DataFrame(index=AMT_day.index,columns=AMT_day.columns)
    for stock in AMT_day.columns:
        AMT_mean[stock]=AMT_day[stock].dropna().rolling(n).mean()
        AMT_std[stock]=AMT_day[stock].dropna().rolling(n).std()
    AMT_up=(AMT_mean+0.66*AMT_std)
    AMT_low=(AMT_mean-0.66*AMT_std)
    ###定义因子：超过上成交量部分的收益总和
    return_up=copy.copy(return_day)
    return_up[AMT_day<AMT_up]=0
    return_up=return_up.rolling(n).sum().shift(1)  ##如果个股出现了长时间停牌，那么复牌后的成交量和复牌前的成交量几乎无关
    return_up=return_up.loc[Start_time:]
    return AMT_day,return_up,trade_day
####获取该分钟的过去n日成交量的最大值/均值/标准差####
def Factor_min_compare_day(n,AMT_min,way):
    if way=='max':
        AMT_min_mean_by_day = AMT_min.groupby('time').rolling(n).max().shift(1)
        AMT_min_mean_by_day.index.rename(['date1', 'date', 'time'], inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.reset_index()
        AMT_min_mean_by_day['datetime'] = AMT_min_mean_by_day['date'] * 10000 + AMT_min_mean_by_day['time']
        AMT_min_mean_by_day = AMT_min_mean_by_day.drop(['date1', 'date', 'time'], axis=1)
        AMT_min_mean_by_day.set_index('datetime', inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.sort_index().shift(1).loc[201701010925:]
        AMT_min_mean_by_day = AMT_min_mean_by_day.replace(0, np.nan)
    elif way=='mean':
        AMT_min_mean_by_day = AMT_min.groupby('time').rolling(n).mean().shift(1)
        AMT_min_mean_by_day.index.rename(['date1', 'date', 'time'], inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.reset_index()
        AMT_min_mean_by_day['datetime'] = AMT_min_mean_by_day['date'] * 10000 + AMT_min_mean_by_day['time']
        AMT_min_mean_by_day = AMT_min_mean_by_day.drop(['date1', 'date', 'time'], axis=1)
        AMT_min_mean_by_day.set_index('datetime', inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.sort_index().shift(1).loc[201701010925:]
        AMT_min_mean_by_day = AMT_min_mean_by_day.replace(0, np.nan)
    elif way=='std':
        AMT_min_mean_by_day = AMT_min.groupby('time').rolling(n).std().shift(1)
        AMT_min_mean_by_day.index.rename(['date1', 'date', 'time'], inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.reset_index()
        AMT_min_mean_by_day['datetime'] = AMT_min_mean_by_day['date'] * 10000 + AMT_min_mean_by_day['time']
        AMT_min_mean_by_day = AMT_min_mean_by_day.drop(['date1', 'date', 'time'], axis=1)
        AMT_min_mean_by_day.set_index('datetime', inplace=True)
        AMT_min_mean_by_day = AMT_min_mean_by_day.sort_index().shift(1).loc[201701010925:]
        AMT_min_mean_by_day = AMT_min_mean_by_day.replace(0, np.nan)
    else:
        AMT_min_mean_by_day=pd.DataFrame(None)
    return AMT_min_mean_by_day
####获取从开盘到该分钟的累计成交量###
def Factor_min_sum(AMT_min):
    AMT_min_by_open=AMT_min.groupby('date').apply(lambda x:x.cumsum(axis=0))
    AMT_min_by_open=AMT_min_by_open.reset_index()
    AMT_min_by_open['datetime']=AMT_min_by_open['date']*10000+AMT_min_by_open['time']
    AMT_min_by_open=AMT_min_by_open.drop(['date','time'],axis=1)
    AMT_min_by_open.set_index('datetime',inplace=True)
    AMT_min_by_open=AMT_min_by_open.sort_index().loc[201701010925:]
    return AMT_min_by_open
################计算因子值并保存######################
def factor_AMT(stock_pool,n):
    ####AMT_day是没有前置的数据，return_up是前置后的数据（即当日的值是昨天的结果）
    AMT_day, return_up, trade_day = get_DailyData(n, Start_time, End_time, stock_pool)
    #############把日间参数变成日内参数#############
    return_up_min = change_day_to_inday(return_up)
    AMT_day_min = change_day_to_inday(AMT_day.shift(1).loc[20170101:])
    stock_pool_min = change_day_to_inday(stock_pool)
    #########获取日内分钟成交量#########
    get_date = trade_day[trade_day.index(20161201):]
    stock_all = list(set(stock_pool.columns.tolist()))
    AMT_min = getData.get_minute_1factor('amt', start_datetime=Start_time, end_datetime=End_time, minute_interval=1,
                                         code_list=stock_all, type='stock', diy_address=None)
    ###再把成交量的格式统一起来##
    AMT = AMT_min.reset_index()
    AMT['datetime'] = AMT['date'] * 10000 + AMT['time']
    AMT.drop(['date', 'time'], axis=1, inplace=True)
    AMT.set_index('datetime', inplace=True)
    AMT = AMT.sort_index().loc[201701010925:]
    ####获取该分钟的过去n日成交量的最大值/均值/标准差，从开盘到该分钟的累计成交量
    AMT_min_max = Factor_min_compare_day(n, AMT_min, 'max')
    AMT_min_mean = Factor_min_compare_day(n, AMT_min, 'mean')
    AMT_min_std = Factor_min_compare_day(n, AMT_min, 'std')
    AMT_min_by_open = Factor_min_sum(AMT_min)
    ###获取当日市值=股价*自由流通股本
    Close_min = getData.get_minute_1factor('close', start_datetime=Start_time, end_datetime=End_time, minute_interval=1,
                                           code_list=stock_all, type='stock')
    Close_min = Close_min.reset_index()
    Close_min = Close_min.drop(Close_min[Close_min['date'] < Start_time].index)
    Close_min['datetime'] = Close_min['date'] * 10000 + Close_min['time']
    Close_min = Close_min.set_index('datetime')
    Close_min = Close_min.drop(['date', 'time'], axis=1)
    Free_shares = getData.get_daily_1factor('free_float_shares', date_list=get_date, code_list=stock_all, type='stock',
                                            diy_address=None).loc[20170101:] * 10000
    Free_shares_min = change_day_to_inday(Free_shares)  # 单位是万股
    Market_free_value = Close_min * Free_shares_min
    ###获取当日收益率#####
    Close_min = getData.get_minute_1factor('close_badj', start_datetime=Start_time, end_datetime=End_time,
                                           minute_interval=1, code_list=stock_all, type='stock')
    Close_min = Close_min.reset_index()
    Close_min = Close_min.drop(Close_min[Close_min['date'] < Start_time].index)
    Close_min['datetime'] = Close_min['date'] * 10000 + Close_min['time']
    Close_min = Close_min.set_index('datetime')
    Close_min = Close_min.drop(['date', 'time'], axis=1)
    stock_close_day = getData.get_daily_1factor('close_badj', date_list=get_date, code_list=stock_all, type='stock',
                                                diy_address=None).shift(1).loc[20170101:]
    Close_yesterday = change_day_to_inday(stock_close_day)
    return_min = Close_min / Close_yesterday - 1
    stock_close_day = getData.get_daily_1factor('close_badj', date_list=get_date, code_list=stock_all, type='stock',
                                                diy_address=None).loc[20161220:]
    return_day = stock_close_day / stock_close_day.shift(1) - 1
    return_yesterday = return_day.shift(1).loc[20170101:]
    return_day_to_yesterday = return_day.shift(2).loc[20170101:]
    return_yesterday_to_yesterday = return_day.shift(3).loc[20170101:]
    return_yesterday = change_day_to_inday(return_yesterday)
    return_day_to_yesterday = change_day_to_inday(return_day_to_yesterday)
    return_yesterday_to_yesterday = change_day_to_inday(return_yesterday_to_yesterday)
    ###保存数据
    AMT_min_max.to_hdf('/data/user/015624/factor_AMT/AMT_min_max.h5', key='AMT_min_max')
    AMT_min_mean.to_hdf('/data/user/015624/factor_AMT/AMT_min_mean.h5', key='AMT_min_mean')
    AMT_min_std.to_hdf('/data/user/015624/factor_AMT/AMT_min_std.h5', key='AMT_min_std')
    AMT_min_by_open.to_hdf('/data/user/015624/factor_AMT/AMT_min_by_open.h5', key='AMT_min_by_open')
    return_up_min.to_hdf('/data/user/015624/factor_AMT/return_up_min.h5', key='return_up_min')
    AMT.to_hdf('/data/user/015624/factor_AMT/AMT.h5', key='AMT')
    stock_pool_min.to_hdf('/data/user/015624/factor_AMT/stock_pool_min.h5', key='stock_pool_min')
    Market_free_value.to_hdf('/data/user/015624/factor_AMT/Market_free_value.h5', key='Market_free_value')
    return_min.to_hdf('/data/user/015624/factor_AMT/return_min.h5', key='return_min')
    return_yesterday.to_hdf('/data/user/015624/factor_AMT/return_yesterday.h5', key='return_yesterday')
    return_day_to_yesterday.to_hdf('/data/user/015624/factor_AMT/return_day_to_yesterday.h5',key='return_day_to_yesterday')
    return_yesterday_to_yesterday.to_hdf('/data/user/015624/factor_AMT/return_yesterday_to_yesterday.h5',key='return_yesterday_to_yesterday')

factor_AMT(stock_pool,10)
###读取数据
AMT_min_max = pd.read_hdf('/data/user/015624/factor_AMT/AMT_min_max.h5','AMT_min_max')
AMT_min_mean = pd.read_hdf('/data/user/015624/factor_AMT/AMT_min_mean.h5','AMT_min_mean')
AMT_min_std = pd.read_hdf('/data/user/015624/factor_AMT/AMT_min_std.h5','AMT_min_std')
AMT_min_by_open = pd.read_hdf('/data/user/015624/factor_AMT/AMT_min_by_open.h5','AMT_min_by_open')
return_up_min = pd.read_hdf('/data/user/015624/factor_AMT/return_up_min.h5','return_up_min')
AMT = pd.read_hdf('/data/user/015624/factor_AMT/AMT.h5','AMT')
stock_pool_min = pd.read_hdf('/data/user/015624/factor_AMT/stock_pool_min.h5','stock_pool_min')
Market_free_value = pd.read_hdf('/data/user/015624/factor_AMT/Market_free_value.h5','Market_free_value')
return_min = pd.read_hdf('/data/user/015624/factor_AMT/return_min.h5','return_min')
return_yesterday = pd.read_hdf('/data/user/015624/factor_AMT/return_yesterday.h5','return_yesterday')
return_day_to_yesterday = pd.read_hdf('/data/user/015624/factor_AMT/return_day_to_yesterday.h5','return_day_to_yesterday')
return_yesterday_to_yesterday = pd.read_hdf('/data/user/015624/factor_AMT/return_yesterday_to_yesterday.h5','return_yesterday_to_yesterday')


##因子测试
# 注意点1：因为过去几天也有放量，所以不能按照最大值的逻辑来做

##当昨日成交量激增收益return_up_min>0时，如果该分钟成交量>该分钟过去10日成交量的最大值就买入
# 大于最大值：超额胜率41.41%，平均收益-0.1552%，盈亏比1.1815，信号比例5.76%
# 大于平均值：超额胜率41.22%，平均收益-0.1477%，盈亏比1.2102，信号比例20.68%
# 大于平均值+0.66倍标准差：超额胜率41.29%，平均收益-0.1569%，盈亏比1.190，信号比例12.38%
# 大于平均值小于最大值：超额胜率41.17%，平均收益-0.1477%，盈亏比1.212，信号比例14.92%
# 大于平均值小于平均值+0.66倍标准差：超额胜率41.13%，平均收益-0.1657%，盈亏比1.1856，信号比例8.30%
factor_11=((return_up_min>0.0001)*(AMT>AMT_min_mean))*1
factor_11=factor_11*stock_pool_min
factor_11=factor_11[abs(factor_11).sum()[abs(factor_11).sum()!=0].index]

##当昨日成交量激增收益return_up_min>0时，该分钟成交量>该分钟过去10日成交量的平均值：
# 且日内分钟成交量在市场前列10%才买入：超额胜率41.32%，平均收益-14.10%，盈亏比1.209，信号比例4.83%
# 且日内分钟成交量在市场前列20%才买入：超额胜率41.4%，平均收益-14.55%，盈亏比1.198，信号比例9.03%
# 且日内分钟成交量在市场前列30%才买入：超额胜率41.44%，平均收益-14.64%，盈亏比1.197，信号比例12.51%
# 且日内分钟成交量在市场前列40%才买入：超额胜率41.39%，平均收益-14.20%，盈亏比1.207，信号比例15.28%——继续调整
# 且日内分钟成交量在市场前列50%才买入：超额胜率41.24%，平均收益-14.24%，盈亏比1.207，信号比例17.39%

# 且下跌超过5%才买：超额胜率47.13%，平均收益-0.1001%，盈亏比1.0336，信号比例0.3283%
# 且下跌超过4%才买：超额胜率46.28%，平均收益-0.0980%，盈亏比1.0654，信号比例0.5740%
# 且下跌超过3%才买：超额胜率45.92%，平均收益-0.0875%，盈亏比1.0833，信号比例1.07%
# 且下跌超过2%才买：超额胜率45.25%，平均收益-0.0676%，盈亏比1.127，信号比例2.06%——调整
# 且下跌超过2%，低于5%才买：超额胜率45.25%，平均收益-0.0695%，盈亏比1.125，信号比例1.74%

# 且昨日收益率>0才买：超额胜率44.72%，平均收益-0.00816%，盈亏比1.139，信号比例1.11%
# 且前日收益率>0才买：超额胜率45.57%，平均收益-0.0045%，盈亏比1.189，信号比例1.13%
# 昨日且前日收益率>0才买：超额胜率45.23%，平均收益-0.0024%，盈亏比1.208，信号比例0.6%

#买点信号汇总：
#基准：过去10日的放量收益>0,且该分钟收益率>过去10分钟收益率均值，且该分钟成交量在市场前40%，且日内到该分钟收益率<-2%：
#超额胜率45.25%，平均收益-0.0676%，盈亏比1.127，信号比例2.06%
#1、且前日收益率>0: 超额胜率45.57%，平均收益-0.0045%，盈亏比1.189，信号比例1.13%
#2、且昨日和前日收益率都>0: 超额胜率45.23%，平均收益-0.0024%，盈亏比1.208，信号比例0.6%
#3、且前日和大前日收益都>0: 超额胜率46.29%，平均收益0.0173%，盈亏比1.18，信号比率0.589%

#卖点信号汇总：
# 当日涨幅低于5%就卖出
#基准：超额胜率44.91%，平均收益-0.096%，盈亏比1.1098，信号比例1.7396%
#1：超额胜率45.83%，平均收益-0.0030%，盈亏比1.178，信号比例1.13%
#2：超额胜率45.61%，平均收益0.0103%，盈亏比1.204，信号比例0.5991%
#3：超额胜率46.56%，平均收益0.0195%，盈亏比1.17，信号比例0.0589%——选了这个

# 当日涨幅超过5%就卖出
#基准：超额胜率45.44%，平均收益-0.0647%，盈亏比1.122，信号比例2.06%
#1：超额胜率45.28%，平均收益-0.035%，盈亏比1.166，信号比例0.96%
#2：超额胜率44.93%，平均收益-0.0443%，盈亏比1.175，信号比例0.5172%
#3：超额胜率46.05$，平均收益-0.0131%，盈亏比1.156，信号比例0.5035%

min_compare=AMT/Market_free_value
min_compare=min_compare.rank(axis=1,pct=True)
factor_12=((return_up_min>0.0001)*(AMT>AMT_min_mean)*(min_compare>=0.6)*(return_min<-0.02)*(return_day_to_yesterday>0)*(return_yesterday_to_yesterday>0))*1+(return_min>0.05)*(-1)
factor_12=factor_12*stock_pool_min
factor_12=factor_12[abs(factor_12).sum()[abs(factor_12).sum()!=0].index]
temp_factor_signal = FactorBackTest(factor_12)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
temp_factor_signal.result_output(filename='AMT',fileroot='/data/user/015624/factor_AMT/')


temp_factor_signal = FactorBackTest(End_factor_min)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
