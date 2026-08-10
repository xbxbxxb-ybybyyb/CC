# %matplotlib inline
# -*- coding:UTF-8 -*-
import matplotlib
import pandas as pd
import numpy as np
import datetime
from multifactor.IO import IO
from tqdm import tqdm
import os, copy, time
import matplotlib.pyplot as plt
import multifactor.utility.dt as udt
from multiprocessing import Pool
import itertools
import warnings
warnings.filterwarnings('ignore')

class Order:
    def __init__(self, symbol=None, action=None, submit_price=None, fill_price=None, quantity=0, status=None,
                 create_sig = None, create_time=None, finish_sig = None, finish_time=None, 
                 create_tick_pxlist=[], finish_tick_pxlist=[], hold_tick_num = 0, finish_tick_deal_estimate = None, hold_closetick_num = 0):
        self.symbol = symbol
        self.action = action  # buy_open sell_open buy_close sell_close
        self.submit_price = submit_price  # 发单价格
        self.fill_price = fill_price  # 成交价格
        self.quantity = quantity
        self.status = status  # 订单当前的状态submit为挂单 fill为已经成交 cancel为已经撤销
        self.create_sig = create_sig # 触发开仓的信号
        self.create_time = create_time  # 在哪个信号bar的时间戳上发的单
        self.finish_sig = finish_sig # 触发平仓的信号
        self.finish_time = finish_time  # 在哪个信号bar的时间戳上成交的
        self.create_tick_pxlist = create_tick_pxlist  # 基于哪个tick挂的单，此tick的[buy1price, sell1price, lastpx]
        self.finish_tick_pxlist = finish_tick_pxlist  # 基于哪个tick成交的，此tick的[buy1price, sell1price, lastpx]
        self.hold_tick_num = hold_tick_num # 持续了多少根tick
        self.finish_tick_deal_estimate = finish_tick_deal_estimate # 平仓那根tick的成交估计
        self.hold_closetick_num = hold_closetick_num # 平仓单持续了多少根低于出场阈值的tick，平仓单撤单重发时用
        
