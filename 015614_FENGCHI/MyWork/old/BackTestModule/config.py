# from xquant.marketdata import MarketData
from xquant.factordata import FactorData
import os
from xquant.strategy.backtest.Performance import *
from dataApi.getData import  *
import pandas as pd
import matplotlib.finance as fnc
import matplotlib.pyplot as plt
import datetime
from multiprocessing import Pool
from matplotlib.dates import DateFormatter, WeekdayLocator, DayLocator, MONDAY, date2num

s = FactorData()
# mdp = MarketData()
root_path = '/data/group/800319/junkData/'
# ZZ500_daily_stock_pool =pd.read_pickle('%s/ZZ500_daily_pool.pkl'%root_path)

def get_stock_pool(key='common_stock_list'):
    check = pd.read_hdf('/data/group/800319/junkData/daily/common_stock_list.h5', key)
    check = check.T
    stock_pool = {}
    for day in check.columns:
        stock_pool[day] = check[check[day]].index.tolist()
        # print(day, len(stock_pool[day]))
    return stock_pool
ZZ500_daily_stock_pool = get_stock_pool('ZZ500')
HS300_daily_stock_pool = get_stock_pool('HS300')
ZZ800_daily_stock_pool = {}
for day in HS300_daily_stock_pool:
    ZZ800_daily_stock_pool[day] = list(set(HS300_daily_stock_pool[day]).union(set(ZZ500_daily_stock_pool[day])))
common_stock_list_pool = get_stock_pool()


def get_index_comp(start_date:int,end_date:int,index_id:str):
    """
    获取指定指数历史一段时间内每天的成分股列表
    :param start_date:
    :param end_date:
    :param index_id:
    :return: dict：keys 日期  values该日期的成分股代码List
    """
    pool_dict = {}
    trading_day = s.tradingday(start_date, end_date, \
                               frequency='DAY', dayType=None, dateType='TRADINGDAYS')
    for day in trading_day:
        temp_comp = s.hset('INDEX', day, index_id)
        pool_dict[int(day)] = temp_comp['stock'].apply(lambda x: int(x[:-3])).tolist()
    return pool_dict

def load_minutes_data(stk_id,trading_days,object_type='stock'):
    """
    读取某只标的某个区间内的分钟行情数据
    :param stk_id: int/str
    :param trading_days: list([int])
    :return: pd.DataFrame(index=[date_time:int],columns=[stock_id:int])
    """
    if object_type=='stock':
        data_path = 'minuteByStock'
    elif object_type=='index':
        data_path = 'minuteByStockBench'
    else:
        raise Exception('Undefined objective type "%s"')%object_type

    if not os.path.exists('%s/%s/%s.h5'%(root_path,data_path,str(stk_id))):
        raise Exception("Minutes data of stock %s are not exist in local!"%str(stk_id))
    # h5 = pd.HDFStore('%s/%s/%s.h5'%(root_path,data_path,str(stk_id)),'r')
    # data = h5['/%s'%str(stk_id)]
    # h5.close()
    data = pd.read_hdf('%s/%s/%s.h5'%(root_path,data_path,str(stk_id)),'/%s'%str(stk_id))
    data['datetime'] = data['date']*10000+data['time']
    data = data[data['date'].isin(trading_days)]
    data = data.set_index('datetime').drop(['date','time'],axis=1)
    # data = data.loc[trading_days[0]*10000:trading_days[-1]*10000+1501]
    return data

def get_net_value_evaluation(net_value, benchmark_net):
    Pf = Performance()
    annual_return = Pf.Annualized_Returns(net_value, start_date = net_value.index[0], end_date = net_value.index[-1])
    benchmark_return = Pf.Benchmark_Returns(benchmark_net, start_date = benchmark_net.index[0], end_date = benchmark_net.index[-1])
    annual_excess = annual_return[0][0] - benchmark_return[0][0]
    volatility = Pf.Volatility(net_value, start_date = net_value.index[0], end_date = net_value.index[-1])
    sharpe = Pf.Sharpe_Ratio(net_value, end_date = net_value.index[-1], rf = 0.02, start_date = net_value.index[0])
    MDD = (1 - net_value[net_value.columns[0]] / net_value[net_value.columns[0]].cummax()).max()
    daily_profit = net_value[net_value.columns[0]].pct_change()
    daily_active = daily_profit - benchmark_net[benchmark_net.columns[0]].pct_change()
    active_win_rate = (daily_active>0).sum()/len(daily_active.dropna())
    profit_win_rate = (daily_profit>0).sum()/len(daily_profit.dropna())
    net_evaluation = pd.DataFrame([annual_return[0][0], annual_excess, volatility[0], sharpe[0][0], profit_win_rate, active_win_rate, MDD],
                                  index = ['Annual Return', 'Annual Excess', 'Volatility', 'Sharpe', 'profit_win_rate', 'active_win_rate', 'MDD'])

    return net_evaluation

