from multifactor.IO import IO
import pandas as pd

pd.set_option('max_rows',200)

import pandas as pd
import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime
from multifactor.IO import IO
import itertools

import warnings
warnings.filterwarnings('ignore')

def evaluate(signal, ticker, price_kind = 'vwap', long_in = 0.5, long_out = 0.5, short_in = -10000, short_out = -0.5
            ,initial_cash = 10000000,  c_rate = 2.5 / 100000, slippage = 0.6, leverage_rate = 1):
    if isinstance(signal, pd.Series):
        signal = signal.to_frame()
    signal.columns = ['raw']
    #获取信号开始结束时间，获取行情数据
    start_time = int(str(signal.ix[[0]].index.values[0]).split('T')[0].replace('-',''))
    end_time = str(signal.ix[[-1]].index.values[0]).split('T')[0]
    end_time = int(str((datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)).date()).replace('-',''))
    
    md = IO.read_data([start_time, end_time],columns = ['open','high','low','close','vwap'], alt = '/data/user/012245/warehouse/prod/MD/CHINA_FUTURES/MINUTE/MAIN/MD_CHINA_FUTURES_MINUTE_MAIN.h5')
    md = md.xs(ticker, level = 1)
    
    df = signal.join(md)
    
    #每天只交易9:35-14:50时间段
    idx = df.index
    t1 = df.loc[(idx.hour == 9) & (idx.minute >= 34)]
    t2 = df.loc[(idx.hour >= 10) & (idx.hour <=13)]
    t3 = df.loc[(idx.hour == 14) & (idx.minute <= 55)]
    t = t1.append(t2).append(t3)
    t = t.sort_index()
    t = t.reset_index()
    t['date'] = t['dt'].apply(lambda x:x.date())
    # 将每天数据的第一条以及后两条设置为0,确保不持隔夜仓
    alist = t.groupby('date').apply(lambda x:x.dt.iloc[0]).tolist()
    blist = t.groupby('date').apply(lambda x:x.dt.iloc[-2:]).tolist()
    t.loc[t.dt.isin(alist),'raw'] = 0
    t.loc[t.dt.isin(blist),'raw'] = 0
    t.drop(['date'], axis = 1, inplace=True)
    t = t.set_index('dt')
    
    df = t.sort_index()
    
    face_value_dict = {
        'IC.CFE':200,
        'IF.CFE':300,
        'IH.CFE':300
    }
    
    # 获取开平仓信号
    df = get_signal_from_threshold(df, long_in, long_out, short_in, short_out)
    
    # 获取当前持仓状态
    df = get_position_from_signal(df)
    
    # 获取资金曲线
    df = get_equity_curve_from_pos(df, price_kind=price_kind, initial_cash = initial_cash, face_value = face_value_dict[ticker], c_rate = c_rate, slippage=slippage, leverage_rate = leverage_rate)
    
    # 获取每笔交易细节
    trade = transfer_equity_curve_to_trade(df)
    
    # 获取策略评价各项指标
    results, monthly_return = strategy_evaluate(df, trade)
    
    # 返回各项指标， 资金曲线， 每笔交易细节， 每月收益
    return results, df[['equity_curve']] - 1, trade, monthly_return

# 获取开平仓信号
def get_signal_from_threshold(df, long_in = 0.5, long_out = 0.2, short_in = -0.5, short_out = -0.5):
    #找出做多信号
    condition1 = df['raw'] > long_in
    condition2 = df['raw'].shift(1) <= long_in
    df.loc[condition1 & condition2, 'signal_long'] = 1
    
    #找出做多平仓信号
    condition1 = df['raw'] < long_out
    condition2 = df['raw'].shift(1) >= long_out
    df.loc[condition1 & condition2, 'signal_long'] = 0
    
    # 找出做空信号
    condition1 = df['raw'] < short_in
    condition2 = df['raw'].shift(1) >= short_in
    df.loc[condition1 & condition2, 'signal_short'] = -1
    
    #找出做空平仓信号
    condition1 = df['raw'] > short_out
    condition2 = df['raw'].shift(1) <= short_out
    df.loc[condition1 & condition2, 'signal_short'] = 0
    
    # 合并信号，当同时出现平仓开仓信号时，视为无效交易，只平仓不开仓
    df['signal'] = df[['signal_long','signal_short']].prod(axis = 1, min_count = 1)
    
    # 下午14:30后不开仓
    idx = df.index
    df.loc[(idx.hour == 14) & (idx.minute > 30) & ((df.signal == 1) | (df.signal == -1)),'signal'] = np.nan
    
    temp = df[df['signal'].notnull()][['signal']]
    temp['signal'] = temp['signal'].astype('int')
    temp = temp[temp['signal'] != temp['signal'].shift(1)]
    df['signal'] = temp['signal']
    
    df = df.drop(['signal_long','signal_short'], axis = 1)
    return df

