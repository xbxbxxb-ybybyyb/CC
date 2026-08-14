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
        return('error：参数有误')
    return stock_pool
Start_time=20170101
End_time=20191231
stock_pool=get_stock_list('ZZ800',Start_time,End_time)
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
################计算因子值并保存######################
def factor_beta(stock_pool):
    stock_all = list(set(stock_pool.columns.tolist()))
    ##########定义半衰期alpha##################
    half_life = 63
    windows = 252
    alpha = 0.5 ** (1 / half_life)
    weighted_window = np.logspace(1, windows, windows, base=alpha)
    W = np.diag(weighted_window)
    ##########定义个股收益率和风险股票池收益率#################
    trade_day = tradeDate.get_date_range(20151201, end_date=20191231, period='D', dividing_point=15)
    stock_MV = getData.get_daily_1factor('mkt_cap_ard', date_list=trade_day, code_list=stock_all, type='stock', diy_address=None).shift(1)
    stock_close_day = getData.get_daily_1factor('close_badj', date_list=trade_day, code_list=stock_all, type='stock',diy_address=None)
    return_day = stock_close_day / stock_close_day.shift(1) - 1
    #############计算日间参数：回归项和残差项目################
    stock_beta = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    stock_alpha = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_day = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_mean = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_up_mean = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_low_mean = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_std = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_up_std = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    res_low_std = pd.DataFrame(index=return_day.loc[Start_time:].index, columns=return_day.columns)
    for date in stock_beta.index:
        stock_today = stock_pool.loc[date][stock_pool.loc[date] > 0].index.tolist()
        before_date = return_day.index.tolist()[return_day.index.tolist().index(date) - 252]
        risk_return_today = (return_day.loc[before_date:date, stock_today] * stock_MV.loc[before_date:date,stock_today]).sum(axis=1)/\
                            stock_MV.loc[before_date:date,stock_today].sum(axis=1)
        return_today = return_day.loc[before_date:date, stock_today]
        y = return_today.iloc[:-1, :]  # 前252个交易日的结果作为当日的信息
        X = risk_return_today[:-1]
        X = np.vstack((np.ones(X.size), np.array(X)))  # 定义风险股票池收益率X
        stock_reg = np.linalg.inv(X.dot(W).dot(X.T)).dot(X).dot(W).dot(np.array(y))
        stock_beta.loc[date, stock_today] = stock_reg[1, :]
        stock_alpha.loc[date, stock_today] = stock_reg[0, :]
        res = y - X.T.dot(stock_reg)
        res_day.loc[date, stock_today] = res.iloc[-1]
        res_mean.loc[date, stock_today] = res.mean()
        res_up_mean.loc[date, stock_today] = res[res > 0].mean()
        res_low_mean.loc[date, stock_today] = res[res < 0].mean()
        res_std.loc[date, stock_today] = res.std()
        res_up_std.loc[date, stock_today] = res[res > 0].std()
        res_low_std.loc[date, stock_today] = res[res < 0].std()
    #####将前一天市值变成日内参数###########
    get_date = trade_day[trade_day.index(20161230):]
    stock_MV = getData.get_daily_1factor('mkt_cap_ard', date_list=get_date, code_list=stock_all, type='stock',diy_address=None).shift(1)
    stock_MV = stock_MV * stock_pool
    stock_MV = stock_MV.drop(20161230)
    MV_yesterday = change_day_to_inday(stock_MV)
    #####将前一天收盘价变成日内参数######
    stock_close_day = getData.get_daily_1factor('close_badj', date_list=get_date, code_list=stock_all, type='stock',diy_address=None).shift(1)
    stock_close_day = stock_close_day.drop(20161230)
    Close_yesterday = change_day_to_inday(stock_close_day)
    ####将beta,残差，均值变为日内参数####
    stock_beta_yesterday = change_day_to_inday(stock_beta)
    stock_alpha_yesterday = change_day_to_inday(stock_alpha)
    res_day_yesterday = change_day_to_inday(res_day)
    res_mean_yesterday = change_day_to_inday(res_mean)
    res_up_mean_yesterday = change_day_to_inday(res_up_mean)
    res_low_mean_yesterday = change_day_to_inday(res_low_mean)
    stock_pool_min = change_day_to_inday(stock_pool)
    res_std = change_day_to_inday(res_std)
    res_up_std = change_day_to_inday(res_up_std)
    res_low_std = change_day_to_inday(res_low_std)
    ###############计算个股开盘到该分钟的收益率####################
    ####获取分钟收盘价数据#####
    Close_min = getData.get_minute_1factor('close_badj', start_datetime=Start_time, end_datetime=End_time,minute_interval=1, code_list=stock_all, type='stock')
    Close_min = Close_min.reset_index()
    Close_min = Close_min.drop(Close_min[Close_min['date'] < Start_time].index)
    Close_min['datetime'] = Close_min['date'] * 10000 + Close_min['time']
    Close_min = Close_min.set_index('datetime')
    Close_min = Close_min.drop(['date', 'time'], axis=1)
    ######计算开盘至该分钟为止的收益率############
    return_min = Close_min / Close_yesterday - 1
    #####计算开盘至该分钟为止的风险池收益率####
    risk_return_min = (return_min * MV_yesterday).sum(axis=1) / MV_yesterday.sum(axis=1)
    value_theory = pd.DataFrame(index=stock_beta_yesterday.index, columns=stock_beta_yesterday.columns)
    for i in value_theory.columns:
        value_theory[i] = stock_beta_yesterday[i] * risk_return_min + stock_alpha_yesterday[i]
    #######计算因子值:残差#####
    factor = return_min - value_theory
    ######将结果保存到h5文件中方便读取###############
    factor.to_hdf('/data/user/015624/factor_beta/factor_alpha.h5',key='factor')
    stock_beta_yesterday.to_hdf('/data/user/015624/factor_beta/stock_beta_yesterday.h5',key='stock_beta_yesterday')
    stock_alpha_yesterday.to_hdf('/data/user/015624/factor_beta/stock_alpha_yesterday.h5',key='stock_alpha_yesterday')
    res_mean_yesterday.to_hdf('/data/user/015624/factor_beta/res_mean_yesterday.h5',key='res_mean_yesterday')
    res_up_mean_yesterday.to_hdf('/data/user/015624/factor_beta/res_up_mean_yesterday.h5',key='res_up_mean_yesterday')
    res_low_mean_yesterday.to_hdf('/data/user/015624/factor_beta/res_low_mean_yesterday.h5',key='res_low_mean_yesterday')
    res_day_yesterday.to_hdf('/data/user/015624/factor_beta/res_day_yesterday.h5',key='res_day_yesterday')
    stock_pool_min.to_hdf('/data/user/015624/factor_beta/stock_pool_min.h5', key='stock_pool_min')
    res_std.to_hdf('/data/user/015624/factor_beta/res_std.h5', key='res_std')
    res_up_std.to_hdf('/data/user/015624/factor_beta/res_up_std.h5', key='res_up_std')
    res_low_std.to_hdf('/data/user/015624/factor_beta/res_low_std.h5', key='res_low_std')
    return_min.to_hdf('/data/user/015624/factor_beta/return_min.h5', key='return_min')

