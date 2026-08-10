%matplotlib inline
# -*- coding:UTF-8 -*-
import matplotlib
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
warnings.filterwarnings('ignore')
import dill


class Order:
    def __init__(self, symbol=None, action=None, submit_price=None, fill_price=None, quantity=0, status=None,
                 create_sig = None, create_time=None, create_ticktime=None, finish_sig = None, finish_time=None, finish_ticktime=None,
                 create_tick_pxlist=[], finish_tick_pxlist=[]):
        self.symbol = symbol
        self.action = action  # buy_open sell_open buy_close sell_close
        self.submit_price = submit_price  # 发单价格
        self.fill_price = fill_price  # 成交价格
        self.quantity = quantity
        self.status = status  # 订单当前的状态submit为挂单 fill为已经成交 cancel为已经撤销
        self.create_sig = create_sig # 触发开仓的信号
        self.create_time = create_time  # 在哪个信号bar的时间戳上发的单
        self.create_ticktime = create_ticktime  # 基于哪个tick时间发的单
        self.finish_sig = finish_sig # 触发平仓的信号
        self.finish_time = finish_time  # 在哪个信号bar的时间戳上成交的
        self.finish_ticktime = finish_ticktime  # 基于哪个tick成交的
        self.create_tick_pxlist = create_tick_pxlist  # 基于哪个tick挂的单，此tick的[buy1price, sell1price, lastpx]
        self.finish_tick_pxlist = finish_tick_pxlist  # 基于哪个tick成交的，此tick的[buy1price, sell1price, lastpx]


def strategy_evaluate(pnl, initial_cash, total_order_counts, cancel_order_counts):
    # ===新建一个dataframe保存回测指标
    results = pd.DataFrame()

    # ===计算累积净值
    results.loc[0, '累积净值'] = round(pnl['equity_curve'].iloc[-1], 3)

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
    results.loc[0, '最大回撤'] = format(max_draw_down, '.2%')
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
    results.loc[0, '总撤单数量'] = cancel_order_counts
    results.loc[0, '胜率'] = format(results.loc[0, '盈利笔数'] / len(pnl), '.2%')  # 胜率

    longtrade = pnl[pnl['pos'] == 1]
    shorttrade = pnl[pnl['pos'] == -1]
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
    results.loc[0, '每笔交易平均盈亏'] = round(pnl['change'].mean(), 6)  # 每笔交易平均盈亏
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
        if x.action in ['buy_open']:
            order_submitted_num += x.quantity
        elif x.action == 'sell_open':
            order_submitted_num -= x.quantity
    assert 'buy_open' not in _ or 'sell_open' not in _, str(date) + str(_)
    return order_submitted_num


def make_deal(order_submitted_list, order_finished_list, buy1px, sell1px, lastpx, tickdt, nowtime, pre_sig):
    #     _fill_money_sum = 0
    _fill_quantity_sum = 0
    _fill_idx = []
    for k in range(len(order_submitted_list)):
        _order = order_submitted_list[k]
        if _order.action in ['buy_open', 'buy_close'] and _order.status == 'submit':
            if min(lastpx, sell1px) <= _order.submit_price:
                _order.status = 'fill'
                _order.fill_price = min(_order.submit_price, sell1px)
                _order.finish_sig = pre_sig
                _order.finish_time = nowtime
                _order.finish_ticktime = tickdt
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                order_finished_list.append(_order)
                #                 _fill_money_sum += _order.submit_price * _order.quantity * self.face_value
                _fill_quantity_sum += _order.quantity
                _fill_idx.append(k)
        elif _order.action in ['sell_open', 'sell_close'] and _order.status == 'submit':
            if max(lastpx, buy1px) >= _order.submit_price:
                _order.status = 'fill'
                _order.fill_price = max(_order.submit_price, buy1px)
                _order.finish_sig = pre_sig
                _order.finish_time = nowtime
                _order.finish_ticktime = tickdt
                _order.finish_tick_pxlist = [buy1px, sell1px, lastpx]
                order_finished_list.append(_order)
                #                 _fill_money_sum += _order.submit_price * _order.quantity * self.face_value
                _fill_quantity_sum -= _order.quantity
                _fill_idx.append(k)
    if len(_fill_idx) > 0:
        _fill_idx.reverse()
        for _idx in _fill_idx:
            del order_submitted_list[_idx]
    return order_submitted_list, order_finished_list, _fill_quantity_sum


