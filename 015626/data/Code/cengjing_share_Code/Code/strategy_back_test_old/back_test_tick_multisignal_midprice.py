# -*- coding:UTF-8 -*-
import matplotlib
matplotlib.use('Agg')
import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os
import matplotlib.pyplot as plt
import itertools
import multifactor.utility.dt as udt
from functools import partial
from multiprocessing import Pool
import warnings
# warnings.filterwarnings('ignore')
import dill

# 挂单分配算法，提交给系统组实盘开发所用，本回测用不到
def get_ordernum_per_sig(order_num,need_trade_num_persig):
    deal_vol = 0
    need_trade_num_persig_v2 = []
    for x in need_trade_num_persig:
        #当与挂单方向不同时，认为抵消成交, 成交方向相反
        if x * order_num < 0:
            deal_vol -= x
            need_trade_num_persig_v2.append(0)
        else:
            need_trade_num_persig_v2.append(x)
    deal_num_per_sig = get_deal_vol_per_sig(deal_vol, need_trade_num_persig_v2)
    res_num_per_sig = list(map(lambda x:x[0] - x[1], zip(need_trade_num_persig_v2, deal_num_per_sig)))
    order_num_per_sig = get_deal_vol_per_sig(order_num, res_num_per_sig)
    assert np.sum(order_num_per_sig) == order_num
    for i in range(len(order_num_per_sig)):
        assert np.sign(order_num_per_sig[i]) * np.sign(order_num) >= 0
        assert abs(order_num_per_sig[i]) <= abs(res_num_per_sig[i])
    return order_num_per_sig

def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)

def get_target_pos_from_signal_min(signal, pos_dict):
    if signal != signal:
        signal = 0
    for k, v in pos_dict.items():
        if (abs(signal) >= k[0]) and (abs(signal) < k[1]):
            return v[0]

def get_target_pos_from_signal_max(signal, pos_dict):
    if signal != signal:
        signal = 0
    for k, v in pos_dict.items():
        if (abs(signal) >= k[0]) and (abs(signal) < k[1]):
            return v[1]