factor_beta(stock_pool)
########从h5文件中读取数据#################
factor = pd.read_hdf('/data/user/015624/factor_beta/factor_alpha.h5','factor')
stock_beta_yesterday = pd.read_hdf('/data/user/015624/factor_beta/stock_beta_yesterday.h5','stock_beta_yesterday')
stock_alpha_yesterday = pd.read_hdf('/data/user/015624/factor_beta/stock_alpha_yesterday.h5','stock_alpha_yesterday')
res_day_yesterday = pd.read_hdf('/data/user/015624/factor_beta/res_day_yesterday.h5','res_day_yesterday')
res_mean_yesterday = pd.read_hdf('/data/user/015624/factor_beta/res_mean_yesterday.h5','res_mean_yesterday')
res_up_mean_yesterday = pd.read_hdf('/data/user/015624/factor_beta/res_up_mean_yesterday.h5','res_up_mean_yesterday')
res_low_mean_yesterday = pd.read_hdf('/data/user/015624/factor_beta/res_low_mean_yesterday.h5','res_low_mean_yesterday')
stock_pool_min = pd.read_hdf('/data/user/015624/factor_beta/stock_pool_min.h5','stock_pool_min')
res_std = pd.read_hdf('/data/user/015624/factor_beta/res_std.h5','res_std')
res_up_std = pd.read_hdf('/data/user/015624/factor_beta/res_up_std.h5','res_up_std')
res_low_std = pd.read_hdf('/data/user/015624/factor_beta/res_low_std.h5','res_low_std')
return_min = pd.read_hdf('/data/user/015624/factor_beta/return_min.h5','return_min')