def getEXRightDividend(start,end,stk_list):

    EXRightDividend = s.get_factor_value(
        "WIND_AShareEXRightDividendRecord",
        factors=['BONUS_SHARE_RATIO', 'CONVERSED_RATIO', 'RIGHTSISSUE_RATIO', 'SEO_RATIO', 'RIGHTSISSUE_PRICE',
                 'SEO_PRICE', 'CASH_DIVIDEND_RATIO', 'EX_DATE', 'S_INFO_WINDCODE'],
        EX_DATE = ['>='+str(start),'<='+str(end)],
    )

    EXRightDividend['shareRatio'] = EXRightDividend[['BONUS_SHARE_RATIO', 'CONVERSED_RATIO',
            'RIGHTSISSUE_RATIO', 'SEO_RATIO']].sum(axis=1)
    EXRightDividend['receiveRatio'] = pd.concat([EXRightDividend['RIGHTSISSUE_RATIO'] * EXRightDividend[
            'RIGHTSISSUE_PRICE'], EXRightDividend['SEO_RATIO'] * EXRightDividend['SEO_PRICE']], axis=1).sum(axis=1)
    EXRightDividend['payoutRatio'] = EXRightDividend['CASH_DIVIDEND_RATIO']
    EXRightDividend = EXRightDividend[['EX_DATE', 'S_INFO_WINDCODE', 'shareRatio', 'receiveRatio', 'payoutRatio']]
    EXRightDividend.columns = ['date', 'code', 'shareRatio', 'receiveRatio', 'payoutRatio']
    EXRightDividend['date'] = EXRightDividend['date'].map(int)
    EXRightDividend = EXRightDividend[EXRightDividend['code'].map(lambda x: x[0]).isin(['0','3','6'])]
    EXRightDividend['code'] = EXRightDividend['code'].map(lambda x: int(x[:6]))
    EXRightDividend = EXRightDividend[EXRightDividend['code'].isin(stk_list)]
    EXRightDividend = EXRightDividend.sort_values('date')
    return EXRightDividend

def out_fig(para):
    stk_id, out_path, signal_list, mkt_piece = para
    check = mkt_piece.reset_index()
    check['index'] = check['index'].apply(lambda x : datetime.datetime.strptime(str(x),'%Y%m%d%H%M'))#.apply(date2num)
    check = check.set_index('index')
    check['fake_date'] = [x for x in range(len(check))]
    signal = signal_list.rename(index={x : datetime.datetime.strptime(str(x),'%Y%m%d%H%M') for x in signal_list.index})

    fig, ax = plt.subplots(figsize=(20,10))
    fnc.candlestick_ochl(
        ax=ax,
        quotes=check[['fake_date', 'open', 'close', 'high', 'low']].values,
        width=0.5,
        colorup='r',
        colordown='g',
        alpha=0.7)
    for idx in signal.index:
        if signal.loc[idx,'signal'] == 1 and signal.loc[idx,'executed signal']==1:
            plt.scatter(check.index.tolist().index(idx),check.loc[idx,'close'],marker = 'v',color = 'r',s=300)
        if signal.loc[idx,'signal'] == -1 and signal.loc[idx,'executed signal']==1:
            plt.scatter(check.index.tolist().index(idx),check.loc[idx,'close'],marker = 'o',color = 'g',s=300)
        if signal.loc[idx,'signal'] == -1 and signal.loc[idx,'executed signal']==0:
            plt.scatter(check.index.tolist().index(idx),check.loc[idx,'close'],marker = 'x',color = 'g',s=300)
        if signal.loc[idx,'signal'] == -2 and signal.loc[idx,'executed signal']==0:
            plt.scatter(check.index.tolist().index(idx),check.loc[idx,'close'],marker = 'o',color = 'y',s=300)
    plt.plot(check['fake_date'],check[mkt_piece.columns[-1]],label='Benchmark')
    plt.plot(check['fake_date'],check['close']-check[mkt_piece.columns[-1]]+1,label='Excess')
    plt.legend(fontsize=16)
    plt.xticks([check['fake_date'].tolist()[int(i*len(check)/5)] for i in range(5)]+[check['fake_date'].tolist()[-1]],
               [check.index[int(i*len(check)/5)] for i in range(5)]+[check.index[-1]],rotation=30)
    plt.savefig(out_path+'%d_%d_%d.jpg'%(stk_id,int(mkt_piece.index[0]/10000),int(mkt_piece.index[-1]/10000)))
    plt.show()