def strategy_evaluate(pnl, initial_cash, total_order_counts, cancel_order_counts):
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    # ===计算累积净值
    results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 6)

    # 计算夏普比率
    pnl['date'] = pnl['create_time'].apply(lambda x: x.date())
    sharpedailyreturn = pnl.groupby('date')['change'].sum().to_frame()
    tradedays = len(sharpedailyreturn)
    sharpe_ratio = round(sharpedailyreturn['change'].mean() / sharpedailyreturn['change'].std() * np.sqrt(252), 3)
    results.loc[0, '夏普比率'] = sharpe_ratio

    # ===计算年化收益
    annual_return = (pnl['equity_curve'].iloc[-1] / pnl['equity_curve'].iloc[0] - 1) * (
            '365 days 00:00:00' / (pnl['finish_time'].iloc[-1] - pnl['create_time'].iloc[0]))

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
    start_date = \
    sharpedailyreturn[sharpedailyreturn['date'] <= end_date].sort_values(by='equity_curve', ascending=False).iloc[0][
        'date']
    # 将无关的变量删除
    sharpedailyreturn.drop(['max2here', 'dd2here'], axis=1, inplace=True)
    sharpedailyreturn = sharpedailyreturn.set_index('date')
    results.loc[0, '最大回撤'] = format(max_draw_down, '.6%')
    results.loc[0, '最大回撤开始时间'] = str(start_date)
    results.loc[0, '最大回撤结束时间'] = str(end_date)

    # ===年化收益/回撤比
    results.loc[0, '年化收益/回撤比'] = round(abs(annual_return / max_draw_down), 2)

    # ===统计每笔交易
    results.loc[0, '总交易笔数'] = len(pnl)  # 交易笔数
    results.loc[0, '平均每天交易笔数'] = round(len(pnl) / tradedays, 2)  # 盈利笔数
    results.loc[0, '亏损笔数'] = len(pnl.loc[pnl['change'] <= 0])  # 亏损笔数
    results.loc[0, '盈利笔数'] = len(pnl.loc[pnl['change'] > 0])  # 盈利笔数
    results.loc[0, '总委托单数量'] = total_order_counts
    results.loc[0, '成交率'] = format((total_order_counts - cancel_order_counts) / total_order_counts, '.2%')
    results.loc[0, '总撤单数量'] = cancel_order_counts
    results.loc[0, '撤单率'] = format(cancel_order_counts / total_order_counts, '.2%')
    results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(pnl), '.2%')  # 胜率

    longtrade = pnl[pnl['pos'] == 1]
    shorttrade = pnl[pnl['pos'] == -1]
    results.loc[0, '做多盈利'] = longtrade.change.sum()
    results.loc[0, '做空盈利'] = shorttrade.change.sum()
    results.loc[0, '做多笔数'] = len(longtrade)
    if len(longtrade) > 0:
        results.loc[0, '做多胜率'] = format(len(longtrade[longtrade.change > 0]) / len(longtrade), '.2%')  # 胜率
    else:
        results.loc[0, '做多胜率'] = np.nan
    results.loc[0, '做空笔数'] = len(shorttrade)
    if len(shorttrade) > 0:
        results.loc[0, '做空胜率'] = format(len(shorttrade[shorttrade.change > 0]) / len(shorttrade), '.2%')  # 胜率
    else:
        results.loc[0, '做空胜率'] = np.nan
    results.loc[0, '每笔交易平均盈亏'] = round(pnl['change'].mean(), 9)  # 每笔交易平均盈亏
    results.loc[0, '盈亏收益比'] = round(pnl.loc[pnl['change'] > 0]['change'].mean() / \
                                    pnl.loc[pnl['change'] < 0][
                                        'change'].mean() * (-1), 2)  # 盈亏比

    results.loc[0, '单笔最大盈利'] = format(pnl['change'].max(), '.2%')  # 单笔最大盈利
    results.loc[0, '单笔最大亏损'] = format(pnl['change'].min(), '.2%')  # 单笔最大亏损

    # ===统计持仓时间
    pnl['持仓时间'] = pnl['hold_time_seconds']
    max_minutes = pnl['持仓时间'].max()
    results.loc[0, '单笔最长持有时间'] = str(int(max_minutes)) + ' seconds'  # 单笔最长持有时间

    min_minutes = pnl['持仓时间'].min()
    results.loc[0, '单笔最短持有时间'] = str(int(min_minutes)) + ' seconds'  # 单笔最短持有时间

    mean_minutes = pnl['持仓时间'].mean()
    results.loc[0, '平均持仓周期'] = str(round(mean_minutes, 1)) + ' seconds'  # 平均持仓周期

    # ===连续盈利亏算
    results.loc[0, '最大连续盈利笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(pnl['change'] > 0, 1, np.nan))])  # 最大连续盈利笔数
    results.loc[0, '最大连续亏损笔数'] = max(
        [len(list(v)) for k, v in itertools.groupby(np.where(pnl['change'] < 0, 1, np.nan))])  # 最大连续亏损笔数

    pnl['date'] = pnl['create_time'].apply(lambda x: x.date())
    daily_openvalue = pnl.groupby('date').agg({'open_fill_value': 'sum'})
    results.loc[0, '平均每日杠杆'] = round(daily_openvalue.mean()[0] / initial_cash, 2)

    results = results.T
    results.columns = ['num']
    return results, sharpedailyreturn


def get_order_submitted_num(o_list, date):
    order_submitted_num = 0
    _ = set()
    for x in o_list:
        _.add(x.action)
        if x.action == 'buy_open':
            order_submitted_num += x.quantity
        elif x.action == 'sell_open':
            order_submitted_num -= x.quantity
        elif x.action == 'buy_close':
            order_submitted_num -= x.quantity
        elif x.action == 'sell_close':
            order_submitted_num += x.quantity
    assert len(_) <= 1, str(date) + str(_)
    return order_submitted_num


def get_buy_dealpx(a, alist):
    for i in range(len(alist)):
        if a < alist[i]:
            return alist[i - 1]
    return alist[-1]

def get_sell_dealpx(a, alist):
    for i in range(len(alist)-1,0,-1):
        if a > alist[i]:
            return alist[i + 1]
    return alist[0]

# 用对价成交
def make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, deal_px_vol, nowtime, now_sig, vwappx):
    _fill_quantity_sum = 0
    _fill_idx = []
    
    deal_estimate = deal_px_vol.copy()
    plist = sorted(deal_estimate.keys())
    if len(plist) == 0:
        return order_submitted_list, order_finished_list, _fill_quantity_sum
    
    # 从买卖最优价格各去掉一张
#     _plist0 = plist[0]
#     deal_estimate[_plist0] -= 1
#     if deal_estimate[_plist0] == 0:
#         del(deal_estimate[_plist0])
#         plist = plist[1:]
#     if len(plist) > 0 and plist[-1] != _plist0:
#         deal_estimate[plist[-1]] -= 1
#         if deal_estimate[plist[-1]] == 0:
#             del(deal_estimate[plist[-1]])
#             plist = plist[:-1]
#     if len(plist) == 0:
#         return order_submitted_list, order_finished_list, _fill_quantity_sum
    
    # 价格优先 时间优先
    if order_submitted_list[0].action in ['buy_open', 'buy_close']:
        order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
    else:
        order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
        
    for k in range(len(order_submitted_list)):
        _order = order_submitted_list[k]
        if _order.action in ['buy_open', 'buy_close'] and _order.status == 'submit':
            if plist[0] <= _order.submit_price:
                _order.status = 'fill'
                deal_px = _order.submit_price #get_buy_dealpx(_order.submit_price, plist)
                _order.fill_price = deal_px 
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                order_finished_list.append(_order)
                _fill_quantity_sum += _order.quantity
                _fill_idx.append(k) 
                deal_px = plist[0]
                deal_estimate[deal_px] -= _order.quantity
                if deal_estimate[deal_px] == 0:
                    del(deal_estimate[deal_px])
                    plist = sorted(deal_estimate.keys())
                    if len(plist) == 0:
                        break
                
        elif _order.action in ['sell_open', 'sell_close'] and _order.status == 'submit':
            if plist[-1] >= _order.submit_price:
                _order.status = 'fill'
                deal_px = _order.submit_price # get_sell_dealpx(_order.submit_price, plist)
                _order.fill_price = deal_px 
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                order_finished_list.append(_order)
                _fill_quantity_sum -= _order.quantity
                _fill_idx.append(k)
                deal_px = plist[-1]
                deal_estimate[deal_px] -= _order.quantity
                if deal_estimate[deal_px] == 0:
                    del(deal_estimate[deal_px])
                    plist = sorted(deal_estimate.keys())
                    if len(plist) == 0:
                        break
                
         
    if len(_fill_idx) > 0:
        _fill_idx.reverse()
        for _idx in _fill_idx:
            del order_submitted_list[_idx]
    return order_submitted_list, order_finished_list, _fill_quantity_sum