# 根据开平仓信号计算当前仓位
def get_position_from_signal(df):
    df['signal'].fillna(method = 'ffill', inplace = True)
    df['signal'].fillna(value = 0, inplace = True)
    df['pos'] = df['signal'].shift()
    df['pos'].fillna(value = 0, inplace = True)
#     df.drop(['signal'], axis = 1, inplace=True)
    return df

# 根据仓位获取资金曲线
def get_equity_curve_from_pos(df, price_kind, initial_cash = 10000000, face_value = 200, c_rate = 2.3 / 100000, slippage=0.6, leverage_rate = 1):
    df = df.reset_index()
    # 下根k线开盘价
    df['next_' + price_kind] = df[price_kind].shift(-1)
    df['next_' + price_kind].fillna(value = df[price_kind], inplace = True)
    
    # 找出开平仓的k线
    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(1)
    open_pos_condition = condition1 & condition2
    
    condition1 = df['pos'] != 0
    condition2 = df['pos'] != df['pos'].shift(-1)
    close_pos_condition = condition1 & condition2
    
    # 对每次交易进行分组
    df.loc[open_pos_condition, 'start_time'] = df['dt']
    df['start_time'].fillna(method = 'ffill', inplace = True)
    df.loc[df['pos'] == 0,'start_time'] = pd.NaT
    
    # 开始计算资金曲线
    # 在open_pos_condition的k线，以指定价格种类计算买入数量。
    df.loc[open_pos_condition, 'contract_num'] = initial_cash * leverage_rate / (face_value * df[price_kind])
    df['contract_num'] = np.floor(df['contract_num']) # 向下取整
    # 开仓价格
    df.loc[open_pos_condition, 'open_pos_price'] = df[price_kind] + slippage * df['pos']
    # 开仓后剩余的钱,扣除手续费
    df['cash'] = initial_cash - df['open_pos_price'] * face_value * df['contract_num'] * c_rate
    
    # 开仓之后cash, contract_num, open_pos_price不再变动
    for _ in ['contract_num', 'open_pos_price', 'cash']:
        df[_].fillna(method = 'ffill', inplace = True)
    df.loc[df['pos'] == 0, ['contract_num','open_pos_price','cash']] = None
    
    # 在平仓时
    df.loc[close_pos_condition, 'close_pos_price'] = df['next_' + price_kind] - slippage * df['pos']
    # 平仓后手续费
    df.loc[close_pos_condition, 'close_pos_fee'] = df['close_pos_price'] * face_value * df['contract_num'] * c_rate
    
    # 计算利润
    # 持仓至今盈亏
    df['profit'] = face_value * df['contract_num'] * (df['close'] - df['open_pos_price']) * df['pos']
    df.loc[close_pos_condition, 'profit'] = face_value * df['contract_num'] * (df['close_pos_price'] - df['open_pos_price']) * df['pos']
    
    # 账户净值
    df['net_value'] = df['cash'] + df['profit']
    
    # 平仓时扣除手续费
    df.loc[close_pos_condition, 'net_value'] -= df['close_pos_fee']
    
    # 计算资金收益率曲线
    df['equity_change'] = df['net_value'].pct_change()
    df.loc[open_pos_condition, 'equity_change'] = df.loc[open_pos_condition, 'net_value'] / initial_cash - 1
    df['equity_change'].fillna(value = 0, inplace = True)
    df['equity_curve'] = (1 + df['equity_change']).cumprod()
    
    df = df.drop(['next_' + price_kind, 'contract_num',  'cash', 'close_pos_fee', 'profit', 'net_value'], axis = 1)
    
    return df
    
 # 将资金曲线数据，转化为交易数据
