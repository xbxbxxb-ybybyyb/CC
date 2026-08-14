# coding: utf-8
# Author：fengchi863
# Date ：2020/6/9 13:05
'''
下单方案2：
首先根据交易量平分在当天的分钟上，每次必下单，下单价格根据信号来确定，
每次挂单1分钟，若没有成交，则继续追单5分钟（即4次），每次都根据当时的
信号确定下单价格。
'''
import itertools
import time

import numpy as np
import pandas as pd

from DataUtil import DataUtil
from IntradayBackTest.SignalBackTest import SignalBackTestBase
from System.ReadFileData import get_transaction_data, get_tick_data
from System.calc_order_transaction import order_transaction, generate_order_dict
from conf.path_config import *
from dataApi.getData import get_daily_1factor, get_date_range
from dataApi.stockList import trans_windcode2int
from dataApi.tradeDate import trade_minutes

EPOSILON = 1e-10


def reformate_id(df):
    if isinstance(df.index[0], tuple):
        df.index = [x[0] * 10000 + x[1] for x in df.index]
    df.index = pd.to_datetime(df.index.astype(str))
    df.columns = [str(stk).zfill(6) + '.SZ' if int(stk) < 400000 else str(stk) + '.SH' for stk in df.columns]


def get_deal_datetime(num_board_lot):
    partition = len(trade_minutes[:-30]) / num_board_lot
    if partition < 5:
        partition = 5
    return [trade_minutes[i * partition] for i in range(num_board_lot)]


def get_deal_change_point(change_point, num_board_lot):
    partition = abs(num_board_lot) / len(change_point)
    len_slice = len(change_point) / abs(num_board_lot)
    if partition >= 1:
        return change_point
    else:
        return [change_point[np.ceil(i * len_slice).astype(int)]
                for i in range(abs(num_board_lot))]


def get_progress_bar(change_point, num_board_lot, signal, finished_date_time):
    # every_point_vol = np.ceil(num_board_lot / len(change_point)) # floor
    # change_point_progress = [every_point_vol * (i + 1) for i in range(len(change_point))]
    # change_point_progress[-1] = num_board_lot
    # change_point_progress_dict = dict(zip(change_point, change_point_progress))
    # change_point_progress_series = pd.Series(change_point_progress_dict)
    # change_point_progress_series[finished_date_time] = num_board_lot
    # change_point_progress_series = change_point_progress_series.resample('1min', fill_method='ffill')
    target_piece = pd.Series([num_board_lot / 45] * 45, index=change_point)
    target_finished = target_piece.cumsum().apply(lambda x: round(x))
    target_finished = target_finished.reindex(signal.index).fillna(method='ffill')
    return target_finished * 100


def datetime_reindex(df):
    date_list = get_date_range(df.index[0][0], df.index[-1][0])
    datetime_list = list(itertools.product(date_list, trade_minutes))
    df = df.reindex(datetime_list)
    return df


def get_diff_datetime(dt1, dt2):
    return int(abs(dt1 - dt2).seconds / 60)


def get_good_price(signal, trade_direction, date_time, pankou_info, mk_data, stk_id):
    # if date_time.strftime('%Y%m%d') == '20180207' and stk_id == 688:
    #     print(1)
    tick_pankou_info = pankou_info.loc[date_time]

    if trade_direction is "B":
        if signal[date_time] == 1:
            price = mk_data.loc[date_time, 'close']  # 上一分钟收盘价
        else:
            if mk_data.loc[date_time, 'close'] < 10.0:
                price = tick_pankou_info['Buy1Price']
            elif 10.0 <= mk_data.loc[date_time, 'close'] < 20.0:
                price = tick_pankou_info['Buy2Price']
            else:
                price = tick_pankou_info['Buy3Price']

        if price == 0:  # 买入时涨停
            price = tick_pankou_info['Buy1Price']
        if tick_pankou_info['Buy1Price'] == 0:  # 买入时跌停
            price = tick_pankou_info['Sell1Price']

    elif trade_direction is "S":
        if signal[date_time] == 1:
            if mk_data.loc[date_time, 'close'] < 10.0:
                price = tick_pankou_info['Sell1Price']
            elif 10.0 <= mk_data.loc[date_time, 'close'] < 20.0:
                price = tick_pankou_info['Sell2Price']
            else:
                price = tick_pankou_info['Sell3Price']

        else:
            price = mk_data.loc[date_time, 'close']  # 上一分钟收盘价

        if price == 0:  # 卖出时跌停
            price = tick_pankou_info['Sell1Price']
        if tick_pankou_info['Sell1Price'] == 0:  # 卖出时涨停
            price = tick_pankou_info['Buy1Price']

    if np.isnan(price):
        print(date_time, stk_id, 'the price is NaN!')
    return price