def get_timediff_seconds(start_time, end_time):
    m = (end_time - start_time).total_seconds()
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90 * 60
    else:
        return m


class TS_BACK_TEST:

    def __init__(self, signal, in_t=0.9, submit_order_t=0.8, out_t=0.7, initial_cash=2e8, cash_divnum=10,
                 ticker='IC.CFE',
                 start_date=None, end_date=None, n_jobs=24,
                 c_rate=3 / 100000, tickslippage_dict={(0, 0.5): 10, (0.5, 0.7): 1.2, (0.7, 0.9): 0.8, (0.9, 100): 0.2},
                 vol_pertick=1,
                 delay_tick_num=0, put_limit_order_per_ticknum=1, max_wait_tick_num=4,
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
        self.submit_order_t = submit_order_t
        self.out_t = out_t
        self.initial_cash = initial_cash
        self.cash_divnum = cash_divnum
        self.ticker = ticker
        self.put_limit_order_per_ticknum = put_limit_order_per_ticknum  # 每隔几个tick挂一个限价单，默认为1表示每个tick挂一个限价单
        face_value_dict = {'IC.CFE': 200,
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
        self.vol_pertick = vol_pertick
        self.max_wait_tick_num = max_wait_tick_num
        self.delay_tick_num = delay_tick_num
        self.n_jobs = n_jobs

        columns_list = self.signal.reset_index().columns.tolist()
        global dt_idx, raw_idx
        dt_idx = columns_list.index('dt')
        raw_idx = columns_list.index('raw')

        univ = IO.read_data([self.start_date, self.end_date], columns=['contract_00'],
                            alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
        self.univ = univ.xs(self.ticker, level=1)
        self.daily_opendata = IO.read_data([self.start_date, self.end_date], columns=['open'],
                                           alt='/data/user/015626/data/share/MD/CHINA_FUTURES/daily/MD_SIF_TICK_TO_DAILY_ALL_CONTRACT.h5')

    def get_tickslippage(self, _presig):
        for k, v in self.tickslippage_dict.items():
            if (abs(_presig) >= k[0]) and (abs(_presig) < k[1]):
                return v

    def get_trade_num(self, _order_submitted_list, pre_sig, max_pos, pre_hold_num, put_order_status, nowtime, date):
        # 当前挂单数量
#         print('***',nowtime, pre_sig, pre_hold_num, put_order_status)
#         for x in _order_submitted_list:
#             print(x.__dict__)
        order_submitted_num = get_order_submitted_num(_order_submitted_list, date)
#         print('order_submitted_num:',order_submitted_num)
        iscancel_openorder = False
        iscancel_closeorder = False
        if nowtime.time() < self.trade_start_time:
            need_trade_num = 0
            #             print(pre_hold_num, pre_sig, need_trade_num, put_order_status)
            return need_trade_num, put_order_status, iscancel_openorder, iscancel_closeorder
        elif nowtime.time() >= self.trade_end_time:
            target_pos = 0
            put_order_status = 'close_pos'
            # 撤单
            iscancel_openorder = True
            need_trade_num = pre_hold_num * -1
            #             print(pre_hold_num, pre_sig, need_trade_num, put_order_status)
            return need_trade_num, put_order_status, iscancel_openorder, iscancel_closeorder

        if abs(pre_sig) >= self.in_t:
            target_pos = max_pos * np.sign(pre_sig)
            put_order_status = 'open_pos'
            need_trade_num = target_pos - pre_hold_num - order_submitted_num
            iscancel_closeorder = True
        elif abs(pre_sig) >= self.submit_order_t:
            if put_order_status == 'open_pos':
                target_pos = max_pos * np.sign(pre_sig)
                need_trade_num = target_pos - pre_hold_num - order_submitted_num
            else:
                need_trade_num = 0
            iscancel_closeorder = True
        elif abs(pre_sig) >= self.out_t:
            if put_order_status == 'close_pos':
                need_trade_num = pre_hold_num * -1
            else:
                put_order_status = 'no_pos'
                need_trade_num = 0
                iscancel_closeorder = True
        elif abs(pre_sig) < self.out_t:
            target_pos = 0
            put_order_status = 'close_pos'
            # 撤单
            iscancel_openorder = True
            need_trade_num = pre_hold_num * -1
        if np.sign(pre_sig) * np.sign(pre_hold_num) < 0:
            iscancel_openorder = True
            need_trade_num = pre_hold_num * -1
            put_order_status = 'close_pos'
#         print(pre_hold_num, pre_sig, need_trade_num, put_order_status)
        return need_trade_num, put_order_status, iscancel_openorder, iscancel_closeorder

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
        filldf['hold_ticktime_seconds'] = filldf.apply(
            lambda x: get_timediff_seconds(x.create_ticktime, x.finish_ticktime), axis=1)
        filldf['hold_ticktime_minutes'] = filldf['hold_ticktime_seconds'] / 60

        filldf.loc[filldf['now_hold_num'] == 0, 'deal_count'] = 1
        filldf['deal_count'] = filldf['deal_count'].cumsum().fillna(method='bfill')

        filldf['fill_value'] = filldf.fill_price * filldf.quantity * self.face_value
        filldf['fee'] = filldf['fill_value'] * self.c_rate

        pen_price_df = filldf.groupby(['deal_count', 'action_oc']).agg(
            {'fill_value': 'sum', 'quantity': 'sum', 'fee': 'sum'})
        pen_price_df['weighted_price'] = pen_price_df['fill_value'] / pen_price_df['quantity'] / self.face_value

        pendf = filldf.groupby('deal_count').agg(
            {'quantity_bs': 'first', 'now_hold_num': lambda x: max(abs(x)), 'create_time': 'first',
             'create_ticktime': 'first', 'finish_time': 'last', 'finish_ticktime': 'last'})
        pendf['now_hold_num'] = pendf['now_hold_num'] * pendf['quantity_bs']

        rlist = [pendf]
        for x in ['open', 'close']:
            rlist.append(pen_price_df[['fill_value', 'fee', 'weighted_price']].xs(x, level=1).add_prefix('%s_' % x))

        rdf = pd.concat(rlist, axis=1)

        rdf['profit_intradeal'] = rdf['close_fill_value'] - rdf['open_fill_value'] - rdf['open_fee'] - rdf['close_fee']
        rdf['change'] = rdf['profit_intradeal'] / self.initial_cash
        rdf['equity_curve'] = rdf['change'].cumsum() + 1
        rdf['hold_time_seconds'] = rdf.apply(lambda x: get_timediff_seconds(x.create_time, x.finish_time), axis=1)
        rdf['hold_time_minutes'] = rdf['hold_time_seconds'] / 60
        rdf['hold_ticktime_seconds'] = rdf.apply(lambda x: get_timediff_seconds(x.create_ticktime, x.finish_ticktime),
                                                 axis=1)
        rdf['hold_ticktime_minutes'] = rdf['hold_ticktime_seconds'] / 60

        rdf = rdf.rename(columns={'quantity_bs': 'pos', 'now_hold_num': 'pos_num'})
        return rdf, total_order_counts, cancel_order_counts

    def back_test_singleday(self, date):
        signal_date = self.signal.loc[str(date)].reset_index().values
        temp_contract = self.univ.loc[str(date)]['contract_00']
        contract = temp_contract.split('.')[0]
        open_price_930 = self.daily_opendata.loc[(str(date), temp_contract)]['open']  # calculate position
        max_pos = np.floor(self.initial_cash / self.cash_divnum / (open_price_930 * self.face_value))

        tickdf = pd.read_csv(
            '/data/user/015626/data/share/MD/CHINA_FUTURES/TICK/STOCK_INDEX_FUTURE/%s/%s.csv' % (contract, date),
            index_col=0, parse_dates=True)[['Buy1Price', 'Sell1Price', 'TotalVolumeTrade', 'LastPx']]
        tickdf['dt'] = tickdf.index
        tickdf['TotalVolumeTrade'] = tickdf.TotalVolumeTrade.diff()
        tickdf = tickdf.round({'Buy1Price': 1, 'Sell1Price': 1, 'LastPx': 1})
        idx_tickdf = tickdf.index
        buy1px_idx = tickdf.columns.tolist().index('Buy1Price')
        sell1px_idx = tickdf.columns.tolist().index('Sell1Price')
        volume_idx = tickdf.columns.tolist().index('TotalVolumeTrade')
        lastpx_idx = tickdf.columns.tolist().index('LastPx')
        tickdt_idx = tickdf.columns.tolist().index('dt')

        now_hold_num = 0
        pre_hold_num = 0  # 记录上一时刻仓位,计算多少笔交易时使用

        date_signal_lenth = len(signal_date)
        pre_sig = signal_date[0][raw_idx]
        order_submitted_list = []  # 当前提交的订单
        order_finished_list = []  # 提交的订单结束，成交或被撤销
        target_pos = 0  # 此bar的目标仓位
        put_order_status = 'no_pos'  # 初始化订单操作的action

        for i in range(1, date_signal_lenth):
            pre_sig = round(pre_sig, 6)
            nowtime = signal_date[i][dt_idx]

            #             print(nowtime)
            need_trade_num, put_order_status, iscancel_openorder, iscancel_closeorder = self.get_trade_num(order_submitted_list, pre_sig,
                                                                                      max_pos, pre_hold_num,
                                                                                      put_order_status, nowtime, date)
            cancel_action_list = []
            if iscancel_openorder:
                cancel_action_list += ['buy_open', 'sell_open']
            if iscancel_closeorder:
                cancel_action_list += ['buy_close', 'sell_close']

            if len(cancel_action_list) > 0 and len(order_submitted_list) > 0:
                _cancel_idx = []
                for k in range(len(order_submitted_list)):
                    _order = order_submitted_list[k]
                    if _order.action in cancel_action_list:
                        _order.status = 'cancel'
                        _order.finish_time = nowtime
                        _order.finish_sig = pre_sig
                        order_finished_list.append(_order)
                        _cancel_idx.append(k)
                _cancel_idx.reverse()
                for _idx in _cancel_idx:
                    del order_submitted_list[_idx]

            tickslippage = self.get_tickslippage(pre_sig)

            if (i == (date_signal_lenth - 1)):
                nexttime = nowtime + (nowtime - signal_date[i - 1][dt_idx])
            else:
                nexttime = signal_date[i + 1][dt_idx]
            order_px_para = tickdf.loc[(idx_tickdf.time >= nowtime.time()) & (idx_tickdf.time < nexttime.time())].values

            if need_trade_num == 0:
                # 当有挂单时，要看此时间段内挂单是否成交 成交记录以及剔除list待完成
                if len(order_submitted_list) > 0:
                    for z in range(len(order_px_para)):
                        order_submitted_list, order_finished_list, fill_quantity_sum = make_deal(order_submitted_list,
                                                                                                 order_finished_list,
                                                                                                 order_px_para[z][
                                                                                                     buy1px_idx],
                                                                                                 order_px_para[z][
                                                                                                     sell1px_idx],
                                                                                                 order_px_para[z][
                                                                                                     lastpx_idx],
                                                                                                 order_px_para[z][
                                                                                                     tickdt_idx],
                                                                                                 nowtime, pre_sig)
                        now_hold_num = now_hold_num + fill_quantity_sum
            else:  # 发单
                open_contract_num = abs(need_trade_num)
                need_trade_num_state = np.sign(need_trade_num)
                # the price of the first order
                pre_tickdf = tickdf.loc[idx_tickdf.time < nowtime.time()].iloc[-1 * (self.delay_tick_num + 1):].values
                if need_trade_num > 0:
                    open_price = pre_tickdf[0][buy1px_idx] + tickslippage
                else:
                    open_price = pre_tickdf[0][sell1px_idx] - tickslippage
                tickdt_time = pre_tickdf[0][tickdt_idx]
                tick_pxlist = [pre_tickdf[0][buy1px_idx], pre_tickdf[0][sell1px_idx], pre_tickdf[0][lastpx_idx]]

                if put_order_status == 'open_pos':  # 当需要挂单开仓时
                    put_order_flag = True  # 是否进行挂单操作
                    _order = Order(symbol=contract, action=None, submit_price=open_price, quantity=1, status='submit',
                                   create_sig = pre_sig, create_time=nowtime, create_ticktime=tickdt_time, create_tick_pxlist=tick_pxlist)
                    if need_trade_num_state == 1:
                        _order.action = 'buy_open'
                        need_trade_num -= 1
                    else:
                        _order.action = 'sell_open'
                        need_trade_num += 1
                    order_submitted_list.append(_order)
                    if need_trade_num == 0:
                        put_order_flag = False
                    
                    wait_tick_num = 0
                    for z in range(len(order_px_para)):
                        order_submitted_list, order_finished_list, fill_quantity_sum = make_deal(order_submitted_list,
                                                                                                 order_finished_list,
                                                                                                 order_px_para[z][
                                                                                                     buy1px_idx],
                                                                                                 order_px_para[z][
                                                                                                     sell1px_idx],
                                                                                                 order_px_para[z][
                                                                                                     lastpx_idx],
                                                                                                 order_px_para[z][
                                                                                                     tickdt_idx],
                                                                                                 nowtime, pre_sig)
                        now_hold_num = now_hold_num + fill_quantity_sum

                        wait_tick_num += 1
                        if wait_tick_num >= self.put_limit_order_per_ticknum and put_order_flag:
                            if z - self.delay_tick_num < 0:
                                if need_trade_num_state == 1:
                                    open_price = pre_tickdf[z + 1][buy1px_idx] + tickslippage
                                else:
                                    open_price = pre_tickdf[z + 1][sell1px_idx] - tickslippage
                                tickdt_time = pre_tickdf[z + 1][tickdt_idx]
                                tick_pxlist = [pre_tickdf[z + 1][buy1px_idx], pre_tickdf[z + 1][sell1px_idx],
                                               pre_tickdf[z + 1][lastpx_idx]]
                            else:
                                if need_trade_num_state == 1:
                                    open_price = order_px_para[z - self.delay_tick_num][buy1px_idx] + tickslippage
                                else:
                                    open_price = order_px_para[z - self.delay_tick_num][sell1px_idx] - tickslippage
                                tickdt_time = order_px_para[z - self.delay_tick_num][tickdt_idx]
                                tick_pxlist = [order_px_para[z - self.delay_tick_num][buy1px_idx],
                                               order_px_para[z - self.delay_tick_num][sell1px_idx],
                                               order_px_para[z - self.delay_tick_num][lastpx_idx]]

                            if need_trade_num_state == 1:
                                _order = Order(symbol=contract, action='buy_open', submit_price=open_price,
                                               quantity=1, status='submit', create_sig = pre_sig, create_time=nowtime,
                                               create_ticktime=tickdt_time, create_tick_pxlist=tick_pxlist)
                                order_submitted_list.append(_order)
                                need_trade_num -= 1
                            else:
                                _order = Order(symbol=contract, action='sell_open', submit_price=open_price,
                                               quantity=1, status='submit', create_sig = pre_sig, create_time=nowtime,
                                               create_ticktime=tickdt_time, create_tick_pxlist=tick_pxlist)
                                order_submitted_list.append(_order)
                                need_trade_num += 1
                            wait_tick_num = 0
                            if need_trade_num == 0:
                                put_order_flag = False
                elif put_order_status == 'close_pos':
                    wait_tick_num = 0
                    makedealflag = False
                    for z in range(len(order_px_para)):
                        #                         if abs(abs(open_price) / valid_px - 1) >= 0.05:
                        #                             continue
                        if not makedealflag:
                            # 现将所有平仓单撤掉
                            if len(order_submitted_list) > 0:
                                _cancel_idx = []
                                for k in range(len(order_submitted_list)):
                                    _order = order_submitted_list[k]
                                    if _order.action in ['buy_close', 'sell_close']:
                                        _order.status = 'cancel'
                                        _order.finish_sig = pre_sig
                                        _order.finish_time = nowtime
                                        _order.finish_ticktime = tickdt_time
                                        order_finished_list.append(_order)
                                        _cancel_idx.append(k)
                                _cancel_idx.reverse()
                                for _idx in _cancel_idx:
                                    del order_submitted_list[_idx]

                            _order = Order(symbol=contract, action=None, submit_price=open_price, quantity=1,
                                           status='submit', create_sig = pre_sig, create_time=nowtime,
                                           create_ticktime=tickdt_time, create_tick_pxlist=tick_pxlist)
                            if need_trade_num_state == 1:
                                _order.action = 'buy_close'
                            #                                 need_trade_num -= 1
                            else:
                                _order.action = 'sell_close'
                            #                                 need_trade_num += 1
                            order_submitted_list.append(_order)
                            makedealflag = True

                        tickvolume = order_px_para[z][volume_idx]
                        if tickvolume > 0:
                            order_submitted_list, order_finished_list, fill_quantity_sum = make_deal(
                                order_submitted_list, order_finished_list, order_px_para[z][buy1px_idx],
                                order_px_para[z][sell1px_idx], order_px_para[z][lastpx_idx],
                                order_px_para[z][tickdt_idx], nowtime, pre_sig)
                            now_hold_num = now_hold_num + fill_quantity_sum
                            need_trade_num = need_trade_num - fill_quantity_sum
                            if need_trade_num == 0:
                                break

                        wait_tick_num += 1
                        if wait_tick_num >= self.max_wait_tick_num:
                            if z - self.delay_tick_num < 0:
                                if need_trade_num > 0:
                                    open_price = pre_tickdf[z + 1][buy1px_idx] + tickslippage
                                else:
                                    open_price = pre_tickdf[z + 1][sell1px_idx] - tickslippage
                                tickdt_time = pre_tickdf[z + 1][tickdt_idx]
                                tick_pxlist = [pre_tickdf[z + 1][buy1px_idx], pre_tickdf[z + 1][sell1px_idx],
                                               pre_tickdf[z + 1][lastpx_idx]]
                            else:
                                if need_trade_num > 0:
                                    open_price = order_px_para[z - self.delay_tick_num][buy1px_idx] + tickslippage
                                else:
                                    open_price = order_px_para[z - self.delay_tick_num][sell1px_idx] - tickslippage
                                tickdt_time = order_px_para[z - self.delay_tick_num][tickdt_idx]
                                tick_pxlist = [order_px_para[z - self.delay_tick_num][buy1px_idx],
                                               order_px_para[z - self.delay_tick_num][sell1px_idx],
                                               order_px_para[z - self.delay_tick_num][lastpx_idx]]

                            wait_tick_num = 0
                            makedealflag = False

                        if open_contract_num == 0:
                            break
            pre_sig = signal_date[i][raw_idx]
            pre_hold_num = now_hold_num

        assert len(order_submitted_list) == 0, date
        col_list = ['symbol', 'action', 'submit_price', 'fill_price', 'quantity', 'status', 'create_time',
                    'create_ticktime','create_sig', 'finish_time', 'finish_ticktime','finish_sig', 'create_tick_pxlist', 'finish_tick_pxlist']
        finishdf = [
            [x.symbol, x.action, x.submit_price, x.fill_price, x.quantity, x.status, x.create_time, x.create_ticktime,x.create_sig,
             x.finish_time, x.finish_ticktime,x.finish_sig, x.create_tick_pxlist, x.finish_tick_pxlist] for x in order_finished_list]
        finishdf = pd.DataFrame(finishdf, columns=col_list)

        return finishdf

    def back_test(self):
        date_list = [int(x.strftime('%Y%m%d')) for x in set(self.signal.index.date)]
        date_list.sort()
        with Pool(self.n_jobs) as pool:
            rlist = pool.map(self.back_test_singleday, date_list)
        #         rlist = []
        #         for date in date_list:
        #             print(date)
        #             rlist.append(self.back_test_singleday(date))
        trade_df = pd.concat(rlist, axis=0).sort_values(by='create_ticktime')

        totaltrade_df, total_order_counts, cancel_order_counts = self.trade_helper(trade_df)
        results, daily_return = strategy_evaluate(totaltrade_df, self.initial_cash, total_order_counts, cancel_order_counts)
        daily_return.columns = ['daily_return','daily_equty_curve']
        
        if self.save_results:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            totaltrade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_total_trade_detail.csv'))
            trade_df.to_csv(os.path.join(self.save_path, self.name_prefix + '_order_detail.csv'))
            daily_return.to_csv(os.path.join(self.save_path, self.name_prefix + '_daily_return.csv'))
            results.to_csv(os.path.join(self.save_path, self.name_prefix + '_results.csv'), encoding='gbk')
            totaltrade_df.set_index('create_time').change.cumsum().plot(figsize=(20, 10))
            plt.title('profit', fontsize='large')
            plt.savefig(os.path.join(self.save_path, self.name_prefix + '_profit.png'))
        
        return {'total_trade_detail':totaltrade_df, 'results':results, 'order_detail':trade_df, 'daily_return':daily_return}


import sys

sys.path.insert(4, '/data/user/015626/JupyterNotebooks/utils/')
from operators_wyc import *

sig = pd.read_pickle('/data/user/016700/Data/Sigs/2021_10/10s_results_continuous.pkl')
sig['ret'] = sig.vwap.shift(-2) / sig.vwap.shift(-1) - 1
sig['raw'] = ts_rank(sig['pred'], 1200)
# sig = sig.loc['20211027 101730':'20211027 101810']
# sig = sig.between_time('1322', '1340')

ts = TS_BACK_TEST(sig['raw'], in_t=0.8, submit_order_t=0.7, out_t=0.5, initial_cash=3.5e8, cash_divnum=10,
                  c_rate=3 / 100000, ticker='IC.CFE',
                  max_wait_tick_num=2, start_date=20210701, end_date=20210701,
                  tickslippage_dict={(0, 0.5): 10,
                                     (0.5, 0.7): 1.2,
                                     (0.7, 0.8): 0,
                                     (0.8, 0.9): 0,
                                     (0.9, 100): 0},
                  trade_start_time=[9, 30], trade_end_time=[14, 46],
                  save_results = True,
                  save_path='/data/user/015626/data/share/LOCAL_DATA/Mobius/test20220615',
                  name_prefix='test')
# finishdf = ts.back_test_singleday(20211021)
result = ts.back_test()