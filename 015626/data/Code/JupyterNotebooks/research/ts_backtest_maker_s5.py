# -*- coding:UTF-8 -*-
# 增加做空
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
                 create_tick_pxlist=[], finish_tick_pxlist=[], hold_tick_num = 0, finish_tick_deal_estimate = None, 
                 hold_closetick_num = 0, submit_px_inob = 0, order_type = 'limit'):
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
        self.finish_quantity = 0 # 当前已经完成的数量
        self.remain_quantity = quantity # 剩余完成数量
        self.create_tick_pxlist = create_tick_pxlist  # 基于哪个tick挂的单，此tick的[buy1price, sell1price, lastpx]
        self.finish_tick_pxlist = finish_tick_pxlist  # 基于哪个tick成交的，此tick的[buy1price, sell1price, lastpx]
        self.hold_tick_num = hold_tick_num # 持续了多少根tick
        self.finish_tick_deal_estimate = finish_tick_deal_estimate # 平仓那根tick的成交估计
        self.hold_closetick_num = hold_closetick_num # 平仓单持续了多少根低于出场阈值的tick，平仓单撤单重发时用
        self.submit_px_inob = submit_px_inob # 发单时依照第几档盘口
        self.order_type = order_type # 委托单类型 限价单还是市价单
        
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
            order_submitted_num += x.remain_quantity
        elif x.action == 'sell_open':
            order_submitted_num -= x.remain_quantity
        elif x.action == 'buy_close':
            order_submitted_num -= x.remain_quantity
        elif x.action == 'sell_close':
            order_submitted_num += x.remain_quantity
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

# 用发单价成交
def make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, deal_px_vol, nowtime, now_sig, vwappx):
    if deal_px_vol != deal_px_vol:
        return order_submitted_list, order_finished_list, _fill_quantity_sum

    _fill_quantity_sum = 0
    _fill_idx = []
    
    trade_info = deal_px_vol.copy()
    plist = sorted(trade_info.keys())
    if len(plist) == 0:
        return order_submitted_list, order_finished_list, _fill_quantity_sum
    
    # 价格优先 时间优先
    if order_submitted_list[0].action in ['buy_open', 'buy_close']:
        order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
    else:
        order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
        
    for k in range(len(order_submitted_list)):
        _order = order_submitted_list[k]
        if _order.order_type == 'market':
            fill_money = 0
            for pr,v in trade_info.items():
                deal_quantity = min(_order.remain_quantity, v)
                deal_quantity = round(deal_quantity, 5)
                deal_px = pr #get_buy_dealpx(_order.submit_price, plist)
                fill_money += deal_quantity * deal_px
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                _order.finish_quantity += deal_quantity
                _order.remain_quantity -= deal_quantity
                if _order.action in ['buy_open', 'buy_close']:
                    _fill_quantity_sum += deal_quantity
                elif _order.action in ['sell_open', 'sell_close']:
                    _fill_quantity_sum -= deal_quantity
                if round(_order.remain_quantity, 5) == 0:
                    _order.status = 'fill'
                    _order.fill_price = round(fill_money / _order.finish_quantity, 2)
                    order_finished_list.append(_order)
                    _fill_idx.append(k) 
                    break
            if round(_order.remain_quantity, 5) != 0:
                deal_quantity = _order.remain_quantity
                deal_quantity = round(deal_quantity, 5)
                deal_px = sell1px if _order.action in ['buy_open', 'buy_close'] else buy1px
                fill_money += deal_quantity * deal_px
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                _order.finish_quantity += deal_quantity
                _order.remain_quantity -= deal_quantity
                if _order.action in ['buy_open', 'buy_close']:
                    _fill_quantity_sum += deal_quantity
                elif _order.action in ['sell_open', 'sell_close']:
                    _fill_quantity_sum -= deal_quantity
                _order.status = 'fill'
                _order.fill_price = round(fill_money / _order.finish_quantity, 2)
                order_finished_list.append(_order)
                _fill_idx.append(k)

        elif _order.action in ['buy_open', 'buy_close'] and _order.status in ['submit', 'partial_fill']:
            for p in plist:
                if p > _order.submit_price:
                    break
                if trade_info[p] == 0:
                    continue
                deal_quantity = min(_order.remain_quantity, trade_info[p])
                deal_quantity = round(deal_quantity, 5)
                deal_px = _order.submit_price #get_buy_dealpx(_order.submit_price, plist)
                _order.fill_price = deal_px 
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                _order.finish_quantity += deal_quantity
                _order.remain_quantity -= deal_quantity
                # order_finished_list.append(_order)
                _fill_quantity_sum += deal_quantity
                # _fill_idx.append(k) 
                trade_info[p] -= deal_quantity
                if round(_order.remain_quantity, 5) == 0:
                    _order.status = 'fill'
                    order_finished_list.append(_order)
                    _fill_idx.append(k) 
                    break
                else:
                    _order.status = 'partial_fill'
                
        elif _order.action in ['sell_open', 'sell_close'] and _order.status in ['submit', 'partial_fill']:
            for i in range(len(plist)-1, -1, -1):
                p = plist[i]
                if p < _order.submit_price:
                    break
                if trade_info[p] == 0:
                    continue
                deal_quantity = min(_order.remain_quantity, trade_info[p])
                deal_quantity = round(deal_quantity, 5)
                deal_px = _order.submit_price #get_buy_dealpx(_order.submit_price, plist)
                _order.fill_price = deal_px 
                _order.finish_sig = now_sig
                _order.finish_time = nowtime
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                _order.finish_quantity += deal_quantity
                _order.remain_quantity -= deal_quantity
                # order_finished_list.append(_order)
                _fill_quantity_sum -= deal_quantity
                # _fill_idx.append(k) 
                trade_info[p] -= deal_quantity
                if round(_order.remain_quantity, 5) == 0:
                    _order.status = 'fill'
                    order_finished_list.append(_order)
                    _fill_idx.append(k) 
                    break
                else:
                    _order.status = 'partial_fill'
         
    if len(_fill_idx) > 0:
        _fill_idx.reverse()
        for _idx in _fill_idx:
            del order_submitted_list[_idx]
    return order_submitted_list, order_finished_list, _fill_quantity_sum