def transfer_equity_curve_to_trade(equity_curve):

    # =选取开仓、平仓条件
    condition1 = equity_curve['pos'] != 0
    condition2 = equity_curve['pos'] != equity_curve['pos'].shift(1)
    open_pos_condition = condition1 & condition2

    # =对每次交易进行分组
    if 'start_time' not in equity_curve.columns:
        equity_curve.loc[open_pos_condition, 'start_time'] = equity_curve['dt']
        equity_curve['start_time'].fillna(method='ffill', inplace=True)
        equity_curve.loc[equity_curve['pos'] == 0, 'start_time'] = pd.NaT

    # =遍历每笔交易
    trade = pd.DataFrame()
    for _index, group in equity_curve.groupby('start_time'):
        _i = len(trade)
        trade.loc[_i, 'signal'] = group['pos'].iloc[0]  # 本次交易方向
        if 'leverage_rate' in group:
            trade.loc[_i, 'leverage_rate'] = group['leverage_rate'].iloc[0]

        g = group[group['pos'] != 0]
        trade.loc[_i, 'start_bar'] = _index  # 本次交易开始时间
        trade.loc[_i, 'end_bar'] = g.iloc[-1]['dt']  # 本次交易结束那根K线的开始时间
        trade.loc[_i, 'start_price'] = g.iloc[0]['open_pos_price']  # 开仓价格
        trade.loc[_i, 'end_price'] = g.iloc[-1]['close_pos_price']  # 平仓价格
        trade.loc[_i, 'bar_num'] = g.shape[0]  # 交易周期
        trade.loc[_i, 'change'] = (group['equity_change'] + 1).prod() - 1  # 本次交易收益
        trade.loc[_i, 'end_equity_curve'] = g.iloc[-1]['equity_curve']  # 本次交易结束时资金曲线
        trade.loc[_i, 'min_equity_curve'] = g['equity_curve'].min()

    return trade


# 计算策略评价指标
def strategy_evaluate(equity_curve, trade):
    """
    :param equity_curve: 带资金曲线的df
    :param trade: transfer_equity_curve_to_trade的输出结果，每笔交易的df
    :return:
    """

    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    # ===计算累积净值
    results.loc[0, '累积净值'] = round(equity_curve['equity_curve'].iloc[-1], 2)

    # 计算夏普比率
    equity_curve['equity_ratio'] = equity_curve['equity_change'] + 1
    equity_curve['date'] = equity_curve['dt'].apply(lambda x:x.date())
    sharpedailyreturn = equity_curve.groupby('date')['equity_ratio'].prod().to_frame()
    sharpedailyreturn['equity_ratio'] = sharpedailyreturn['equity_ratio'] - 1
    sharpe_ratio = round(sharpedailyreturn['equity_ratio'].mean()/sharpedailyreturn['equity_ratio'].std()*np.sqrt(252),3)
    results.loc[0, '夏普比率'] = sharpe_ratio
    
    # ===计算年化收益
    annual_return = (equity_curve['equity_curve'].iloc[-1] / equity_curve['equity_curve'].iloc[0]) ** (
        '1 days 00:00:00' / (equity_curve['dt'].iloc[-1] - equity_curve['dt'].iloc[0]) * 365) - 1
    results.loc[0, '年化收益'] = format(round(annual_return, 2), '.1%') 
    

    # ===计算最大回撤
    # 计算当日之前的资金曲线的最高点
    equity_curve['max2here'] = equity_curve['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    equity_curve['dd2here'] = equity_curve['equity_curve'] / equity_curve['max2here'] - 1
    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(equity_curve.sort_values(by=['dd2here']).iloc[0][['dt', 'dd2here']])
    # 计算最大回撤开始时间
    start_date = equity_curve[equity_curve['dt'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0]['dt']
    # 将无关的变量删除
    equity_curve.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
    results.loc[0, '最大回撤开始时间'] = str(start_date)
    results.loc[0, '最大回撤结束时间'] = str(end_date)

    # ===年化收益/回撤比
    results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)

    # ===统计每笔交易
    results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
    results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
    results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率

    results.loc[0, '每笔交易平均盈亏'] = format(trade['change'].mean(), '.2%')  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                    trade.loc[trade['change'] < 0][
                                        'change'].mean() * (-1), 2)  # 盈亏比

    results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

    # ===统计持仓时间
    trade['持仓时间'] = trade['bar_num']
    max_minutes = trade['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' 分钟'  # 单笔最长持有时间

    min_minutes = trade['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' 分钟'  # 单笔最短持有时间

    mean_minutes = trade['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes,1)) + ' 分钟'  # 平均持仓周期

    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

    # ===每月收益率
    equity_curve.set_index('dt', inplace=True)
    monthly_return = equity_curve[['equity_change']].resample(rule='M').apply(lambda x: (1 + x).prod() - 1)

    results = results.T
    results.columns = ['num']
    return results, monthly_return   
    
# factor = pd.read_hdf('/data/user/012398/data/MD/IC_long.h5')
# a,b,c,d = evaluate(factor,'IC.CFE')
# print(a)