# deal_price 成交
# def make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, deal_px_vol, nowtime, now_sig, vwappx):
#     _fill_quantity_sum = 0
#     _fill_idx = []
    
#     deal_estimate = deal_px_vol.copy()
#     plist = sorted(deal_estimate.keys())
#     if len(plist) == 0:
#         return order_submitted_list, order_finished_list, _fill_quantity_sum
    
#     # 从买卖最优价格各去掉一张
#     _plist0 = plist[0]
#     deal_estimate[_plist0] -= 1
#     if deal_estimate[_plist0] == 0:
#         del(deal_estimate[_plist0])
#         plist = plist[1:]
#     if len(plist) > 0 and plist[-1] != _plist0:
#         deal_estimate[plist[-1]] -= 1
#         if deal_estimate[plist[-1]] == 0:
#             del(deal_estimate[plist[-1]])
#             plist = plist[:-1]
#     if len(plist) == 0:
#         return order_submitted_list, order_finished_list, _fill_quantity_sum
    
#     # 价格优先 时间优先
#     if order_submitted_list[0].action in ['buy_open', 'buy_close']:
#         order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
#     else:
#         order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
        
#     for k in range(len(order_submitted_list)):
#         _order = order_submitted_list[k]
#         if _order.action in ['buy_open', 'buy_close'] and _order.status == 'submit':
#             if plist[0] <= _order.submit_price:
#                 _order.status = 'fill'
#                 deal_px = get_buy_dealpx(_order.submit_price, plist)
#                 _order.fill_price = deal_px 
#                 _order.finish_sig = now_sig
#                 _order.finish_time = nowtime
#                 _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
#                 order_finished_list.append(_order)
#                 _fill_quantity_sum += _order.quantity
#                 _fill_idx.append(k) 
#                 deal_estimate[deal_px] -= _order.quantity
#                 if deal_estimate[deal_px] == 0:
#                     del(deal_estimate[deal_px])
#                     plist = sorted(deal_estimate.keys())
#                     if len(plist) == 0:
#                         break
                
#         elif _order.action in ['sell_open', 'sell_close'] and _order.status == 'submit':
#             if plist[-1] >= _order.submit_price:
#                 _order.status = 'fill'
#                 deal_px = get_sell_dealpx(_order.submit_price, plist)
#                 _order.fill_price = deal_px 
#                 _order.finish_sig = now_sig
#                 _order.finish_time = nowtime
#                 _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
#                 order_finished_list.append(_order)
#                 _fill_quantity_sum -= _order.quantity
#                 _fill_idx.append(k)
#                 deal_estimate[deal_px] -= _order.quantity
#                 if deal_estimate[deal_px] == 0:
#                     del(deal_estimate[deal_px])
#                     plist = sorted(deal_estimate.keys())
#                     if len(plist) == 0:
#                         break
                
         
#     if len(_fill_idx) > 0:
#         _fill_idx.reverse()
#         for _idx in _fill_idx:
#             del order_submitted_list[_idx]
#     return order_submitted_list, order_finished_list, _fill_quantity_sum


def get_timediff_seconds(start_time, end_time):
    if start_time != start_time:
        return np.nan
    m = (end_time - start_time).total_seconds()
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90 * 60
    else:
        return m