def get_timediff_seconds(start_time, end_time):
    if start_time != start_time:
        return np.nan
    return (end_time - start_time).total_seconds()

def get_buy_px(list_numbers, target_sum):
    i = 0
    cumulative_sum = 0
    for b in list_numbers:
        i += 1
        cumulative_sum += b[1]
        if cumulative_sum >= target_sum:
            return b[0] + 0.01, i
    return list_numbers[-1][0] - 0.01, 21

def get_sell_px(list_numbers, target_sum):
    i = 0
    cumulative_sum = 0
    for b in list_numbers:
        i += 1
        cumulative_sum += b[1]
        if cumulative_sum >= target_sum:
            return b[0] - 0.01, i
    return list_numbers[-1][0] + 0.01, 21


class TS_BACK_TEST:

    def __init__(self, signal, in_t=0.9, in_submit_order_t = 0.8, in_cancel_order_t=0.5, out_submit_order_t=0, out_t=-0.3, 
                 max_pos = 0.001, order_num_pertick = 0.001, 
                 max_wait_tick_num_close_order = None, update_order_ticknum = None,  
                 initial_cash=2e8, ticker='IC.CFE', start_date=None, end_date=None, n_jobs=24,
                 c_rate=2.4 / 100000, tickslippage_dict={(0, 0.5): 10, (0.5, 0.7): 1.2, (0.7, 0.9): 0.8, (0.9, 100): 0.2},
                 save_results = True, save_path='/data/user/', name_prefix='', origin_tick = None, trade_deal_ratio = 1,
                 buy_px_idx = 0, sell_px_idx = 0, close_pos_quickly = False, save_detail = False, order_price_N = 4,
                 close_use_market_order = False):
        """
        :param signal: 信号
        :param in_t=0.9, in_submit_order_t = 0.8, in_cancel_order_t=0.5:为进场发单阈值，当信号大于0.9时候开始发单，信号不掉落至0.8就可继续发单，当信号小于0.5时就撤单
        :param out_submit_order_t=0, out_t=-0.3: 当信号小于-0.3时开始发单平仓，信号不大于0时可以继续委托。
        :param max_pos = 0.001, order_num_pertick = 0.001:每次开仓的目标仓位是max_pos,但是单次发单委托量上限是order_num_pertick
        :param max_wait_tick_num_close_order: 平仓单持续几根bar进行撤单
        :param update_order_ticknum: 委托单多少根bar更新一次价格
        :param initial_cash： 初始资金
        :param c_rate: 手续费
        :param tickslippage_dict: 不同信号对应不同slippage
        :param origin_tick: 原始tick数据，用来撮合
        :param trade_deal_ratio: 用来撮合的transaction数据的撮合比例
        :param buy_px_idx = 0, sell_px_idx = 0: 开仓时委托单发单价格
        :param close_pos_quickly: 开仓后是否立马平仓，为true表示马上发平仓单，为false表示按照信号平仓
        :param order_price_N: 当使用预测成交量挂单时，制定出来的价格距离本方一档小于2*order_price_N的话，本次不发单
        :param close_use_market_order: 当为true时，如果有平仓单，当前后两根bar的盘口价格波动大于30时，转为市价单平仓
        """

        if start_date is not None:
            self.start_date = start_date
            self.end_date = end_date
            self.signal = signal.loc[str(self.start_date):str(self.end_date)]
        else:
            self.start_date = signal.index.tolist()[0].strftime('%Y%m%d')
            self.end_date = signal.index.tolist()[-1].strftime('%Y%m%d')
            self.signal = signal

        self.origin_tick = origin_tick
        self.trade_deal_ratio = trade_deal_ratio

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
        self.cash = initial_cash
        self.ticker = ticker
        # face_value_dict = {'IC.CFE': 200,
        #                    'IM.CFE': 200,
        #                    'IF.CFE': 300,
        #                    'IH.CFE': 300}
        self.face_value = 1# face_value_dict[self.ticker]

        self.c_rate = c_rate

        self.save_results = save_results
        self.save_path = save_path
        self.name_prefix = name_prefix

        self.tickslippage_dict = tickslippage_dict
        self.n_jobs = n_jobs

        self.buy_px_idx = buy_px_idx
        self.sell_px_idx = sell_px_idx

        self.close_pos_quickly = close_pos_quickly
        self.save_detail = save_detail
        self.order_price_N = order_price_N
        self.close_use_market_order = close_use_market_order

        self.now_open_price = None
        self.now_open_time = None
        # self.cancel_close = False

    def get_tickslippage(self, now_sig, now_hold_num):
        # if np.sign(now_sig) * np.sign(now_hold_num) == -1:
        #     return 10
        for k, v in self.tickslippage_dict.items():
            if (abs(now_sig) >= k[0]) and (abs(now_sig) < k[1]):
                return v

    def get_trade_num(self, _order_submitted_list, now_sig, pre_hold_num, put_order_status, nowtime, date):
        # 当前挂单数量
        order_submitted_num = get_order_submitted_num(_order_submitted_list, date)
 
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
            # elif now_sig > self.out_submit_order_t:
            #     put_order_status = 'no_pos'
            #     need_trade_num = 0
            #     return need_trade_num, put_order_status
            # elif now_sig < self.out_submit_order_t:
            #     need_trade_num = (pre_hold_num - order_submitted_num) * -1
            #     return need_trade_num, put_order_status
            else:
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
            # elif now_sig < -1 * self.out_submit_order_t:
            #     put_order_status = 'no_pos'
            #     need_trade_num = 0
            #     return need_trade_num, put_order_status
            # elif now_sig > -1 * self.out_submit_order_t:
            #     need_trade_num = (pre_hold_num - order_submitted_num) * -1
            #     return need_trade_num, put_order_status
            else:
                need_trade_num = (pre_hold_num - order_submitted_num) * -1
                return need_trade_num, put_order_status
        
        need_trade_num = 0
        return need_trade_num, put_order_status

    def cancel_order(self, order_submitted_list, order_finished_list, now_sig, now_hold_num, put_order_status, nowtime):
        # print('*' * 10, now_sig, put_order_status)
        cancel_action_set = set()

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
        # print(nowtime, now_sig, cancel_action_list)

        if len(cancel_action_list) > 0 and len(order_submitted_list) > 0:
            _cancel_idx = []
            for k in range(len(order_submitted_list)):
                _order = order_submitted_list[k]
                if _order.action in cancel_action_list:
                    if _order.status == 'partial_fill':
                        _order.status = 'partial_cancel'
                    else:
                        _order.status = 'cancel'
                    # if _order.action in ['sell_close']:
                    #     self.cancel_close = True
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
            _cancel_idx.reverse()
            for _idx in _cancel_idx:
                # print('normal cancel:', order_submitted_list[_idx].__dict__)
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
                # if cancel_num >= self.order_num_pertick:
                #     break
                _order = order_submitted_list[k]
                if (_order.action in ['buy_close', 'sell_close']) and (_order.hold_closetick_num >= self.max_wait_tick_num_close_order):
                    if _order.status == 'partial_fill':
                        _order.status = 'partial_cancel'
                    else:
                        _order.status = 'cancel'
                    # if _order.action in ['sell_close']:
                    #     self.cancel_close = True
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
                    cancel_num += 1
            _cancel_idx.reverse()
            for _idx in _cancel_idx:
                # print('close ticknum cancel:', order_submitted_list[_idx].__dict__)
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
            # print(nowtime, 'chedan ')
            # 价格优先 时间优先
            if order_submitted_list[0].action in ['buy_open', 'buy_close']:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(x.submit_price, x.create_time))
            else:
                order_submitted_list = sorted(order_submitted_list, key = lambda x:(-1 * x.submit_price, x.create_time))
            cancel_num = 0
            _cancel_idx = []
            for k in range(len(order_submitted_list)):
                # if cancel_num >= self.order_num_pertick:
                #     break
                _order = order_submitted_list[k]
                if _order.hold_tick_num >= self.update_order_ticknum:
                    if _order.status == 'partial_fill':
                        _order.status = 'partial_cancel'
                    else:
                        _order.status = 'cancel'
                    # if _order.action in ['sell_close']:
                    #     self.cancel_close = True
                    _order.finish_time = nowtime
                    _order.finish_sig = now_sig
                    order_finished_list.append(_order)
                    _cancel_idx.append(k)
                    cancel_num += 1
            _cancel_idx.reverse()

            for _idx in _cancel_idx:
                # print('cancel_by_update_order_ticknum', now_hold_num, nowtime, order_submitted_list[_idx].__dict__)
                del order_submitted_list[_idx]

        return order_submitted_list, order_finished_list

    def trade_helper(self, finishdf):
        bs_dict = {'buy': 1, 'sell': -1}
        finishdf['action_bs'] = finishdf['action'].apply(lambda x: bs_dict[x.split('_')[0]])
        finishdf['action_oc'] = finishdf['action'].apply(lambda x: x.split('_')[1])

        total_order_counts = len(finishdf)
        canceldf = finishdf[finishdf['status'] == 'cancel']
        cancel_order_counts = len(canceldf)
        filldf = finishdf[finishdf['status'].isin(['fill', 'partial_cancel'])]

        filldf['quantity_bs'] = filldf['finish_quantity'] * filldf['action_bs']
        filldf['now_hold_num'] = round(filldf.quantity_bs.cumsum(), 5)
       
        filldf.loc[filldf['now_hold_num'] == 0, 'deal_count'] = 1
        filldf['deal_count'] = filldf['deal_count'].cumsum().fillna(method='bfill')

        filldf['fill_value'] = filldf.fill_price * filldf.finish_quantity * self.face_value
        filldf['fee'] = filldf['fill_value'] * self.c_rate

        pen_price_df = filldf.groupby(['deal_count', 'action_oc']).agg(
            {'fill_value': 'sum', 'finish_quantity': 'sum', 'fee': 'sum'})
        pen_price_df['weighted_price'] = pen_price_df['fill_value'] / pen_price_df['finish_quantity'] / self.face_value

        pendf = filldf.groupby('deal_count').agg(
            {'quantity_bs': 'first', 'now_hold_num': lambda x: max(abs(x)), 'create_time': 'first',
             'finish_time': 'last'})
        pendf['now_hold_num'] = pendf['now_hold_num'] * np.sign(pendf['quantity_bs'])

        rlist = [pendf]
        for x in ['open', 'close']:
            rlist.append(pen_price_df[['fill_value', 'fee', 'weighted_price']].xs(x, level=1).add_prefix('%s_' % x))

        rdf = pd.concat(rlist, axis=1)

        rdf['profit_intradeal'] = (rdf['close_fill_value'] - rdf['open_fill_value'])*np.sign(rdf['quantity_bs']) - rdf['open_fee'] - rdf['close_fee']
        rdf['change'] = rdf['profit_intradeal'] / self.initial_cash
        rdf['equity_curve'] = rdf['change'].cumsum() + 1
        rdf['hold_time_seconds'] = rdf.apply(lambda x: get_timediff_seconds(x.create_time, x.finish_time), axis=1)
        rdf['hold_time_minutes'] = rdf['hold_time_seconds'] / 60
        
        rdf = rdf.rename(columns={'quantity_bs':'pos', 'now_hold_num': 'pos_num'})
        rdf['pos'] = np.sign(rdf['pos'])
        return rdf, total_order_counts, cancel_order_counts

    def back_test_singleday(self, date):
        signal_date = self.signal.join(self.origin_tick, how = 'left').reset_index()
        # signal_date['deal_px_vol'] = signal_date['deal_px_vol'].shift(-1)
        signal_date['vwap'] = signal_date['amount'] / signal_date['volume'] / self.face_value
        signal_date = signal_date.replace([np.inf, -np.inf], np.nan)
        _temp = signal_date.set_index('dt')[['raw','deal_px_vol','vwap']]
        
        signal_date = signal_date.rename(columns = {'bid_p1':'Buy1Price', 'ask_p1':'Sell1Price', 'close':'LastPx'})
        col_list = signal_date.columns.tolist()
        signal_date = signal_date.values
        
        dt_idx = col_list.index('dt')
        raw_idx = col_list.index('raw')
        Buy1Price_idx = col_list.index('Buy1Price')
        Sell1Price_idx = col_list.index('Sell1Price')
        LastPx_idx = col_list.index('LastPx')
        deal_px_vol_idx = col_list.index('deal_px_vol')
        vwap_idx = col_list.index('vwap')
        pred_sell_volume_idx = col_list.index('pred_sell_volume')
        bids_idx = col_list.index('bids')
        pred_buy_volume_idx = col_list.index('pred_buy_volume')
        asks_idx = col_list.index('asks')

        now_hold_num = 0

        date_signal_lenth = len(signal_date)
        order_submitted_list = []  # 当前提交的订单
        order_finished_list = []  # 提交的订单结束，成交或被撤销
        target_pos = 0  # 此bar的目标仓位
        put_order_status = 'no_pos'  # 初始化订单操作的action

        for i in tqdm(range(1, date_signal_lenth)):
            # print(i)
            assert round(np.sum([x.remain_quantity for x in order_submitted_list]), 5) <= self.max_pos, (date, i, np.sum([x.remain_quantity for x in order_submitted_list])) #change
            now_tick = signal_date[i]
            now_sig = round(now_tick[raw_idx], 6)
            nowtime = now_tick[dt_idx]

            now_hold_num = round(now_hold_num, 5)
            
            buy1px = now_tick[Buy1Price_idx]
            sell1px = now_tick[Sell1Price_idx]
            # if now_hold_num == 0 and sell1px - buy1px > 2.5 and buy1px - signal_date[i-1][Buy1Price_idx] < -2.5:
            #     now_sig = -0.7
            if self.close_pos_quickly:
                if now_hold_num > 0:
                    now_sig = -0.7
                elif now_hold_num < 0:
                    now_sig = 0.7
            # if int(nowtime.strftime('%Y%m%d')) > 20240105:
            #     print(nowtime, now_sig, now_hold_num)

            lastpx = now_tick[LastPx_idx]
            vwappx = now_tick[vwap_idx]
            _deal_px_vol = now_tick[deal_px_vol_idx]
            # print(nowtime, _deal_px_vol)
            if _deal_px_vol != _deal_px_vol:
                deal_px_vol = {}
            else:
                deal_px_vol = {}
                for x in _deal_px_vol:
                    if x[0] in deal_px_vol.keys():
                        deal_px_vol[x[0]] += x[1] * self.trade_deal_ratio
                    else:
                        deal_px_vol[x[0]] = x[1] * self.trade_deal_ratio
            
            if len(order_submitted_list) > 0:
                # 判断成交
                order_submitted_list, order_finished_list, _fill_quantity_sum = make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, deal_px_vol, nowtime, now_sig, vwappx)
                if now_hold_num == 0 and _fill_quantity_sum != 0:
                    self.now_open_price = open_price
                    self.now_open_time = nowtime
                now_hold_num += _fill_quantity_sum
                
        
                # 撤单
                order_submitted_list, order_finished_list = self.cancel_order(order_submitted_list, order_finished_list, now_sig, now_hold_num, put_order_status, nowtime)
                
                # 当有挂单时，更新挂单持仓ticks
                for _order in order_submitted_list:
                    _order.hold_tick_num += 1
                    if _order.action == 'buy_close' and (now_sig > self.out_submit_order_t * -1):
                        _order.hold_closetick_num += 1
                    elif _order.action == 'sell_close' and (now_sig < self.out_submit_order_t):
                        _order.hold_closetick_num += 1

            need_trade_num, put_order_status = self.get_trade_num(order_submitted_list, now_sig,
                                                                                      round(now_hold_num, 5),
                                                                                      put_order_status, nowtime, date)
            need_trade_num = round(need_trade_num, 5)
            # print('*' * 10, i, now_sig, need_trade_num, now_hold_num, put_order_status, nowtime, '*' * 10)
            # for xx in order_submitted_list:
            #     print(xx.__dict__)

            tickslippage = self.get_tickslippage(now_sig, now_hold_num)

            if need_trade_num != 0:
                open_contract_num = round(min(abs(need_trade_num), self.order_num_pertick), 5)
                need_trade_num_state = np.sign(need_trade_num)
                # the price of the order
                buy_px_list = [buy1px, sell1px, (buy1px + sell1px) / 2, buy1px + tickslippage]
                sell_px_list = [sell1px, buy1px, (buy1px + sell1px) / 2, sell1px - tickslippage]
                submit_px_inob = 0
                if need_trade_num > 0:
                    if now_hold_num < 0:#说明是平仓
                        open_price = min(buy1px, self.now_open_price - 0.01)
                    else:
                        if self.buy_px_idx == 4:
                            pred_sell_volume = now_tick[pred_sell_volume_idx]
                            bids = now_tick[bids_idx]
                            bids = [[float(x[0]),float(x[1])] for x in eval(bids)]
                            open_price, submit_px_inob = get_buy_px(bids, pred_sell_volume)
                            if buy1px - open_price < self.order_price_N * 2:
                                open_price = None
                        else:
                            open_price = buy_px_list[self.buy_px_idx]#buy1px # (buy1px + sell1px) / 2 # buy1px + tickslippage
                else:
                    if now_hold_num > 0:
                        open_price = max(sell1px, self.now_open_price + 0.01)#buy1px # (buy1px + sell1px) / 2 # sell1px - tickslippage
                    else:
                        if self.sell_px_idx == 4:
                            pred_buy_volume = now_tick[pred_buy_volume_idx]
                            asks = now_tick[asks_idx]
                            asks = [[float(x[0]),float(x[1])] for x in eval(asks)]
                            open_price, submit_px_inob = get_buy_px(asks, pred_buy_volume)
                            if open_price - sell1px < self.order_price_N * 2:
                                open_price = None
                        else:
                            open_price = sell_px_list[self.sell_px_idx]


                # if self.cancel_close == True:
                #     open_price = buy1px
                # self.cancel_close = False
                tickdt_time = nowtime
                tick_pxlist = [buy1px, sell1px, lastpx]

                if put_order_status in ['buy_open_pos', 'sell_open_pos'] and open_price is not None:  # 当需要挂单开仓时
                    _order = Order(symbol=self.ticker, action=None, submit_price=open_price, quantity=open_contract_num, status='submit',
                                   create_sig = now_sig, create_time=nowtime,  create_tick_pxlist=tick_pxlist, submit_px_inob = submit_px_inob)
                    if need_trade_num_state == 1:
                        _order.action = 'buy_open'
                        need_trade_num -= open_contract_num
                    else:
                        _order.action = 'sell_open'
                        need_trade_num += open_contract_num
                    _order.hold_tick_num += 1

                    # if self.close_use_market_order and _order.action in ['sell_close', 'sell_open']:
                    #     if sell1px - signal_date[i-1][Sell1Price_idx] < -30:
                    #         _order.order_type = 'market'

                    order_submitted_list += [copy.deepcopy(_order)]
             
                elif put_order_status in ['buy_close_pos', 'sell_close_pos','close_pos'] and open_price is not None:
                    _order = Order(symbol=self.ticker, action=None, submit_price=open_price, quantity=open_contract_num, status='submit',
                                   create_sig = now_sig, create_time=nowtime, create_tick_pxlist=tick_pxlist, submit_px_inob = submit_px_inob)
                    if need_trade_num_state == 1:
                        _order.action = 'buy_close'
                        need_trade_num -= open_contract_num
                    else:
                        _order.action = 'sell_close'
                        need_trade_num += open_contract_num
                    _order.hold_tick_num += 1
                    _order.hold_closetick_num += 1

                    if (nowtime - self.now_open_time).seconds >= 10:
                        _order.order_type = 'market'
                    
                    if _order.action == 'sell_close' and sell1px - self.now_open_price < -50:
                        _order.order_type = 'market'
                    elif _order.action == 'buy_close' and buy1px - self.now_open_price > 50:
                        _order.order_type = 'market'
                
                    if self.close_use_market_order:
                        if _order.action == 'sell_close' and sell1px - signal_date[i-1][Sell1Price_idx] < -30:
                            _order.order_type = 'market'
                        elif _order.action == 'buy_close' and buy1px - signal_date[i-1][Buy1Price_idx] > 30:
                            _order.order_type = 'market'

                    order_submitted_list += [copy.deepcopy(_order)]
                    
            # print('#######')
            # for xx in order_submitted_list:
            #     print(xx.__dict__)
            # print('%%%%%%%')
            # for xx in order_finished_list:
            #     print(xx.__dict__)
    
        # assert len(order_submitted_list) == 0, date
        col_list = ['symbol', 'action', 'submit_price', 'fill_price', 'quantity', 'finish_quantity', 'remain_quantity', 'status', 'create_time',
                    'create_sig', 'finish_time','finish_sig', 'create_tick_pxlist', 'finish_tick_pxlist', 'hold_tick_num', 'hold_closetick_num', 'submit_px_inob', 'order_type']
        finishdf = [[x.symbol, x.action, x.submit_price, x.fill_price, x.quantity, x.finish_quantity, x.remain_quantity, x.status, x.create_time, x.create_sig,
             x.finish_time, x.finish_sig, x.create_tick_pxlist, x.finish_tick_pxlist, x.hold_tick_num, x.hold_closetick_num, x.submit_px_inob, x.order_type] for x in order_finished_list]
        finishdf = pd.DataFrame(finishdf, columns=col_list)
        
        finishdf['dt'] = finishdf['create_time']
        finishdf = finishdf.set_index('dt')
        finishdf = _temp.join(finishdf, how = 'left').reset_index()
        return finishdf

    def back_test(self):
        date_list = [int(x.strftime('%Y%m%d')) for x in set(self.signal.index.date)]
        date_list.sort()
        # with Pool(self.n_jobs) as pool:
        #     rlist = pool.map(self.back_test_singleday, date_list)
        
        rlist = [self.back_test_singleday('test_date')]

        trade_df = pd.concat(rlist, axis=0).sort_values(by='dt')
        _trade_df = trade_df.dropna(subset = ['symbol']).sort_values(by = 'create_time')

        totaltrade_df, total_order_counts, cancel_order_counts = self.trade_helper(_trade_df)

        results, daily_return = strategy_evaluate(totaltrade_df.copy(), self.initial_cash, total_order_counts, cancel_order_counts)
        daily_return.columns = ['daily_return','daily_equty_curve']
        
        if self.save_results:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_total_trade_detail.csv'))
            if self.save_detail:
                _trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_order_detail.csv'))
                daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + '_results.csv'), encoding='gbk')
            totaltrade_df.set_index('create_time').change.cumsum().plot(figsize=(8, 4))
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + '_profit.png'))
            plt.show()
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
result_date = 20220804
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