#根据beta不同设定不同的触发阈值——买点：
######因子1.1：beta>1时，残差小于下平均-1.6倍标准差，且当日残差>昨日残差买入###
# 1.2倍标准差：超额胜率47.417%，收益率0.0414%，盈亏比1.149
# 1.3倍标准差：超额胜率47.35%，收益率0.0644%，盈亏比1.173
# 1.4倍标准差：超额胜率47.98%，收益率0.0436%，盈亏比1.124
# 1.5倍标准差：超额胜率48.1132%，收益率0.0489%，盈亏比1.1222
# 1.6倍标准差：超额胜率48.60%，收益率0.0828%，盈亏比1.1277  选这个
# 1.7倍标准差：超额胜率48.18%，收益率0.0708%，盈亏比1.1351
# 1.8倍标准差：超额胜率47.26%，收益率0.0324%，盈亏比1.14328
factor_11=((stock_beta_yesterday>=1)*(factor<=res_low_mean_yesterday-1.6*res_low_std)*(factor>res_day_yesterday))*1
factor_11=factor_11*stock_pool_min
factor_11=factor_11[abs(factor_11).sum()[abs(factor_11).sum()!=0].index]

######因子1.2：beta<1时，残差小于下平均-2.1倍标准差，且当日残差>昨日残差买入###
# 2.5倍标准差：超额胜率49.723%，收益率0.066%，盈亏比1.058
# 2.4倍标准差：超额胜率48.73%，收益率0.0869%，盈亏比1.1173
# 2.3倍标准差：超额胜率48.93%，收益率0.0946%，盈亏比1.1159
# 2.2倍标准差：超额胜率48.29%，收益率0.0607%，盈亏比1.1190
# 2.1倍标准差：超额胜率48.99%，收益率0.0981%，盈亏比1.1192 选这个
factor_12=((stock_beta_yesterday<1)*(factor<=res_low_mean_yesterday-2.1*res_low_std)*(factor>res_day_yesterday))*1
factor_12=factor_12*stock_pool_min
factor_12=factor_12[abs(factor_12).sum()[abs(factor_12).sum()!=0].index]

#卖点信号汇总：
######因子1.3：beta>1：残差大于上平均+3.3倍标准差卖出；
# 上平均3.0倍标准差卖出：超额胜率48.60%，收益率0.0836%，盈亏比1.1284
# 上平均3.1倍标准差卖出：超额胜率48.60%，收益率0.0856%，盈亏比1.130
# 上平均3.2倍标准差卖出：超额胜率48.60%，收益率0.0866%，盈亏比1.131
# 上平均3.3倍标准差卖出：超额胜率48.60%，收益率0.0906%，盈亏比1.134  用这个
# 上平均3.4倍标准差卖出：超额胜率48.60%，收益率0.0897%，盈亏比1.1336
factor_11=((stock_beta_yesterday>=1)*(factor<=res_low_mean_yesterday-1.6*res_low_std)*(factor>res_day_yesterday))*1
factor_13=((stock_beta_yesterday>=1)*(factor>=res_up_mean_yesterday+3.1*res_up_std))*(-1)
factor_13=factor_11+factor_13
factor_13=factor_13*stock_pool_min
factor_13=factor_13[abs(factor_13).sum()[abs(factor_13).sum()!=0].index]

#信号汇总：
# 单边胜率50.64%，收益率0.1777%，盈亏比1.0877，信号比率0.1435%
# 超额胜率48.75%，收益率0.0880%，盈亏比1.1241
##买入信号：
factor_buy=((stock_beta_yesterday>=1)*(factor<=res_low_mean_yesterday-1.6*res_low_std)*(factor>res_day_yesterday))*1+\
          ((stock_beta_yesterday<1)*(factor<=res_low_mean_yesterday-2.1*res_low_std)*(factor>res_day_yesterday))*1
##卖出信号：
factor_sell=((stock_beta_yesterday>=1)*(factor>=res_up_mean_yesterday+3.1*res_up_std))*(-1)
factor_all=factor_buy+factor_sell
factor_all=factor_all*stock_pool_min
factor_all=factor_all[abs(factor_all).sum()[abs(factor_all).sum()!=0].index]
factor_all.to_hdf('/data/user/015624/factor_beta/factor_result.h5',key='factor_all')
factor_all = pd.read_hdf('/data/user/015624/factor_beta/factor_result.h5','factor_all')
###############因子回测#################
temp_factor_all = FactorBackTest(factor_all)
temp_factor_all.evaluation(24)
print(temp_factor_all.evaluation_result.T)
###将结果保存到excel
temp_factor_all.result_output(filename='Beta',fileroot='/data/user/015624/factor_beta/')