class TS_BACK_TEST:

    def __init__(self, signal, in_t=0.9, in_submit_order_t = 0.8, in_cancel_order_t=0.5, out_submit_order_t=0, out_t=-0.3, max_pos = 1, order_num_pertick = 1, 
                 max_wait_tick_num_close_order = None, update_order_ticknum = None,  
                 initial_cash=2e8, ticker='IC.CFE', start_date=None, end_date=None, n_jobs=24,
                 c_rate=2.4 / 100000, tickslippage_dict={(0, 0.5): 10, (0.5, 0.7): 1.2, (0.7, 0.9): 0.8, (0.9, 100): 0.2},
                 trade_start_time=[9, 30], trade_end_time=[14, 56],
                 save_results = True, save_path='/data/user/', name_prefix=''):

        if start_date is not None:
            self.start_date = start_date
            self.end_date = end_date
            self.signal = signal.loc[str(self.start_date):str(self.end_date)]
        else:
            self.start_date = signal.index.tolist()[0].strftime('%Y%m%d')
            self.end_date = signal.index.tolist()[-1].strftime('%Y%m%d')
            self.signal = signal

        self.signal.index.name = 'dt'
        if isinstance(self.signal, pd.Series):
            self.signal = self.signal.to_frame()
        self.signal.columns = ['raw']
        self.signal = self.signal.fillna(0)

        self.in_t = in_t
        self.in_submit_order_t = in_submit_order_t
        self.out_submit_order_t = out_submit_order_t
        self.in_cancel_order_t = in_cancel_order_t
        self.out_t = out_t
        self.max_pos = max_pos
        self.order_num_pertick = order_num_pertick
        self.max_wait_tick_num_close_order = max_wait_tick_num_close_order
        self.update_order_ticknum = update_order_ticknum
        self.initial_cash = initial_cash
        self.ticker = ticker
        face_value_dict = {'IC.CFE': 200,
                           'IM.CFE': 200,
                           'IF.CFE': 300,
                           'IH.CFE': 300}
        self.face_value = face_value_dict[self.ticker]

        self.trade_start_time = datetime.time(trade_start_time[0], trade_start_time[1])
        self.trade_end_time = datetime.time(trade_end_time[0], trade_end_time[1])

        self.c_rate = c_rate

        self.save_results = save_results
        self.save_path = save_path
        self.name_prefix = name_prefix

        self.tickslippage_dict = tickslippage_dict
        self.n_jobs = n_jobs

        univ = IO.read_data([self.start_date, self.end_date], columns=['contract_00'],
                            alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
        self.univ = univ.xs(self.ticker, level=1)
        self.daily_opendata = IO.read_data([self.start_date, self.end_date], columns=['open'],
                                           alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')

    def get_tickslippage(self, now_sig, now_hold_num):
#         if np.sign(now_sig) * np.sign(now_hold_num) == -1:
#             return 10
        for k, v in self.tickslippage_dict.items():
            if (abs(now_sig) >= k[0]) and (abs(now_sig) < k[1]):
                return v

    def get_trade_num(self, _order_submitted_list, now_sig, pre_hold_num, put_order_status, nowtime, date):
        # 当前挂单数量
        order_submitted_num = get_order_submitted_num(_order_submitted_list, date)

        if nowtime.time() < self.trade_start_time:
            need_trade_num = 0
            return need_trade_num, put_order_status
        elif nowtime.time() >= self.trade_end_time:
            put_order_status = 'close_pos'
            need_trade_num = (pre_hold_num - order_submitted_num) * -1
#             print('&&&&&', nowtime, pre_hold_num, order_submitted_num, need_trade_num)
            return need_trade_num, put_order_status
            
        # 当目前不在开仓状态时
        if put_order_status == 'no_pos': 
            if pre_hold_num == 0:
                if now_sig > self.in_t:
                    put_order_status = 'buy_open_pos'
                    need_trade_num = self.max_pos - order_submitted_num
                elif now_sig < -1 * self.in_t:
                    put_order_status = 'sell_open_pos'
                    need_trade_num = self.max_pos * -1 - order_submitted_num
                else:
                    need_trade_num = 0
            elif pre_hold_num > 0:
                if now_sig > self.in_t:
                    put_order_status = 'buy_open_pos'
                    need_trade_num = self.max_pos - pre_hold_num - order_submitted_num
                elif now_sig < self.out_t:
                    put_order_status = 'sell_close_pos'
                    need_trade_num = pre_hold_num * -1
                else:
                    need_trade_num = 0
            elif pre_hold_num < 0:
                if now_sig < self.in_t * -1:
                    put_order_status = 'sell_open_pos'
                    need_trade_num = -1 * self.max_pos - pre_hold_num - order_submitted_num
                elif now_sig > self.out_t * -1:
                    put_order_status = 'buy_close_pos'
                    need_trade_num = pre_hold_num * -1
                else:
                    need_trade_num = 0
            return need_trade_num, put_order_status
        
        # 当目前多仓
        if put_order_status == 'buy_open_pos':
            if now_sig > self.in_submit_order_t:
                need_trade_num = self.max_pos - pre_hold_num - order_submitted_num
                return need_trade_num, put_order_status
            else:
                put_order_status = 'no_pos'
                if now_sig < self.in_t * -1 and pre_hold_num == 0:
                    assert order_submitted_num == 0
                    need_trade_num = self.max_pos * -1
                    put_order_status = 'sell_open_pos'
                    return need_trade_num, put_order_status
                elif now_sig < self.out_t:
                    put_order_status = 'sell_close_pos'
                    need_trade_num = pre_hold_num * -1
                    return need_trade_num, put_order_status
        
        # 当目前空仓
        if put_order_status == 'sell_open_pos':
            if now_sig < self.in_submit_order_t * -1:
                need_trade_num = -1 * self.max_pos - pre_hold_num - order_submitted_num
                return need_trade_num, put_order_status
            else:
                put_order_status = 'no_pos'
                if now_sig > self.in_t and pre_hold_num == 0:
                    assert order_submitted_num == 0
                    need_trade_num = self.max_pos
                    put_order_status = 'buy_open_pos'
                    return need_trade_num, put_order_status
                elif now_sig > self.out_t * -1:
                    put_order_status = 'buy_close_pos'
                    need_trade_num = pre_hold_num * -1
                    return need_trade_num, put_order_status
        
        # 当前属于平多仓状态
        if put_order_status == 'sell_close_pos':
            if np.sign(pre_hold_num + order_submitted_num) * np.sign(now_sig) >= 0:
                if now_sig > self.in_t:
                    need_trade_num = self.max_pos - pre_hold_num - order_submitted_num
                    put_order_status = 'buy_open_pos'
                    return need_trade_num, put_order_status 
                elif now_sig < -1 * self.in_t:
                    need_trade_num = -1 * self.max_pos - pre_hold_num - order_submitted_num
                    put_order_status = 'sell_open_pos'
                    return need_trade_num, put_order_status
                
            if now_sig > self.in_t:
                need_trade_num = self.max_pos - pre_hold_num - order_submitted_num
                put_order_status = 'buy_open_pos'
                return need_trade_num, put_order_status
            elif now_sig > self.out_submit_order_t:
                put_order_status = 'no_pos'
                need_trade_num = 0
                return need_trade_num, put_order_status
            elif now_sig < self.out_submit_order_t:
                need_trade_num = (pre_hold_num - order_submitted_num) * -1
                return need_trade_num, put_order_status
            
        # 当前属于平空仓状态
        if put_order_status == 'buy_close_pos':
            if np.sign(pre_hold_num + order_submitted_num) * np.sign(now_sig) >= 0:
                if now_sig > self.in_t:
                    need_trade_num = self.max_pos - pre_hold_num - order_submitted_num
                    put_order_status = 'buy_open_pos'
                    return need_trade_num, put_order_status 
                elif now_sig < -1 * self.in_t:
                    need_trade_num = -1 * self.max_pos - pre_hold_num - order_submitted_num
                    put_order_status = 'sell_open_pos'
                    return need_trade_num, put_order_status
                
            if now_sig < -1 * self.in_t:
                need_trade_num = -1 * self.max_pos - pre_hold_num - order_submitted_num
                put_order_status = 'sell_open_pos'
                return need_trade_num, put_order_status
            elif now_sig < -1 * self.out_submit_order_t:
                put_order_status = 'no_pos'
                need_trade_num = 0
                return need_trade_num, put_order_status
            elif now_sig > -1 * self.out_submit_order_t:
                need_trade_num = (pre_hold_num - order_submitted_num) * -1
                return need_trade_num, put_order_status
        
        need_trade_num = 0
        return need_trade_num, put_order_status

    def cancel_order(self, order_submitted_list, order_finished_list, now_sig, now_hold_num, put_order_status, nowtime):
#         print('*' * 10, now_sig, put_order_status)
        cancel_action_set = set()
        if nowtime.time() < self.trade_start_time:
            return order_submitted_list, order_finished_list
        
        if nowtime.time() >= self.trade_end_time:
            cancel_action_set.update(['buy_open', 'sell_open'])
        else:
            if now_sig > self.in_t:
                cancel_action_set.update(['sell_open', 'sell_close'])
            elif now_sig < -1 * self.in_t:
                cancel_action_set.update(['buy_open', 'buy_close'])
            if now_sig < self.in_cancel_order_t:
                cancel_action_set.add('buy_open')
            if now_sig > -1 * self.in_cancel_order_t:
                cancel_action_set.add('sell_open')
            if now_sig > self.out_submit_order_t:
                cancel_action_set.add('sell_close')
            if now_sig < self.out_submit_order_t * -1:
                cancel_action_set.add('buy_close')
 
        cancel_action_list = list(cancel_action_set)
#         print(nowtime, now_sig, cancel_action_list)

        if len(cancel_action_list) > 0 and len(order_submitted_list) > 0:
            _cancel_idx = []
            for k in range(len(order_submitted_list)):
                _order = order_submitted_list[k]
                if _order.action in cancel_action_list:
                    _order.status = 'cancel'
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
            _cancel_idx.reverse()
            for _idx in _cancel_idx:
#                 print('normal cancel:', order_submitted_list[_idx].__dict__)
                del order_submitted_list[_idx]
        
        # 按照平仓单持续时间撤单
        if (self.max_wait_tick_num_close_order is not None) and (len(order_submitted_list) > 0):
            if order_submitted_list[0].action in ['buy_open', 'buy_close']:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
            else:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
            cancel_num = 0
            _cancel_idx = []
            for k in range(len(order_submitted_list)):
                if cancel_num >= self.order_num_pertick:
                    break
                _order = order_submitted_list[k]
                if (_order.action in ['buy_close', 'sell_close']) and (_order.hold_closetick_num >= self.max_wait_tick_num_close_order):
                    _order.status = 'cancel'
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
                    cancel_num += 1
            _cancel_idx.reverse()
            for _idx in _cancel_idx:
#                 print('close ticknum cancel:', order_submitted_list[_idx].__dict__)
                del order_submitted_list[_idx]
    
        # 更新订单价格
        cancel_by_update_order_ticknum = False
        if self.update_order_ticknum is not None and len(order_submitted_list) > 0:
            # 当前挂单数量
            order_submitted_num = get_order_submitted_num(order_submitted_list, 'fake date')
            _action = order_submitted_list[0].action
            if _action == 'buy_open':
                if now_sig > self.in_submit_order_t and self.max_pos == (now_hold_num + order_submitted_num):
                    cancel_by_update_order_ticknum = True
            elif _action == 'sell_open':
                if now_sig < self.in_submit_order_t * -1 and self.max_pos * -1 == (now_hold_num + order_submitted_num):
                    cancel_by_update_order_ticknum = True
            elif _action == 'buy_close':
                if now_sig > self.out_submit_order_t * -1 and now_hold_num == order_submitted_num:
                    cancel_by_update_order_ticknum = True
            elif _action == 'sell_close':
                if now_sig < self.out_submit_order_t and now_hold_num == order_submitted_num:
                    cancel_by_update_order_ticknum = True
        if cancel_by_update_order_ticknum:
#             print(nowtime, 'chedan ')
            # 价格优先 时间优先
            if order_submitted_list[0].action in ['buy_open', 'buy_close']:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
            else:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
            cancel_num = 0
            _cancel_idx = []
            for k in range(len(order_submitted_list)):
                if cancel_num >= self.order_num_pertick:
                    break
                _order = order_submitted_list[k]
                if _order.hold_tick_num >= self.update_order_ticknum:
                    _order.status = 'cancel'
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
                    cancel_num += 1
            _cancel_idx.reverse()

            for _idx in _cancel_idx:
#                     print(now_hold_num, nowtime, order_submitted_list[_idx].__dict__)
                del order_submitted_list[_idx]

        return order_submitted_list, order_finished_list

    def trade_helper(self, finishdf):
        bs_dict = {'buy': 1, 'sell': -1}
        finishdf['action_bs'] = finishdf['action'].apply(lambda x: bs_dict[x.split('_')[0]])
        finishdf['action_oc'] = finishdf['action'].apply(lambda x: x.split('_')[1])

        total_order_counts = len(finishdf)
        canceldf = finishdf[finishdf['status'] == 'cancel']
        cancel_order_counts = len(canceldf)
        filldf = finishdf[finishdf['status'] == 'fill']

        filldf['quantity_bs'] = filldf['quantity'] * filldf['action_bs']
        filldf['now_hold_num'] = filldf.quantity_bs.cumsum()
       
        filldf.loc[filldf['now_hold_num'] == 0, 'deal_count'] = 1
        filldf['deal_count'] = filldf['deal_count'].cumsum().fillna(method='bfill')

        filldf['fill_value'] = filldf.fill_price * filldf.quantity * self.face_value
        filldf['fee'] = filldf['fill_value'] * self.c_rate

        pen_price_df = filldf.groupby(['deal_count', 'action_oc']).agg(
            {'fill_value': 'sum', 'quantity': 'sum', 'fee': 'sum'})
        pen_price_df['weighted_price'] = pen_price_df['fill_value'] / pen_price_df['quantity'] / self.face_value

        pendf = filldf.groupby('deal_count').agg(
            {'quantity_bs': 'first', 'now_hold_num': lambda x: max(abs(x)), 'create_time': 'first',
             'finish_time': 'last'})
        pendf['now_hold_num'] = pendf['now_hold_num'] * pendf['quantity_bs']

        rlist = [pendf]
        for x in ['open', 'close']:
            rlist.append(pen_price_df[['fill_value', 'fee', 'weighted_price']].xs(x, level=1).add_prefix('%s_' % x))

        rdf = pd.concat(rlist, axis=1)

        rdf['profit_intradeal'] = (rdf['close_fill_value'] - rdf['open_fill_value'])*rdf['quantity_bs'] - rdf['open_fee'] - rdf['close_fee']
        rdf['change'] = rdf['profit_intradeal'] / self.initial_cash
        rdf['equity_curve'] = rdf['change'].cumsum() + 1
        rdf['hold_time_seconds'] = rdf.apply(lambda x: get_timediff_seconds(x.create_time, x.finish_time), axis=1)
        rdf['hold_time_minutes'] = rdf['hold_time_seconds'] / 60
        
        rdf = rdf.rename(columns={'quantity_bs': 'pos', 'now_hold_num': 'pos_num'})
        return rdf, total_order_counts, cancel_order_counts

    def back_test_singleday(self, date):
        signal_date = self.signal.loc[str(date)]
        temp_contract = self.univ.loc[str(date)]['contract_00']
        contract = temp_contract.split('.')[0]
        open_price_930 = self.daily_opendata.loc[(str(date), temp_contract)]['open']  # calculate position
#         max_pos = self.max_pos # np.floor(self.initial_cash / self.cash_divnum / (open_price_930 * self.face_value))
        tickdf = pd.read_csv('/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/RECENT_MONTH_with_deal_estimate/%s/%s.csv' % (self.ticker.replace('.', '_'), date), index_col=0, parse_dates=True)
        signal_date = signal_date.join(tickdf)
        signal_date.loc[signal_date.HighPx != signal_date.HighPx.shift(1), 'HighPx_change'] = signal_date['HighPx']
        signal_date.loc[signal_date.LowPx != signal_date.LowPx.shift(1), 'LowPx_change'] = signal_date['LowPx']
        signal_date['volume'] = signal_date.TotalVolumeTrade.diff()
        signal_date['amount'] = signal_date.TotalValueTrade.diff()
        signal_date['vwap'] = signal_date['amount'] / signal_date['volume'] /self.face_value
        signal_date = signal_date.replace([np.inf, -np.inf], np.nan)
        _temp = signal_date[['raw','deal_px_vol','vwap']]
        delete_columns = ['TradingDate', 'PreOpenInterest', 'PreClosePx', 'PreSettlePrice', 'OpenPx', 'HighPx', 'LowPx', 'TotalVolumeTrade', 
                          'TotalValueTrade', 'OpenInterest', 'ClosePx', 'SettlePrice', 'PreDelta', 'CurrDelta', 'ReceiveDateTime']
        signal_date = signal_date.drop(delete_columns, axis = 1).reset_index()
        col_list = signal_date.columns.tolist()
        signal_date = signal_date.values
        
        dt_idx = col_list.index('dt')
        raw_idx = col_list.index('raw')
        Buy1Price_idx = col_list.index('Buy1Price')
        Sell1Price_idx = col_list.index('Sell1Price')
        LastPx_idx = col_list.index('LastPx')
        deal_px_vol_idx = col_list.index('deal_px_vol')
        vwap_idx = col_list.index('vwap')

        now_hold_num = 0

        date_signal_lenth = len(signal_date)
        order_submitted_list = []  # 当前提交的订单
        order_finished_list = []  # 提交的订单结束，成交或被撤销
        target_pos = 0  # 此bar的目标仓位
        put_order_status = 'no_pos'  # 初始化订单操作的action

        for i in range(1, date_signal_lenth):
            assert len(order_submitted_list) <= self.max_pos, (date, i)
            now_tick = signal_date[i]
            now_sig = round(now_tick[raw_idx], 6)
            nowtime = now_tick[dt_idx]
            buy1px = now_tick[Buy1Price_idx]
            sell1px = now_tick[Sell1Price_idx]
            lastpx = now_tick[LastPx_idx]
            vwappx = now_tick[vwap_idx]
            deal_px_vol = eval(now_tick[deal_px_vol_idx])
            
            if len(order_submitted_list) > 0:
                # 判断成交
                order_submitted_list, order_finished_list, _fill_quantity_sum = make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, deal_px_vol, nowtime, now_sig, vwappx)
                now_hold_num += _fill_quantity_sum
        
                # 撤单
                order_submitted_list, order_finished_list = self.cancel_order(order_submitted_list, order_finished_list, now_sig, now_hold_num, put_order_status, nowtime)
                
                # 当有挂单时，更新挂单持仓ticks
                for _order in order_submitted_list:
                    _order.hold_tick_num += 1
                    if _order.action == 'buy_close' and (now_sig > self.out_submit_order_t * -1 or nowtime.time() >= self.trade_end_time):
                        _order.hold_closetick_num += 1
                    elif _order.action == 'sell_close' and (now_sig < self.out_submit_order_t or nowtime.time() >= self.trade_end_time):
                        _order.hold_closetick_num += 1

            need_trade_num, put_order_status = self.get_trade_num(order_submitted_list, now_sig,
                                                                                      now_hold_num,
                                                                                      put_order_status, nowtime, date)
#             print('*' * 10, i, now_sig, need_trade_num, now_hold_num, put_order_status, nowtime, '*' * 10)
#             for xx in order_submitted_list:
#                 print(xx.__dict__)

            tickslippage = self.get_tickslippage(now_sig, now_hold_num)

            if need_trade_num != 0:
                open_contract_num = min(abs(need_trade_num), self.order_num_pertick)
                need_trade_num_state = np.sign(need_trade_num)
                # the price of the order
                if need_trade_num > 0:
                    open_price = sell1px #(buy1px + sell1px) / 2 # buy1px + tickslippage
                else:
                    open_price = buy1px #(buy1px + sell1px) / 2 # sell1px - tickslippage
                tickdt_time = nowtime
                tick_pxlist = [buy1px, sell1px, lastpx]

                if put_order_status in ['buy_open_pos', 'sell_open_pos']:  # 当需要挂单开仓时
                    _order = Order(symbol=contract, action=None, submit_price=open_price, quantity=1, status='submit',
                                   create_sig = now_sig, create_time=nowtime,  create_tick_pxlist=tick_pxlist)
                    if need_trade_num_state == 1:
                        _order.action = 'buy_open'
                        need_trade_num -= open_contract_num
                    else:
                        _order.action = 'sell_open'
                        need_trade_num += open_contract_num
                    _order.hold_tick_num += 1
                    order_submitted_list += [copy.deepcopy(_order) for i in range(open_contract_num)]
             
                elif put_order_status in ['buy_close_pos', 'sell_close_pos','close_pos']:
                    _order = Order(symbol=contract, action=None, submit_price=open_price, quantity=1, status='submit',
                                   create_sig = now_sig, create_time=nowtime, create_tick_pxlist=tick_pxlist)
                    if need_trade_num_state == 1:
                        _order.action = 'buy_close'
                        need_trade_num -= open_contract_num
                    else:
                        _order.action = 'sell_close'
                        need_trade_num += open_contract_num
                    _order.hold_tick_num += 1
                    _order.hold_closetick_num += 1
                    order_submitted_list += [copy.deepcopy(_order) for i in range(open_contract_num)]
                    
#             print('#######')
#             for xx in order_submitted_list:
#                 print(xx.__dict__)
                    
        assert len(order_submitted_list) == 0, date
        col_list = ['symbol', 'action', 'submit_price', 'fill_price', 'quantity', 'status', 'create_time',
                    'create_sig', 'finish_time','finish_sig', 'create_tick_pxlist', 'finish_tick_pxlist', 'hold_tick_num', 'hold_closetick_num']
        finishdf = [
            [x.symbol, x.action, x.submit_price, x.fill_price, x.quantity, x.status, x.create_time, x.create_sig,
             x.finish_time, x.finish_sig, x.create_tick_pxlist, x.finish_tick_pxlist, x.hold_tick_num, x.hold_closetick_num] for x in order_finished_list]
        finishdf = pd.DataFrame(finishdf, columns=col_list)
        
        finishdf['dt'] = finishdf['create_time']
        finishdf = finishdf.set_index('dt')
        finishdf = _temp.join(finishdf, how = 'left').reset_index()
        return finishdf

    def back_test(self):
        date_list = [int(x.strftime('%Y%m%d')) for x in set(self.signal.index.date)]
        date_list.sort()
        with Pool(self.n_jobs) as pool:
            rlist = pool.map(self.back_test_singleday, date_list)

        trade_df = pd.concat(rlist, axis=0).sort_values(by='dt')
        _trade_df = trade_df.dropna(subset = ['symbol']).sort_values(by = 'create_time')

        totaltrade_df, total_order_counts, cancel_order_counts = self.trade_helper(_trade_df)

        results, daily_return = strategy_evaluate(totaltrade_df.copy(), self.initial_cash, total_order_counts, cancel_order_counts)
        daily_return.columns = ['daily_return','daily_equty_curve']
        
        if self.save_results:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_total_trade_detail.csv'))
            _trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_order_detail.csv'))
            daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + '_results.csv'), encoding='gbk')
            totaltrade_df.set_index('create_time').change.cumsum().plot(figsize=(20, 10))
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + '_profit.png'))
            plt.close()

        return {'total_trade_detail':totaltrade_df, 'results':results, 'order_detail':trade_df, 'daily_return':daily_return}