def handle_holiday(df):
    pre_date = udt.get_trading_day_offset(df.index.tolist()[0].date(),-1)[0].date()
    datelist = udt.get_trading_date_range(pre_date,df.index.tolist()[-1].date())
    datedict = {}
    for i in range(1, len(datelist)):
        datedict[datelist[i]] = (datelist[i] - datelist[i-1]).days
    daterange = pd.DataFrame(datedict, index = ['days']).T
    deletelist = daterange[daterange.days > 3].index.tolist()

    t_days_list = [str(i)[:10] for i in deletelist]
    t_mins_list = pd.date_range('09:30:00','09:59:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_df = pd.DataFrame({'dt':index_list})
    index_df['dt'] = pd.to_datetime(index_df['dt'])
    index_df = index_df.set_index('dt')

    df.loc[index_df.index & df.index, 'raw'] = 0
    df = df.sort_index()
    return df

def standard_index(signal_df):
    t_days_list = udt.get_trading_date_range(str(signal_df.index[0].date()).replace('-', ''), str(signal_df.index[-1].date()).replace('-', ''))
    t_days_list = [str(i)[:10] for i in t_days_list]
    t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00', '14:56:00', freq='min').to_list()
    t_mins_list = [str(i)[-8:] for i in t_mins_list]
    index_list = []
    for d in t_days_list:
        for m in t_mins_list:
            index_list.append(d + ' ' + m)
    index_min = pd.DataFrame({'dt': index_list})
    index_min['dt'] = pd.to_datetime(index_min['dt'])
    index_min = index_min.set_index('dt').sort_index()
    
    return signal_df.reindex(index_min.index)

def my_argsort(nums):
    return [i[0] for i in sorted(enumerate(nums), key = lambda x:x[1])]

def get_deal_vol_per_sig(deal_vol, need_trade_num_persig):
    if deal_vol == 0:
        return [0] * len(need_trade_num_persig)
    assert 0 < deal_vol / np.sum(need_trade_num_persig) <= 1
    deal_vol_per_sig = []
    close_num = 0
    open_list = []
    open_index_list = []
    for i in range(len(need_trade_num_persig)):
        x = need_trade_num_persig[i]
        if np.sign(deal_vol) * np.sign(x) <= 0:
            deal_vol_per_sig.append(x)
            close_num += x
        else:
            open_list.append(x)
            open_index_list.append(i)
            deal_vol_per_sig.append('wait')
    deal_vol2 = deal_vol - close_num
    total_open_num = np.sum(open_list)
    if deal_vol2 > 0:
        open_allocate_list = [np.floor(deal_vol2 * x / total_open_num) for x in open_list]
        res_num = deal_vol2 - np.sum(open_allocate_list)
        # 按权重从大到小排序，优先分给权重大的
        for idx in my_argsort(open_list)[::-1]:
            temp_num = min(res_num, open_list[idx] - open_allocate_list[idx])
            open_allocate_list[idx] = open_allocate_list[idx] + temp_num
            res_num = res_num - temp_num
            if res_num == 0:
                break
    else:
        open_allocate_list = [np.ceil(deal_vol2 * x / total_open_num) for x in open_list]
        res_num = deal_vol2 - np.sum(open_allocate_list)
        # 按权重从大到小排序，优先分给权重大的，因为open_list为负数，排序越靠前权重越大
        for idx in my_argsort(open_list):
            temp_num = max(res_num, open_list[idx] - open_allocate_list[idx])
            open_allocate_list[idx] = open_allocate_list[idx] + temp_num
            res_num = res_num - temp_num
            if res_num == 0:
                break
    assert res_num == 0
    for i in range(len(open_list)):
        deal_vol_per_sig[open_index_list[i]] = open_allocate_list[i]
        assert abs(open_allocate_list[i]) <= abs(open_list[i])
    assert np.sum(deal_vol_per_sig) == deal_vol
    return deal_vol_per_sig


def allocate_open_close(dealtotal_vol, pre_hold_num, deal_price_list, deal_volume_list, vol_pertick):
    deal_price_list_open = []
    deal_volume_list_open = []
    deal_price_list_close = []
    deal_volume_list_close = []
    pre_hold_num_abs = int(abs(pre_hold_num))
    if np.sign(pre_hold_num) * np.sign(dealtotal_vol) >= 0:
        deal_price_list_open = deal_price_list
        deal_volume_list_open = deal_volume_list
    else:
        if abs(dealtotal_vol) <= pre_hold_num_abs:
            deal_price_list_close = deal_price_list
            deal_volume_list_close = deal_volume_list
        else:
            if vol_pertick == 1:
                deal_price_list_close = deal_price_list[:pre_hold_num_abs]
                deal_volume_list_close = deal_volume_list[:pre_hold_num_abs]
                deal_price_list_open = deal_price_list[pre_hold_num_abs:]
                deal_volume_list_open = deal_volume_list[pre_hold_num_abs:]
            else:
                temp_close_num = 0
                for i2 in range(len(deal_volume_list)):
                    temp_res_num = pre_hold_num_abs - temp_close_num
                    deal_price_list_close.append(deal_price_list[i2])
                    if temp_res_num > deal_volume_list[i2]:
                        deal_volume_list_close.append(deal_volume_list[i2])
                        temp_close_num += deal_volume_list[i2]
                    elif temp_res_num == deal_volume_list[i2]:
                        deal_volume_list_close.append(deal_volume_list[i2])
                        deal_price_list_open = deal_price_list[i2+1:]
                        deal_volume_list_open = deal_volume_list[i2+1:]
                        break
                    else:
                        deal_volume_list_close.append(temp_res_num)
                        deal_price_list_open = deal_price_list[i2:]
                        deal_volume_list_open = [deal_volume_list[i2] - temp_res_num] + deal_volume_list[i2+1:]
                        break
    deal_volume_close = np.sum(deal_volume_list_close)
    deal_volume_open = np.sum(deal_volume_list_open)
    deal_weighted_price_close = np.multiply(np.array([deal_price_list_close]),np.array([deal_volume_list_close])).sum() / deal_volume_close if deal_volume_close > 0 else np.nan
    deal_weighted_price_open = np.multiply(np.array([deal_price_list_open]),np.array([deal_volume_list_open])).sum() / deal_volume_open if deal_volume_open > 0 else np.nan
    return deal_weighted_price_close, deal_volume_close, deal_weighted_price_open, deal_volume_open
#     {'deal_price_list_close':deal_price_list_close,'deal_volume_list_close':deal_volume_list_close,'deal_price_list_open':deal_price_list_open,'deal_volume_list_open':deal_volume_list_open}

def get_timediff_minutes(start_time, end_time):
    m = (end_time - start_time).total_seconds() / 60
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90 + 1
    else:
        return m + 1

# 计算策略评价指标
def strategy_evaluate(pnl, trade, trade_minute, initial_cash):
    """
    :param trade: 每笔交易的df
    :return:
    """

    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    # ===计算累积净值
    results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 3)

    # 计算夏普比率
    pnl['date'] = pnl['dt'].apply(lambda x: x.date())
    sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, '夏普比率'] = sharpe_ratio

    # ===计算年化收益
    annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
            '365 days 00:00:00' / (pnl['dt'].iloc[-1] - pnl['dt'].iloc[0]))

    results.loc[0, '年化收益'] = format(round(annual_return, 3), '.2%')


    
    sharpedailyreturn['equity_curve'] = sharpedailyreturn['change'].cumsum()
    sharpedailyreturn = sharpedailyreturn.reset_index()
    # ===计算最大回撤
    # 计算当日之前的资金曲线的最高点
    sharpedailyreturn['max2here'] = sharpedailyreturn['equity_curve'].expanding().max()
    # 计算到历史最高值到当日的跌幅，drowdwon
    sharpedailyreturn['dd2here'] = sharpedailyreturn['equity_curve'] - sharpedailyreturn['max2here']
    # 计算最大回撤，以及最大回撤结束时间
    end_date, max_draw_down = tuple(sharpedailyreturn.sort_values(by=['dd2here']).iloc[0][['date', 'dd2here']])
    # 计算最大回撤开始时间
    start_date = sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
        'date']
    # 将无关的变量删除
    sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    sharpedailyreturn = sharpedailyreturn.set_index('date')
    results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
    results.loc[0, '最大回撤开始时间'] = str(start_date)
    results.loc[0, '最大回撤结束时间'] = str(end_date)
    

    # ===年化收益/回撤比
    results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)
    
    # ===统计每笔交易
    results.loc[0, '总交易笔数'] = len(trade)  # 交易笔数
    results.loc[0, '平均每天交易笔数'] = round(len(trade) / tradedays, 2)  # 盈利笔数
    results.loc[0, '亏损笔数'] = len(trade.loc[trade['change'] <= 0])  # 亏损笔数
    results.loc[0, '盈利笔数'] = len(trade.loc[trade['change'] > 0])  # 盈利笔数
    results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(trade), '.2%')  # 胜率
    
    longtrade = trade[trade['pos'] == 1]
    shorttrade = trade[trade['pos'] == -1]
    results.loc[0, '做多笔数'] = len(longtrade)  
    if len(longtrade)  > 0:
        results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
    else:
        results.loc[0, '做多胜率'] = np.nan
    results.loc[0, '做空笔数'] = len(shorttrade)
    if len(shorttrade) > 0:
        results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
    else:
        results.loc[0, '做空胜率'] = np.nan
    results.loc[0, '每笔交易平均盈亏'] = round(trade['change'].mean(), 6)  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(trade.loc[trade['change'] > 0]['change'].mean() / \
                                    trade.loc[trade['change'] < 0][
                                        'change'].mean() * (-1), 2)  # 盈亏比

    results.loc[0, '单笔最大盈利'] = format(trade['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = format(trade['change'].min(), '.2%')  # 单笔最大亏损

    # ===统计持仓时间
    trade['持仓时间'] = trade['holding_time']
    max_minutes = trade['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' 分钟'  # 单笔最长持有时间

    min_minutes = trade['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' 分钟'  # 单笔最短持有时间

    mean_minutes = trade['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) + ' 分钟'  # 平均持仓周期

    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(trade['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数
    
    trade_minute['date'] = trade_minute['deal_time'].apply(lambda x:x.date())
    trade_minute['open_value_intraday'] = trade_minute['open_value_intraday'].fillna(method = 'ffill')
    daily_openvalue = trade_minute.groupby('date').agg({'open_value_intraday':lambda x:x.tail(1)}) / 2
    results.loc[0, '平均每日杠杆'] = round(daily_openvalue.open_value_intraday.sum() / len(sharpedailyreturn) / initial_cash, 2)

    results = results.T
    results.columns = ['num']
    return results, sharpedailyreturn, daily_openvalue

def draw_picture(daily_return, open_value, _result, _pnl, save_path, name):
    daily_df = daily_return[['daily_equty_curve']].join(open_value,how = 'left').fillna(0)
    
    fig = plt.figure(figsize=(10, 10))

    ax1 = fig.add_subplot(2, 1, 1)
    ax1.spines['top'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)

    plt.text(0, 1.0, '%s report'%name, fontsize=22)

    text_fontsize = 16

    plt.text(0, 0.9, 'net value:  ' + str(_result.loc['累积净值']), fontsize=text_fontsize)
    plt.text(0, 0.8, 'sharpe:  '+ str(_result.loc['夏普比率']), fontsize=text_fontsize)
    plt.text(0, 0.7, 'annual ret:  '+ str(_result.loc['年化收益']), fontsize=text_fontsize)
    plt.text(0, 0.6, 'MDD:  '+ str(_result.loc['最大回撤']), fontsize=text_fontsize)
    plt.text(0, 0.5, 'MDD sdate: ' + str(_result.loc['最大回撤开始时间']), fontsize=text_fontsize)
    plt.text(0, 0.4, 'MDD edate: ' + str(_result.loc['最大回撤结束时间']), fontsize=text_fontsize)
    plt.text(0, 0.3, 'annual ret/mdd:  ' + str(_result.loc['年化收益/回撤比']), fontsize=text_fontsize)
    plt.text(0, 0.2, 'trade counts:  ' + str(_result.loc['总交易笔数']), fontsize=text_fontsize)
    plt.text(0, 0.1, 'trade counts perday:  ' + str(_result.loc['平均每天交易笔数']), fontsize=text_fontsize)
    plt.text(0, 0, 'win ratio:  ' + str(_result.loc['胜率']), fontsize=text_fontsize)
    
    plt.text(0.5, 0.9, 'ret per trade:  ' + str(_result.loc['每笔交易平均盈亏']), fontsize=text_fontsize)
    plt.text(0.5, 0.8, 'profit win/loss: ' + str(_result.loc['盈亏收益比']), fontsize=text_fontsize)
    plt.text(0.5, 0.7, 'max profit one trade:  ' + str(_result.loc['单笔最大盈利']), fontsize=text_fontsize)
    plt.text(0.5, 0.6, 'max loss one trade:  ' + str(_result.loc['单笔最大亏损']), fontsize=text_fontsize)
    plt.text(0.5, 0.5, 'hold time per trade:  ' + str(_result.loc['平均持仓周期']).split(' ')[0], fontsize=text_fontsize)
    plt.text(0.5, 0.4, 'average leverage:  ' + str(_result.loc['平均每日杠杆']), fontsize=text_fontsize)
    plt.text(0.5, 0.3, 'stop loss count:  ' + str(_result.loc['止损次数']), fontsize=text_fontsize)
    plt.text(0.5, 0.2, 'average open value:  ' + '%.3e'%daily_df.open_value_intraday.mean(), fontsize=text_fontsize)

    plt.xticks([])  # 去掉x轴
    plt.yticks([])  # 去掉y轴

    plt.subplots_adjust(top=0.95, hspace=0)

    ax1 = fig.add_subplot(2, 1, 2)
    if len(daily_return) > 1:
        # 图：分组收益
        xlist = [x.strftime('%Y%m%d') for x in daily_df.index.tolist()]
        ylist = daily_df.daily_equty_curve.tolist()
        ax1.plot(np.arange(len(xlist)), ylist, color='dodgerblue')
        ax1.set_xticks(np.arange(0,len(xlist),step = max(len(xlist)//8, 1)))
        ax1.set_xticklabels([xlist[i] for i in np.arange(0,len(xlist),step = max(len(xlist)//8, 1))])
        plt.ylabel('Return', fontsize='medium')
        ax_right = ax1.twinx()
        ax_right.stackplot(np.arange(daily_df.shape[0]), daily_df.open_value_intraday.values, labels=['open_value'] ,alpha=0.3)
        plt.xlabel('Segment', fontsize='medium')
        plt.ylabel('open value', fontsize='medium')
        # plt.xticks([xlist[i] for i in np.arange(0,len(xlist),step = 15)])
        plt.title('Daily Results', fontsize='large')
    else:
        _pnl.plot(ax = ax1)
        plt.title('profit', fontsize='large')

    plt.subplots_adjust(top=0.95, hspace=0.3)
    plt.savefig(os.path.join(save_path, name + '_result.png'))
    plt.show()
    plt.close()

class TS_BACK_TEST:

    def __init__(self, signal_list, ticker='IC.CFE', start_date = None, end_date = None,
                 tick_price_kind = 'tickslippage',
                 stop_loss=-100,  n_jobs = 24,
                 c_rate=3 / 100000, tickslippage = 1.2, vol_pertick = 1, 
                 delay_tick_num = 0,max_wait_tick_num = 4, no_opening_start_time = [14,30], closing_start_time = [14,51], 
                 trade_start_time = [9,38], trade_end_time = [14,56], save_signal_list = True,
                 save_path='/data/user/', name_prefix=''):
        """
        :param signal_list: 格式为[{'signal':signal1 * -1,'pos_dict':pos_dict1,'cash':initial_cash1}, {'signal':signal2,'pos_dict':pos_dict2,'cash':initial_cash2}]
                            ,有几个信号就传几个dict, 信号dataframe，index为分钟，如果只有一列，则认为此列为信号值，读取行情数据进行测试。
                            如果多列，则第一列需为信号值，在函数内读取行情数据
                            测试时不对信号值做任何处理，使用原始值。
        :param ticker: 交易品种
        :param start_date， end_date: 测试起始结束日期，为None就测全部时间
        :param stop_loss: 止损
        :param n_jobs: 并行使用多少个核
        :param c_rate: 交易费用
        :param tick_slippage: 发单价格滑点
        :param vol_pertick: 每个tick上的成交数量
        :param delay_tick_num: 测试行情是否延迟，延迟几个tick
        :param max_wait_tick_num: 表示一个委托单可以挂多久，不成交就撤单重新挂
        :param no_opening_start_time: 几点不开仓，默认是14:30后不开仓，只平仓
        :param closing_start_time: 几点后只平仓
        :param trade_start_time, trade_end_time: 交易起止时间
        :param save_signal_list: 是否将signal_list参数保存下来
        :param save_path: 结果保存路径
        :param name_prefix: 结果csv命名前缀
        :back_test function return: 一个字典：'results': 策略评价指标,
                'pnl',每分钟累积收益，equity_curve字段表示资金曲线
                'trade_detail': 每笔交易细节，equity_curve字段表示资金曲线,
                'totaltrade_detail', 合并每笔细节的交易记录
                
        """
        assert isinstance(signal_list, list)
        self.signal_list = signal_list
        self.ticker = ticker
        face_value_dict = {'IC.CFE': 200,
                           'IF.CFE': 300,
                           'IH.CFE': 300}
        self.face_value = face_value_dict[self.ticker]
        self.start_date = start_date
        self.end_date = end_date
        self.trade_start_time = datetime.time(trade_start_time[0],trade_start_time[1])
        self.trade_end_time = datetime.time(trade_end_time[0],trade_end_time[1])

        self.signal_df_list = self.prepare_data()

        self.stop_loss = stop_loss * self.initial_cash
        self.c_rate = c_rate
        self.no_opening_start_time = datetime.time(no_opening_start_time[0],no_opening_start_time[1])
        self.closing_start_time = datetime.time(closing_start_time[0],closing_start_time[1])
        
        self.save_path = save_path
        self.name_prefix = name_prefix
        # self.max_open_value = capital_use_rate * self.initial_cash
        
        self.tickslippage = tickslippage
        self.vol_pertick = vol_pertick
        self.max_wait_tick_num = max_wait_tick_num
        self.delay_tick_num = delay_tick_num
        self.tick_price_kind = tick_price_kind
        self.n_jobs = n_jobs

        if self.save_path is not None and not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        if save_signal_list:
            diller(os.path.join(self.save_path, 'signal_list_para.pkl'), signal_list)

        columns_list = self.signal_df_list[0].reset_index().columns.tolist()
        global dt_idx, raw_idx, contract_00_idx, open_idx, close_idx ,low_idx ,vwap_idx ,twap_idx ,pos_price_idx ,pos_min_idx ,pos_max_idx 
        dt_idx = columns_list.index('dt')
        raw_idx = columns_list.index('raw')
        contract_00_idx = columns_list.index('contract_00')
        open_idx = columns_list.index('open')
        close_idx = columns_list.index('close')
        high_idx = columns_list.index('high')
        low_idx = columns_list.index('low')
        vwap_idx = columns_list.index('vwap')
        twap_idx = columns_list.index('twap')
        pos_price_idx = columns_list.index('pos_price')
        pos_min_idx = columns_list.index('pos_min')
        pos_max_idx = columns_list.index('pos_max')

       
    def prepare_data(self):
        signal_df_list = []
        self.initial_cash = 0
        for sig_dict in self.signal_list:
            if self.start_date and self.end_date:
                signal_df = sig_dict['signal'].loc[str(self.start_date):str(self.end_date)]
            else:
                signal_df = sig_dict['signal']

            pos_dict = sig_dict['pos_dict']
            initial_cash = sig_dict['cash']
            self.initial_cash += initial_cash

            if isinstance(signal_df, pd.Series):
                signal_df = signal_df.to_frame()

            # 获取信号开始结束时间，获取行情数据
            start_time = int(str(signal_df.iloc[[0]].index.values[0]).split('T')[0].replace('-', ''))
            end_time = str(signal_df.iloc[[-1]].index.values[0]).split('T')[0]
            end_time = int(str((datetime.datetime.strptime(end_time, '%Y-%m-%d') + datetime.timedelta(1)).date()).replace('-', ''))
            md = None
            if len(signal_df.columns.tolist()) == 1:
                signal_df.columns = ['raw']
                if md is None:
                    md = IO.read_data([start_time, end_time], columns=['contract_00', 'open', 'high', 'low', 'close', 'vwap','volume','twap'],
                                      alt='/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5')
                    md = md.xs(self.ticker, level=1)
                signal_df = signal_df.join(md, how='inner')
            else:
                clist = ['raw'] + signal_df.columns.tolist()[1:]
                signal_df.columns = clist

            signal_df = standard_index(signal_df)
            signal_df = handle_holiday(signal_df)

            pos_price = signal_df['close'].between_time('930','934')
            pos_price = round(pos_price.groupby(pos_price.index.date).mean(), 1)
            signal_df['pos_price'] = pos_price.reindex(signal_df.index, method = 'pad')

            get_target_pos_from_signal_min_temp = partial(get_target_pos_from_signal_min, pos_dict=pos_dict)
            signal_df['pos_min'] = np.sign(signal_df['raw']) * np.floor(signal_df['raw'].apply(get_target_pos_from_signal_min_temp) * initial_cash / signal_df['pos_price'] / self.face_value)
            get_target_pos_from_signal_max_temp = partial(get_target_pos_from_signal_max, pos_dict=pos_dict)
            signal_df['pos_max'] = np.sign(signal_df['raw']) * np.floor(signal_df['raw'].apply(get_target_pos_from_signal_max_temp) * initial_cash / signal_df['pos_price'] / self.face_value)
            signal_df[['pos_min', 'pos_max']] = signal_df[['pos_min', 'pos_max']].shift(1)

            signal_df = signal_df.between_time(self.trade_start_time, self.trade_end_time)
            signal_df['contract_00'] = signal_df['contract_00'].fillna(method = 'bfill')
            signal_df[['raw', 'pos_min', 'pos_max']] = signal_df[['raw', 'pos_min', 'pos_max']].fillna(0)
            signal_df_list.append(signal_df)
        return signal_df_list

    def get_trade_num(self, hold_num, pos_min, pos_max, now_time, stop_loss_flag):
        no_opening_flag = False 
        if stop_loss_flag or (now_time.time() >= self.closing_start_time):
            return 0 - hold_num
        elif now_time.time() >= self.no_opening_start_time:
            no_opening_flag = True

        if (hold_num != 0) and (np.sign(hold_num) != np.sign(pos_max)):
            return 0 - hold_num
        if pos_min == pos_max == 0:
            return 0 - hold_num
        if (pos_min >= 0) and (pos_max > 0):
            if hold_num < pos_min:
                if no_opening_flag:
                    return 0
                else:
                    return pos_min - hold_num
            elif hold_num > pos_max:
                return pos_max - hold_num
            else:
                return 0
        elif (pos_min <= 0) and (pos_max < 0):
            if hold_num > pos_min:
                if no_opening_flag:
                    return 0
                else:
                    return pos_min - hold_num
            elif hold_num < pos_max:
                return pos_max - hold_num
            else:
                return 0
        else:
            raise 'target pos error'

    def back_test_singleday(self, date):
        signal_date_list = []
        for x in self.signal_df_list:
            signal_date_list.append({'signal':x.loc[str(date)].reset_index().values, 'hold_num':0})
                        
        contract = signal_date_list[0]['signal'][0][contract_00_idx].split('.')[0]
        tickdf = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv' % (contract, date), index_col=0, parse_dates=True)[['Buy1Price','Sell1Price','TotalVolumeTrade']]
        tickdf['TotalVolumeTrade'] = tickdf.TotalVolumeTrade.diff()
        tickdf = tickdf.round({'Buy1Price':1,'Sell1Price':1})
        idx_tickdf = tickdf.index
        buy1px_idx = tickdf.columns.tolist().index('Buy1Price')
        sell1px_idx = tickdf.columns.tolist().index('Sell1Price')
        volume_idx = tickdf.columns.tolist().index('TotalVolumeTrade')

        deal_count = 0  # 第几笔交易 每分钟开仓算一笔交易
        now_hold_dealcount = []  # 当前未平仓的开仓序号
        pre_target_pos = (0,0)
        pre_target_pos_state = 0
        profit_intraday = 0
        now_hold_num = 0
        pre_hold_num = 0 #记录上一时刻仓位,计算多少笔交易时使用
        totaldeal_count = 0 #从空仓到持仓再到空仓算一笔交易
        totaltrade_dict = {}
        profit_intradeal = 0 # 计算本次交易收益
        trade_dict = {}
        pnl_dict = {}  # 记录每分钟的资金曲线
        open_value_intraday = 0  # 今日开仓了多少钱 累计
        pre_date = datetime.date(1998, 1, 1)  # 初始前一天日期

        stop_loss_flag = False # 是否触发了止损
        open_max_value_limit_flag = False # 开仓金额是否达到上限
        stop_loss_timelist = []

        date_signal_lenth = len(signal_date_list[0]['signal'])
        for i in range(1, date_signal_lenth):
            sig0 = signal_date_list[0]['signal']
            nowtime = sig0[i][dt_idx]
            close = sig0[i][close_idx]
            last_close = sig0[i - 1][close_idx]  # 上一分钟收盘价
            
            valid_px = sig0[0][close_idx] if i < 5 else sig0[i-5][close_idx] # 判断价格是否有突变的基准价
            
            need_trade_num_persig = []
            raw_signal_persig = []
            target_pos_persig = []
            for sig in signal_date_list:
                hold_num = sig['hold_num']
                pos_min = sig['signal'][i][pos_min_idx]
                pos_max = sig['signal'][i][pos_max_idx]
                need_trade_num_persig.append(self.get_trade_num(hold_num, pos_min, pos_max, nowtime, stop_loss_flag))
                target_pos_persig.append([int(pos_min), int(pos_max)])#记录下来每个策略的目标仓位区间
                raw_signal_persig.append(round(sig['signal'][i][raw_idx],6)) #记录下来每个策略的信号
            need_trade_num = np.sum(need_trade_num_persig) # 此分钟需要交易的数量及方向
            
            if need_trade_num == 0:#此分钟不交易
                # 之前持仓的本分钟收益
                if pre_hold_num != 0:
                    hold_num_profit = self.face_value * pre_hold_num * (close - last_close)  # 此分钟收益
                else:
                    hold_num_profit = 0
                pnl_dict[nowtime] = hold_num_profit
                profit_intraday += hold_num_profit
                profit_intradeal += hold_num_profit
                
                now_hold_num_persig = []
                for i2 in range(len(signal_date_list)):
                    signal_date_list[i2]['hold_num'] = signal_date_list[i2]['hold_num'] + need_trade_num_persig[i2]
                    now_hold_num_persig.append(int(signal_date_list[i2]['hold_num']))                    

                # 如果子模型有交易，记录下来
                if np.any(need_trade_num_persig):
                    dealflag = 'no_direction'
                    # 记录下来本次开仓记录
                    trade_dict[deal_count] = {'deal_count': deal_count, 'pos': 0, 'dealflag':dealflag, 'deal_time': nowtime,
                                              'deal_contract_num': 0,'target_trade_num':0, 'now_hold_num': now_hold_num,
                                              'now_hold_num_persig':now_hold_num_persig,'need_trade_num_persig':need_trade_num_persig, 
                                              'target_pos_persig': str(target_pos_persig), 'signal_persig': str(raw_signal_persig)}
                    deal_count += 1

            else: # 发单
                open_contract_num = abs(need_trade_num)
                need_trade_num_state = np.sign(need_trade_num)
                if (i == (date_signal_lenth - 1)):
                    nexttime = nowtime + (nowtime - sig0[i - 1][dt_idx])
                else:
                    nexttime = sig0[i + 1][dt_idx]
                if nowtime.time() == datetime.time(11,29):
                    if nexttime.time() > datetime.time(11,30):
                        nexttime = pd.Timestamp('%s 113000' % date)
                order_px_para = tickdf.loc[(idx_tickdf.time >= nowtime.time()) & (idx_tickdf.time < nexttime.time())].values

                # the price of the first order
                pre_tickdf = tickdf.loc[idx_tickdf.time < nowtime.time()].iloc[-1*(self.delay_tick_num + 1):].values
                if need_trade_num > 0:
                    open_price = pre_tickdf[0][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[0][sell1px_idx]
                else:
                    open_price = -1 * (pre_tickdf[0][sell1px_idx] - self.tickslippage) if self.tick_price_kind == 'tickslippage' else -1 * pre_tickdf[0][buy1px_idx]
                
                deal_price_list = []
                deal_volume_list = []
                dealtickcount = 0
                usetickcount = 0
                dealtotal_vol = 0
                totalopen_value = 0
                totalopen_fee = 0
                wait_tick_num = 0
                putorder_num = 1
                makedealflag = False
                tick_state = []
                for z in range(len(order_px_para)):
                    if abs(abs(open_price) / valid_px - 1) >= 0.05:
                        if (z != (len(order_px_para) - 1)) and (open_contract_num != 0):
                            putorder_num += 1
                        tick_state.append(0)
                        continue
                    tickvolume = order_px_para[z][volume_idx]

                    deal_price = order_px_para[z][sell1px_idx] if need_trade_num > 0 else order_px_para[z][buy1px_idx] * -1
                    _mid_price = (order_px_para[z][sell1px_idx] + order_px_para[z][buy1px_idx]) / 2
                    _deal_price = _mid_price if need_trade_num > 0 else _mid_price * -1

                    if (round(open_price,1) >= deal_price) and (tickvolume > 0) and not makedealflag:
                        deal_vol = min(self.vol_pertick, open_contract_num)
                        deal_price_list.append(_deal_price * need_trade_num_state)
                        deal_volume_list.append(deal_vol)
                        open_contract_num -= deal_vol

                        open_value = _deal_price * self.face_value * deal_vol * need_trade_num_state
                        open_fee = open_value * self.c_rate
                        open_value_intraday += (open_value + open_fee)
                        totalopen_value += open_value
                        totalopen_fee += open_fee
                        now_hold_num += deal_vol * need_trade_num_state
                        dealtickcount += 1
                        dealtotal_vol += deal_vol * need_trade_num_state

                        tick_state.append(1)
                        makedealflag = True

                    else:# 没成交
                        tick_state.append(0)

                    wait_tick_num += 1    
                    if wait_tick_num >= self.max_wait_tick_num:
                        if z - self.delay_tick_num < 0:
                            if need_trade_num > 0:
                                open_price = pre_tickdf[z+1][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else pre_tickdf[z+1][sell1px_idx]
                            else:
                                open_price = -1 * (pre_tickdf[z+1][sell1px_idx] - self.tickslippage) if self.tick_price_kind == 'tickslippage' else -1 * pre_tickdf[z+1][buy1px_idx]
                        else:
                            if need_trade_num > 0:
                                open_price = order_px_para[z-self.delay_tick_num][buy1px_idx] + self.tickslippage if self.tick_price_kind == 'tickslippage' else order_px_para[z-self.delay_tick_num][sell1px_idx]
                            else:
                                open_price = -1 * (order_px_para[z-self.delay_tick_num][sell1px_idx] - self.tickslippage) if self.tick_price_kind == 'tickslippage' else -1 * order_px_para[z-self.delay_tick_num][buy1px_idx]
                        if (z != (len(order_px_para) - 1)) and (open_contract_num != 0):
                            putorder_num += 1
                        wait_tick_num = 0
                        makedealflag = False

                    usetickcount += 1    
                    if open_contract_num == 0:
                        break

                # 如果当日最后一分钟没平完，按照最后一根tick对价平完
                res_vol = 0
                if nowtime.time() == self.trade_end_time:
                    if now_hold_num != 0:
                        _mid_price = (order_px_para[-1][buy1px_idx] + order_px_para[-1][sell1px_idx]) / 2
                        if now_hold_num > 0:
                            _deal_price = _mid_price
                        elif now_hold_num < 0:
                            _deal_price = _mid_price

                        deal_vol = abs(now_hold_num)
                        res_vol = deal_vol
                        deal_price_list.append(_deal_price)
                        deal_volume_list.append(deal_vol)
                        open_contract_num -= deal_vol

                        open_value = _deal_price * self.face_value * deal_vol
                        open_fee = open_value * self.c_rate
                        open_value_intraday += (open_value + open_fee)
                        totalopen_value += open_value
                        totalopen_fee += open_fee
                        dealtickcount += 1
                        dealtotal_vol += deal_vol * np.sign(now_hold_num) * -1
                        print(nowtime, '强行平仓 ', now_hold_num)
                        now_hold_num += deal_vol * np.sign(now_hold_num) * -1

                        

                # 将此分钟成交分配至各个策略
                deal_vol_per_sig = get_deal_vol_per_sig(dealtotal_vol, need_trade_num_persig)
                now_hold_num_persig = []
                for i2 in range(len(signal_date_list)):
                    signal_date_list[i2]['hold_num'] = signal_date_list[i2]['hold_num'] + deal_vol_per_sig[i2]
                    now_hold_num_persig.append(int(signal_date_list[i2]['hold_num']))

                now_hold_dealcount.append(deal_count)
                
                # 新的收益细节：
                deal_weighted_price_close, deal_volume_close, deal_weighted_price_open, deal_volume_open = allocate_open_close(dealtotal_vol, pre_hold_num, deal_price_list, deal_volume_list, np.max([self.vol_pertick, res_vol]))

                this_deal_closeprofit, this_deal_openprofit, hold_num_profit = 0, 0, 0
                if deal_volume_close > 0:
                    this_deal_closeprofit = self.face_value * deal_volume_close * (deal_weighted_price_close - last_close) * np.sign(pre_hold_num)
                if deal_volume_open > 0:
                    this_deal_openprofit = self.face_value * deal_volume_open * (close - deal_weighted_price_open) * need_trade_num_state
                if abs(pre_hold_num) - deal_volume_close > 0:
                    hold_num_profit = self.face_value * (abs(pre_hold_num) - deal_volume_close) * (close - last_close) * np.sign(pre_hold_num)
                
                dealflag = 'B' if need_trade_num > 0 else 'S'
                # 记录下来本次开仓记录
                trade_dict[deal_count] = {'deal_count': deal_count, 'pos': np.sign(now_hold_num), 'dealflag':dealflag, 'deal_time': nowtime,
                                          'deal_weighted_price_close': deal_weighted_price_close,
                                          'deal_volume_close': deal_volume_close,
                                          'deal_weighted_price_open': deal_weighted_price_open,
                                          'deal_volume_open': deal_volume_open,
                                          'deal_price_list': str(deal_price_list), 'deal_volume_list':deal_volume_list,
                                          'deal_contract_num': dealtotal_vol,'target_trade_num':need_trade_num, 'now_hold_num': now_hold_num,
                                          'now_hold_num_persig':now_hold_num_persig,'need_trade_num_persig':need_trade_num_persig, 'target_pos_persig': str(target_pos_persig), 'signal_persig': str(raw_signal_persig), 
                                          'deal_value': totalopen_value, 'deal_fee': totalopen_fee,'open_value_intraday':open_value_intraday,
                                          'putorder_num':putorder_num, 'dealtickcount': dealtickcount,'usetickcount': usetickcount,'tick_state':str(tick_state),'close':close,'last_close':last_close,'pre_hold_num':pre_hold_num}

                deal_count += 1

                now_hold_num_profit = 0
                profit_thismin = this_deal_closeprofit + this_deal_openprofit + hold_num_profit - totalopen_fee
                pnl_dict[nowtime] = profit_thismin # 此分钟盈亏应为此分钟收益减去手续费
                profit_intraday += profit_thismin
                profit_intradeal += profit_thismin

                if (pre_hold_num == 0) and (now_hold_num != 0):
                    totaltrade_dict[totaldeal_count] = {'totaltrade_count':totaldeal_count,'pos':np.sign(now_hold_num),'open_time':nowtime}
                elif (pre_hold_num != 0) and (now_hold_num == 0):
                    totaltrade_dict[totaldeal_count].update({'pos_close':np.sign(pre_hold_num),'close_time':nowtime,'profit_intradeal':profit_intradeal})
                    profit_intradeal = 0
                    totaldeal_count += 1

            pre_hold_num = now_hold_num
            if profit_intraday < self.stop_loss:
                stop_loss_timelist.append(nowtime)
                stop_loss_flag = True
                print(nowtime, '止损')
            # if open_value_intraday > self.max_open_value:
            #     open_max_value_limit_flag = True

        # return totaltrade_dict, trade_dict, pnl_dict
        return {'totaltrade_dict':pd.DataFrame(totaltrade_dict).T, 'trade_dict':pd.DataFrame(trade_dict).T, 'pnl_dict':pd.DataFrame(pnl_dict, index = ['profit']).T, 'stop_loss_timelist':stop_loss_timelist}

    def back_test(self):
        date_list = [int(x.strftime('%Y%m%d')) for x in set(self.signal_df_list[0].index.date)]
        with Pool(self.n_jobs) as pool:
            rlist = pool.map(self.back_test_singleday, date_list)
        lenth_list = [len(x['trade_dict']) for x in rlist]
        if not np.any(lenth_list):
            print('no trade')
            return None
        totaltrade_df = pd.concat([x['totaltrade_dict'] for x in rlist], axis = 0).sort_values(by = 'open_time')
        trade_df = pd.concat([x['trade_dict'] for x in rlist], axis = 0).sort_values(by = 'deal_time')
        pnl_df = pd.concat([x['pnl_dict'] for x in rlist], axis = 0).sort_index()
        stop_loss_timelist = [x['stop_loss_timelist'][0] for x in rlist if len(x['stop_loss_timelist']) > 0]
        
        totaltrade_df['change'] = totaltrade_df.profit_intradeal / self.initial_cash
        totaltrade_df['equity_curve'] = totaltrade_df.change.cumsum()
        totaltrade_df['holding_time'] = totaltrade_df.apply(lambda x: get_timediff_minutes(x.open_time, x.close_time), axis=1)
        totaltrade_df['totaltrade_count'] = range(len(totaltrade_df))
        
        pnl_df = pnl_df.reset_index()
        pnl_df.columns = ['dt', 'profit']
        pnl_df['change'] = pnl_df['profit'] / self.initial_cash
        pnl_df['equity_curve'] = (pnl_df['profit'].cumsum() + self.initial_cash) / self.initial_cash

        results, daily_return, daily_openvalue = strategy_evaluate(pnl_df.copy(), totaltrade_df.copy(), trade_df.copy(), self.initial_cash)
           
        stop_loss_timelist.sort()
        stoplossdf = pd.DataFrame({'stop_loss_time':stop_loss_timelist})
        stoplossdf['date'] = stoplossdf.stop_loss_time.apply(lambda x:x.date())
        # stoplossdf = stoplossdf.groupby('date').agg({'stop_loss_time':lambda x:x.head(1)})
        
        results.loc['止损次数'] = len(stoplossdf)
        daily_return.columns = ['daily_return','daily_equty_curve']

        pnl_df = pnl_df.set_index('dt')
        pnl = pnl_df[['equity_curve']] - 1
        pnl.columns = ['profit']

        trade_df = trade_df[['deal_time', 'pos', 'dealflag', 'deal_contract_num', 'deal_weighted_price_close', 'deal_volume_close',
         'deal_weighted_price_open', 'deal_volume_open', 'close', 'deal_price_list', 'deal_volume_list', 'now_hold_num', 
         'now_hold_num_persig', 'deal_value', 'deal_fee', 'pre_hold_num', 'signal_persig', 'target_pos_persig', 'target_trade_num',
         'open_value_intraday', 'putorder_num', 'dealtickcount', 'usetickcount', 'tick_state']]
        
        totaltrade_df = totaltrade_df[['totaltrade_count', 'pos',  'open_time', 'close_time', 'pos_close', 'profit_intradeal', 'change',
                                      'equity_curve', 'holding_time']]

        
        
        if self.save_path != None:
            daily_openvalue.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_openvalue.csv'))
            totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_total_trade_detail.csv'), index=False)
            trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_minute_trade_detail.csv'), index=False)
            pnl.to_csv(os.path.join(self.save_path, self.name_prefix + '_pnl.csv'))
            daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + '_results.csv'), encoding='gbk')
            stoplossdf.to_csv(os.path.join(self.save_path, self.name_prefix + '_stop_loss_time.csv'), index=False)
            draw_picture(daily_return, daily_openvalue, results['num'], pnl, self.save_path, self.name_prefix)

            fig = plt.figure(figsize=(20, 10))
            ax1 = fig.add_subplot(1, 1, 1)
            pnl.plot(ax = ax1)
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + '_profit.png'))
            plt.close()

        return {'pnl':pnl, 'results':results, 'trade_df':trade_df, 'totaltrade_dict':totaltrade_df}

# 测试用例多信号
'''
factor = pd.read_hdf('/data/user/012315/share/ts/strategy/minute/ic_prod_v6_102030/res_20211126/ic/prod/norm_nd/pred_comb2.h5')
factor = factor * 2 - 1

data = IO.read_data([start_date_temp,end_date_temp],columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5' % (ticker[:2]))
data = data.reset_index(level = 1).between_time('930', '1456').reset_index().set_index(['dt','Ticker'])
data = data.unstack()['close'].pct_change().rolling(30,min_periods=15).std().stack().reset_index(level = 1)
data.columns = ['Ticker', 'std30']
univ = IO.read_data([start_date_temp,end_date_temp], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
univ = univ.xs(ticker, level = 1)
data = univ.reindex(data.index.unique(), method = 'pad').join(data)
ret_std = data[data.Ticker == data.contract_00][['std30']].sort_index()

factor = ret_std.join(factor, how = 'inner')
factor.columns = ['std','value']


signal1 = factor['value']
signal2 = factor['std'] * factor['value']

pos_dict1 = {(0, 0.6): (0, 0),
                 (0.6, 0.9): (0, 1.0/10),
                 (0.9, 1.1): (1.0/10, 1.0/10)}

pos_dict2 = {(0, 0.0003): (0, 0),
            (0.0003, 0.0004): (0, 0.333/10),
            (0.0004, 0.0005): (0, 0.666/10),
            (0.0005, 0.0006): (0.333/10, 1/10),
            (0.0006, 0.0007): (0.666/10, 1/10),
            (0.0007, 100): (1/10, 1/10)}

initial_cash1 = 5e8
initial_cash2 = 5e8

signal_list = [{'signal':signal1,'pos_dict':pos_dict1,'cash':initial_cash1}, {'signal':signal2,'pos_dict':pos_dict2,'cash':initial_cash2}]

a = TS_BACK_TEST(signal_list,start_date=20200901, end_date=20211001, save_signal_list = False, save_path='/data/user/015626/data/share/factor/back_test/IC_ts/20220224/combine2_reverse',
                 name_prefix='combine')
b = a.back_test_singleday(20201127) # 只测试一天
result = a.back_test() # 测试全部
'''


''' 测试用例单个信号
factor = pd.read_hdf('/data/user/012245/warehouse/vars/wsc/IF_Search_Model.h5')['lgbb'].reset_index(level = 1, drop = True)
factor = ts_rank(factor, 1200)

ticker = 'IF.CFE'
start_date = 20210701
end_date = 20220501
std_adjust = True
signal_name = 'IF_search_lgbb'
date_suffix = '_20'
pos_divnum = 20

start_date_temp = int(udt.get_trading_day_offset(start_date, -2)[0].strftime('%Y%m%d'))
end_date_temp = int(udt.get_trading_day_offset(end_date, 2)[0].strftime('%Y%m%d'))
today = str(int(datetime.datetime.now().strftime('%Y%m%d'))) + date_suffix

std_name = 'origin'
if std_adjust:
    std_name = 'std30'
    # 计算std
    data = IO.read_data([start_date_temp,end_date_temp],columns = ['close'], alt = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/%s_MINUTE.h5' % (ticker[:2]))
    data = data.reset_index(level = 1).between_time('930', '1456').reset_index().set_index(['dt','Ticker'])
    data = data.unstack()['close'].pct_change().rolling(30,min_periods=15).std().stack().reset_index(level = 1)
    data.columns = ['Ticker', 'std30']
    univ = IO.read_data([start_date_temp,end_date_temp], columns = ['contract_00'], alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    univ = univ.xs(ticker, level = 1)
    data = univ.reindex(data.index.unique(), method = 'pad').join(data)
    ret_std = data[data.Ticker == data.contract_00][['std30']].sort_index()

    if isinstance(factor, pd.Series):
        factor = factor.to_frame()
    factor = ret_std.join(factor, how = 'inner')
    factor.columns = ['std','value']
    factor = factor['std'] * factor['value']

save_root_path = '/data/user/015626/data/share/factor/back_test/%s_ts/%s/' % (ticker[:2], today)

pos_dict = {(0,   0.0001): (0,        0),
            (0.0001, 0.0009): (0,        1/pos_divnum),
            (0.0009, 100): (1/pos_divnum,     1/pos_divnum)}


name_prefix = '%s_%s_%s_%s_pos_price' % (signal_name, std_name, start_date, end_date)
save_path = os.path.join(save_root_path,  name_prefix)

signal_list = [{'signal':factor, 'pos_dict':pos_dict, 'cash':5e8}]
ts = TS_BACK_TEST(signal_list, save_signal_list = True, c_rate=3 / 100000, ticker = ticker, stop_loss = -0.005,tickslippage = 0.8, max_wait_tick_num = 4,
                      start_date=start_date, end_date=end_date, save_path=save_path, name_prefix=name_prefix)
result = ts.back_test()
'''