class Signal1min(SignalBackTestBase):
    def __init__(self, start_date=20180101, end_date=20181231):
        super().__init__(start_date=start_date, end_date=end_date)
        self.change_point = [1 + 5 * i for i in range(45)]

    def calc_stk_day(self, stk_id, day, vol, mk_data, signal):
        stk_id = trans_windcode2int(stk_id)
        day = int(day.strftime('%Y%m%d'))
        tick_data = get_tick_data(stk_id, day)
        transaction_data = get_transaction_data(stk_id, day)
        pankou_info = pd.read_pickle(root_path + 'MinutelyTickByStock_from2017/%d.pkl' % stk_id).loc[
                      (day, 930):(day, 1500)]
        # pankou_info = pd.read_pickle(root_path + 'MinutelyTickByStock_from2017/%d.pkl' % 2555).loc[
        #               (20171016, 930):(20171016, 1500)]
        if isinstance(pankou_info.index[0], tuple):
            pankou_info.index = [x[0] * 10000 + x[1] for x in pankou_info.index]
        pankou_info.index = pd.to_datetime(pankou_info.index.astype(str))
        # spread = mk_data['high'] - mk_data['low']
        finished_vol = 0
        if vol > 0:
            trade_direction = 'B'
            signal[signal == 0] = 1
        else:
            trade_direction = 'S'
            signal[signal == 0] = -1
        abs_vol = abs(vol)
        record = []
        num_board_lot = int(round((abs_vol + EPOSILON) / 100))
        change_point = [signal.index[i] for i in self.change_point]
        # change_point = get_deal_change_point(change_point, num_board_lot)

        change_point_date_time = change_point[0]  # 设置第一次的触发时间
        finished_date_time = mk_data.index.tolist()[-1]

        # 平分到各个下单点
        change_point_progress_series = get_progress_bar(change_point, num_board_lot, signal, finished_date_time)
        trade_flag = False

        for idx, date_time in enumerate(signal.index[1:-5]):
            temp_vol = change_point_progress_series[date_time] - finished_vol

            if temp_vol >= 100 and date_time in change_point:
                change_point_date_time = date_time
                trade_flag = True

            # 条件1：如果该段时间的剩余待成交股数小于100股，不足1手，则暂停交易
            # 条件2：持续挂单5分钟，每五分钟判断一次
            if temp_vol < 100 or get_diff_datetime(date_time, change_point_date_time) >= 5:
                trade_flag = False

            if not trade_flag:
                continue

            temp_vol = round(temp_vol, -2)

            price = get_good_price(signal, trade_direction, date_time, pankou_info, mk_data, stk_id)
            order = generate_order_dict(stk_id, price, temp_vol, trade_direction, date_time, withdraw_seconds=59)
            try:
                true_price, available_vol = order_transaction(order, tick_data, transaction_data)
            except Exception as e:
                print(e)
                print(order)
            if np.isnan(available_vol):
                available_vol = 0
                true_price = 0
            record.append([date_time, trade_direction, vol, true_price, temp_vol, available_vol, finished_vol])
            finished_vol += available_vol

        if len(record) > 0:
            record = pd.DataFrame(record,
                                  columns=['datetime', 'trade_direction', 'vol', 'price', 'order_vol', 'available_vol',
                                           'finished_vol'])
            mean_price = (record['available_vol'] * record['price']).sum() / record['available_vol'].sum()
        else:
            mean_price = np.nan
        print(day, stk_id, trade_direction, ' | ', round(finished_vol / abs_vol, 2), ' | ', abs_vol - finished_vol,
              ' | ', mean_price)
        if trade_direction is 'S':
            finished_vol *= -1
        return finished_vol, mean_price, record


if __name__ == '__main__':
    position = 500000000
    signal1min_inst = Signal1min(start_date=20180103, end_date=20181231)

    signal_ = pd.read_pickle(
        junk_clf_path + 'predict_signal_xgb_20200609_rise_down_zero_1min.pkl')
    # predict_signal_lr_rise_down_zero_1min_from2017_selected50factor_20200611
    # predict_signal_xgb_20200609_rise_down_zero_1min

    cap_opt = pd.read_hdf(junk_clf_path + 'Portfolio.h5', 'Portfolio')
    cap_opt_diff = cap_opt.diff()
    daily_close = get_daily_1factor('close', date_list=cap_opt.index.tolist(),
                                    code_list=cap_opt.columns.tolist())

    mkt_cap_opt = (cap_opt * daily_close).sum(axis=1)
    target_vol = (cap_opt_diff.T * position / mkt_cap_opt).T
    target_vol = round(target_vol, -2)
    # test one stock
    # signal_ = signal_.loc[(20180125,925):(20180125,1500)]['603990'].to_frame()
    # target_vol = pd.DataFrame(target_vol.loc[20180125, 603990], index=[20180125], columns=[603990])

    signal1min_inst.reformate_id(signal_)
    signal1min_inst.reformate_id(target_vol)

    e1 = time.time()
    avg_price, deal_vol, record_dict = signal1min_inst.backtest(signal_, target_vol, 20)
    fulfill_percent, out_performance = signal1min_inst.calc_performance(signal_, target_vol, avg_price, deal_vol)
    DataUtil.save_pkl(junk_clf_path + 'fengchi/', 'Signal1min_xgboost_v3_20200701.pkl',
                      avg_price=avg_price, deal_vol=deal_vol, record_dict=record_dict,
                      fulfill_percent=fulfill_percent, out_performance=out_performance)
    print('total backtest time: ' + str(time.time() - e1))