'''
sig = pd.read_pickle('/data/group/800466/tmp/lstm_tick/lstm_20tk_20ticks_oos.pkl')#.loc['20200403'].iloc[26000:]
# sig = pd.read_pickle('/data/user/015626/data/share/LOCAL_DATA/tick_signal_test.pkl')#.loc['20200403'].iloc[27175:]
start_date = 20210101
end_date = 20211231
in_t = 0.15
in_submit_order_t = 0.15
in_cancel_order_t = 0.05
out_t = -0.1
out_submit_order_t = -0.1
max_pos  = 1
order_num_pertick = 1
max_wait_tick_num_close_order = 4
update_order_ticknum = 1
result_date = 20220803
name = 'cf_oos_%s_%s_%s_%s_%s_%s_%s_%s_%s_submitpx_updatepx' % (in_t,in_submit_order_t, in_cancel_order_t,out_submit_order_t, out_t, max_pos, order_num_pertick, max_wait_tick_num_close_order, update_order_ticknum)
ts = TS_BACK_TEST(sig, in_t=in_t,in_submit_order_t=in_submit_order_t, in_cancel_order_t=in_cancel_order_t,out_submit_order_t=out_submit_order_t, out_t=out_t, max_pos = max_pos,order_num_pertick=order_num_pertick,
                  max_wait_tick_num_close_order = max_wait_tick_num_close_order, update_order_ticknum = update_order_ticknum,
                  initial_cash=1e7, 
                  c_rate=2.4 / 100000, ticker='IC.CFE',
                  start_date=start_date, end_date=end_date,
                  trade_start_time=[9, 35], trade_end_time=[14, 55],
                  save_results = True,
                  save_path='/data/user/015626/data/share/factor/back_test/Tick/IC/%s/%s_%s_%s' % (result_date, name, start_date, end_date),
                  name_prefix='test_%s' % name)
# finishdf = ts.back_test_singleday(20210107)
result = ts.back_test()
'''