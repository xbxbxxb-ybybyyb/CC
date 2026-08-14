########################导入部分#########################
import pandas as pd
import numpy as np
import os
import h5py
import sys
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
##判断开盘价是否大于5日均线
def stock_5kline(New_stock_pool):
    stock_all = list(New_stock_pool.columns)
    trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)
    open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    kline_5day=close_day.rolling(5).mean().shift(1)
    stock_pool_5kline=(open_day>=kline_5day)
    return stock_pool_5kline
######获取每日的池子###########
Start_time=20170101
End_time=20191231
###############获取回测股票池:：HS300,ZZ500,ZZ800,ZZ1000,ALL1800#####################
New_stock_pool=pd.read_hdf('/data/group/800319/New_stock_pool.h5','New_stock_pool')
stock_all = list(New_stock_pool.columns)
###计算因子
def cal_factor(New_stock_pool):
    stock_all = list(New_stock_pool.columns)
    #######因子1：隔夜涨幅#############
    trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)
    open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    return_night=(open_day/close_day.shift(1)-1).loc[20170101:]
    ##去掉前10%和后10%的极端值
    return_night_rank=return_night.rank(pct=True,axis=1)
    return_night_rank[return_night_rank<0.05]=np.nan
    return_night_rank[return_night_rank>0.95]=np.nan
    ##去掉开盘涨跌停
    need_del_stock=((round(close_day*1.1*100)/100.0).shift(1)>open_day)+((round(close_day*0.9*100)/100.0).shift(1)<open_day)
    return_night_rank=return_night_rank/need_del_stock

    #######因子2：集合竞价量比:240*集合竞价成交额/过去5日日均成交额###########
    amt_day = getData.get_daily_1factor('amt', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    amt_min=getData.get_minute_1factor('amt', start_datetime=201701010925, end_datetime=201912311500, minute_interval=1, code_list=stock_all, type='stock', diy_address=None)
    Bid_amt=amt_min.reset_index()[amt_min.reset_index()['time']==925].set_index('date').drop('time',axis=1).loc[20170101:]
    amt_5day=amt_day.rolling(5).mean().shift(1)
    Bid_volrate=Bid_amt/amt_5day
    ##去掉开盘涨跌停
    Bid_volrate_rank=(Bid_volrate.rank(pct=True,axis=1)/need_del_stock).loc[20170101:]

    #######因子3：尾盘成交量：收盘前15分钟成交量占比###################
    amt_day = getData.get_daily_1factor('amt', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None)
    amt_min=getData.get_minute_1factor('amt', start_datetime=201701010925, end_datetime=201912311500, minute_interval=1, code_list=stock_all, type='stock', diy_address=None)
    close_amt=amt_min.reset_index()[amt_min.reset_index()['time']>=1445].set_index(['date','time'])
    close_volrate=(close_amt.groupby('date').sum()/amt_day).shift(1).loc[20170101:]
    close_volrate_rank=close_volrate.rank(pct=True,axis=1)

    #########对三个因子进行排列组合，获取最优################
    factor_example = ((return_night > 0.8).loc[20170101:])
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
    average_price = getData.get_daily_1factor('vwap', date_list=list(factor_example.index), code_list=stock_all,
                                              type='stock', diy_address=None)
    # 参数45%,0：胜率49.777%，收益率0.1241%，持仓363个
    # 参数47%，0.0005,：胜率50.17%，收益率0.1592%，持仓262个：胜率43.10%，收益率-0.099%，盈亏比1.194，日均持仓210个
    # 参数48%，0.0008：胜率50.66%，收益率0.18178%，持仓206个
    # 参数50%，0.001：胜率51.10%，收益率0.2136%，持仓135个
    End_factor = pd.DataFrame(0, index=factor_example.index, columns=factor_example.columns)
    list_range = [1, 0.8, 0.6, 0.4, 0.2, 0]
    for t1 in range(1, len(list_range)):
        for t2 in range(1, len(list_range)):
            for t3 in range(1, len(list_range)):
                factor = (return_night_rank >= list_range[t1]) * (return_night_rank <= list_range[t1 - 1]) * \
                         (Bid_volrate_rank >= list_range[t2]) * (Bid_volrate_rank <= list_range[t2 - 1]) * \
                         (close_volrate_rank >= list_range[t3]) * (close_volrate_rank <= list_range[t3 - 1])
                factor = (factor * New_stock_pool * can_buy).loc[20170101:]
                win_rate, average_return = statistics_return(factor,close_day,open_day)
                if win_rate > 0.5 and average_return > 0.001:
                    print(t1, t2, t3)
                    print('win_rate:', win_rate, 'average_return:', average_return)
                    End_factor = End_factor + factor
    Factor_inday = change_day_to_inday(End_factor)
    Factor_inday.to_hdf('/data/user/015624/factor_T0/Factor_inday.h5', key='Factor_inday')

cal_factor(New_stock_pool)
#########日间结果###############
##符合条件全部买入：胜率43.15%，收益率-0.0853%，盈亏比1.211，日均持仓119个
##如果只做开盘价>5日均线的个股：胜率42.97%，收益率-0.0344%，盈亏比1.2819，持仓数56个
Factor_inday = pd.read_hdf('/data/user/015624/factor_T0/Factor_inday.h5','Factor_inday')
stock_up_5kline=stock_5kline(New_stock_pool)
stock_up_5kline=change_day_to_inday(stock_up_5kline.loc[20170101:])
Factor_up_5kline=Factor_inday*stock_up_5kline

##只做开盘价>5日均线的个股，小于开盘价买：胜率44.7%，收益率0.0045%，盈亏比1.27，持仓数量47个——选这个
##只做开盘价>5日均线的个股，大于开盘价买：胜率41.97%，收益率-0.0916%，盈亏比1.2639，持仓数量52
close_min=getData.get_minute_1factor('close_badj', start_datetime=201701010925, end_datetime=201912311500, minute_interval=1, code_list=stock_all, type='stock', diy_address=None)
close_min = close_min.reset_index()
close_min=close_min.drop(close_min[close_min['date'] < Start_time].index)
close_min['datetime'] = close_min['date'] * 10000 + close_min['time']
close_min = close_min.set_index('datetime')
close_min=close_min.drop(['date', 'time'], axis=1)
trade_day = tradeDate.get_date_range(20161220, end_date=End_time, period='D', dividing_point=15)
open_day = getData.get_daily_1factor('open_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None).loc[20170101:]
open_day_min=change_day_to_inday(open_day)
price_lower_open=(close_min<=open_day_min)

Factor_buy=Factor_up_5kline*price_lower_open
Factor_buy.to_hdf('/data/user/015624/factor_T0/Factor_buy.h5', key='Factor_buy')

#########因子测试#############
Factor_buy = pd.read_hdf('/data/user/015624/factor_T0/Factor_buy.h5','Factor_buy')
temp_factor_signal = FactorBackTest(Factor_buy)
temp_factor_signal.evaluation(24)
print(temp_factor_signal.evaluation_result.T)
temp_factor_signal.result_output(filename='Factor_T0',fileroot='/data/user/015624/factor_T0/')

'''
###平仓信号：
close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None).shift(1).loc[20170101:]
close_day_min=change_day_to_inday(close_day)
####大于昨收就走：胜率44.1%，收益率-0.1048%，盈亏比1.1013，持仓数49个
sell_bigger_preclose=(close_min>close_day_min)*(-1)
Factor_test_sell=Factor_test_buy*2+sell_bigger_preclose
Factor_test_sell[Factor_test_sell>1]=1
####大于开盘价就走：胜率42.8%，收益率-0.1415%，盈亏比1.1005，持仓数50个
sell_bigger_open=(close_min>open_day_min)*(-1)
Factor_test_sell=Factor_test_buy*2+sell_bigger_open
Factor_test_sell[Factor_test_sell>1]=1
####高开：大于开盘价走，低开：大于昨收价就走:胜率44.72%，收益率-0.0995%，盈亏比1.086，持仓数49个

high_open=(open_day/close_day-1>0).loc[20170101:]
high_open_min=change_day_to_inday(high_open)
high_sell=high_open_min*(close_min>open_day_min)*(-1)
low_open=(open_day/close_day-1<=0).loc[20170101:]
low_open_min=change_day_to_inday(low_open)
low_sell=low_open_min*(close_min>close_day_min)*(-1)
sell_way=high_sell+low_sell
Factor_test_sell=Factor_test_buy*2+sell_way
Factor_test_sell[Factor_test_sell>1]=1
###个股10点后处于日内最高点回调的比例位于市场后10%就卖：
#如果买入卖出信号重叠则不买入：胜率44.68%，收益率-0.0765%，盈亏比1.24，持仓46个
#先买入：胜率42.64%，收益率-0.0643%，盈亏比1.2532，持仓48个
close_min=getData.get_minute_1factor('close_badj', start_datetime=201701010925, end_datetime=201912311500, minute_interval=1, code_list=stock_all, type='stock', diy_address=None)
high_inday=close_min.groupby('date').cummax() #获取每日累计最大值
#获取分钟收益率到最大值的日内收益率
lower_rate=(close_min/high_inday).rank(pct=True,axis=1)
need_sell=(lower_rate<0.2)
need_sell=set_format(need_sell,Start_time)
###把10点前的都变成Fasle
need_sell['time']=need_sell.index%10000
need_sell[need_sell['time']<1000]=False
need_sell.drop(['time'],axis=1,inplace=True)
Factor_allsignal=need_sell*(-1)+Factor_test_buy*2
Factor_allsignal[Factor_allsignal>1]=1
'''

'''
############简单测试#################
def cal_return(factor):
    close_day = getData.get_daily_1factor('close_badj', date_list=list(factor.index), code_list=list(factor.columns),
                                          type='stock', diy_address=None)
    close = getData.get_daily_1factor('close', date_list=list(factor.index), code_list=list(factor.columns),
                                          type='stock', diy_address=None)
    open_day = getData.get_daily_1factor('open_badj', date_list=list(factor.index), code_list=list(factor.columns),
                                         type='stock', diy_address=None)
    high_day = getData.get_daily_1factor('high_badj', date_list=list(factor.index), code_list=list(factor.columns),
                                         type='stock', diy_address=None)
    low_day = getData.get_daily_1factor('low_badj', date_list=list(factor.index), code_list=list(factor.columns),
                                        type='stock', diy_address=None)
    AMT_day = getData.get_daily_1factor('amt', date_list=list(factor.index), code_list=list(factor.columns), type='stock',
                                        diy_address=None)
    Vol_day = getData.get_daily_1factor('volume', date_list=list(factor.index), code_list=list(factor.columns), type='stock',
                                        diy_address=None)
    can_buy = (abs(high_day - low_day) > 0.00001) * (AMT_day > 0)
    average_price = AMT_day / Vol_day*10
    #用均价成交，今天均价买明天均价卖
    return_stock=(average_price.shift(-1)/average_price-1)*factor*can_buy
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    print('均价买卖',win_rate,average_return)
    #今天均价买明天收盘卖
    return_stock=(close.shift(-1)/average_price-1)*factor*can_buy
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    print('均价买，明天收盘卖',win_rate,average_return)
    #今天开盘价买，今天收盘价卖
    return_stock=(close_day/open_day-1)*factor*can_buy
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    print('开盘价买入，今天收盘价卖出',win_rate, average_return)
    #今天开盘价买，明天开盘价卖
    return_stock=(open_day.shift(-1)/open_day-1)*factor*can_buy
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    print('开盘价买入，明天开盘价卖出',win_rate, average_return)
    #今天开盘价买，明天收盘价卖
    return_stock=(close_day.shift(-1)/open_day-1)*factor*can_buy
    return_stock = return_stock.replace(0, np.nan) - 0.0012
    win_rate=(return_stock>0.000001).sum().sum()/factor.sum().sum()
    average_return=return_stock.sum().sum()/factor.sum().sum()
    print('开盘价买入，明天收盘价卖出',win_rate, average_return)
factor_night=(return_night.rank(pct=True,axis=1)<=0.2)*New_stock_pool
cal_return(factor_night)
'''

gc.collect()


