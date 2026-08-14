# @Time : 2020/6/9 8:41
# @Author : Zhichen Lu
# @File : Signal5min.py
import datetime
import itertools
import os

import numpy as np
import pandas as pd

from SignalBackTest import SignalBackTestBase
from System.calc_order_transaction import order_transaction
from dataApi.getData import get_daily_1factor, get_date_range
from dataApi.tradeDate import trade_minutes


class Signal5min(SignalBackTestBase):

    def __init__(self):
        super().__init__()
        self.change_point = [1 + 5 * i for i in range(43)]

    def calc_stk_day(self, stk_id, date, vol, mk_data, signal):
        # spread = mk_data['high'] - mk_data['low']
        finished_vol = 0
        if vol > 0:
            sign = 1
            signal[signal == 0] = 1
        else:
            sign = -1
            signal[signal == 0] = -1
        signal = sign * signal
        vol = abs(vol)
        record = []
        change_point = [signal.index[i] for i in self.change_point]
        trade_flag = False
        # 计算每分钟上所需要完成的数量
        target_piece = pd.Series([vol / 43 for i in range(43)], index=change_point)
        target_finished = target_piece.cumsum().apply(lambda x: round(x, -2))
        target_finished = target_finished.reindex(signal.index).fillna(method='pad').fillna(0)
        for idx, date_time in enumerate(signal.index[:-30]):
            if finished_vol > vol:
                raise Exception('Bought more than wanted')
            if finished_vol == vol:
                break
            temp_vol = target_finished.loc[date_time] - finished_vol
            if temp_vol == 0:
                trade_flag = False
                continue
            if date_time in change_point:
                if signal.loc[date_time] == 1:
                    trade_flag = True
                    signal_time = date_time
                    signal_base_price = mk_data.loc[signal_time, 'close']
                    signal_future_price = mk_data.shift(-5).loc[signal_time, 'close']
                elif signal.loc[date_time] == -1:
                    trade_flag = False
                else:
                    pass
            if not trade_flag:
                continue
            order = {'stk_id': int(stk_id[:-3]), 'price': mk_data.loc[date_time, 'close'], 'volume': temp_vol, 'start_time': date_time,
                     'withdraw_time': datetime.timedelta(seconds=59), 'direction': {1: 'B', -1: 'S'}[sign]}
            deal_price, dealed_vol = order_transaction(order)  # self.get_available_vol(mk_data.loc[date_time, 'close'], date_time, mk_data, spread, {1: 'B', -1: 'S'}[sign])
            # dealed_vol = min(available_vol, temp_vol) if not np.isnan(available_vol) and not np.isnan(temp_vol) else 0
            finished_vol += dealed_vol if not np.isnan(dealed_vol) else 0
            # record.append([date_time, dealed_vol * sign, mk_data.loc[date_time, 'close'],deal_price, finished_vol * sign])
            record.append([date_time, dealed_vol * sign, mk_data.loc[date_time, 'close'], deal_price, finished_vol * sign, signal_time, signal_base_price, signal_future_price])
        if len(record) > 0:
            # record = pd.DataFrame(record, columns=['datetime', 'vol', 'order_price','deal_price', 'finished_vol'])
            record = pd.DataFrame(record, columns=['datetime', 'vol', 'order_price', 'deal_price', 'finished_vol', 'signal_time', 'signal_base_price', 'signal_future_price'])
            mean_price = (record['vol'].apply(abs) * record['deal_price']).sum() / record['vol'].apply(abs).sum()
        else:
            mean_price = np.nan
        return finished_vol * sign, mean_price, record


def reformate_id(df):
    if isinstance(df.index[0], tuple):
        df.index = [x[0] * 10000 + x[1] for x in df.index]
    df.index = pd.to_datetime(df.index.astype(str))
    if isinstance(df, pd.DataFrame):
        df.columns = [str(stk).zfill(6) + '.SZ' if int(stk) < 400000 else str(stk) + '.SH' for stk in df.columns]


def datetime_reindex(df):
    date_list = get_date_range(df.index[0][0], df.index[-1][0])
    datetime_list = list(itertools.product(date_list, trade_minutes))
    df = df.reindex(datetime_list)
    return df



def main():
    out_path = '/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable_mocker/'
    if not os.path.exists(out_path):
        os.mkdir(out_path)
    position = 200000000
    SBTB = Signal5min()
    flag = '_2018'
    wgt_opt_diff = pd.read_hdf('/data/group/800319/junkClassification/wgt_opt_diff.h5', 'wgt_opt_diff')
    # wgt_opt_diff[abs(wgt_opt_diff)<0.000001]
    signal_ = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/junkClassification/predict_signal_lr_20200529_rise_down_zero.pkl')
    daily_close = get_daily_1factor('close', date_list=wgt_opt_diff.index.tolist(), code_list=wgt_opt_diff.columns.tolist())
    target_vol = wgt_opt_diff * position / daily_close.shift(1)
    target_vol = round(target_vol, -2)
    signal_ = datetime_reindex(signal_)
    print(signal_.shape)
    reformate_id(signal_)
    reformate_id(target_vol)
    import time
    e = time.time()
    avg_price, deal_vol, record = SBTB.backtest(signal_.loc['20180101':'20181231'], target_vol.loc['20180101':'20181231'], kernal_num=20)
    print(time.time() - e)
    pd.to_pickle([avg_price, deal_vol],
                 out_path + 'backtest_res_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200630.pkl' % flag)
    pd.to_pickle(record, out_path + 'record_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200630.pkl' % flag)
    # avg_price, deal_vol = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable/backtest_res_mlp_signal.pkl')
    # fulfill_percent, outperformance = SBTB.calc_performance(signal_, target_vol, avg_price, deal_vol)
    #############

    fulfill_percent, outperformance = SBTB.calc_performance(signal_, target_vol, avg_price, deal_vol)
    pd.to_pickle([fulfill_percent, outperformance], out_path + 'backtest_performance_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200630.pkl' % flag)
    outperformance_all = (outperformance['buy'].sum(axis=1).shift(1) + outperformance['sell'].sum(axis=1)) / 200000000
    # fulfill_percent, outperformance = pd.read_pickle(out_path+'backtest_performance_mlp.pkl')
    # fulfill_accurate, outperformance_accurate = pd.read_pickle('/data/group/800319/junkData/IntraFactorModel/junkClassification/temp_variable/backtest_performance_mlp_signal.pkl')
    # fulfill_all = fulfill_accurate['all']
    # outperformance_all = (outperformance_accurate['buy'].sum(axis=1).shift(1) + outperformance_accurate['sell'].sum(axis=1)) / 200000000
    print(outperformance_all.cumsum())
    pd.to_pickle(outperformance_all, out_path + 'improve_lr_rise_down_zero_5min%s_all_factor_fillnapad_20200630.pkl' % flag)

    # fulfill_percent, outperformance = pd.read_pickle(out_path + 'backtest_performance_lr_rise_down_zero_5min_201801_all_factor_fillnapad_20200629.pkl')
    # buy = outperformance['buy']/position
    # buy.min(axis=1)
    # sell = outperformance['sell']/position
    # sell.max(axis=1).sort_values()
    # sell.min(axis=1)
    """
    fulfill_percent, outperformance = pd.read_pickle(out_path + 'backtest_performance_lr_rise_down_zero_5min_from2017_selected50factor_20200611.pkl')
    outperformance_all = (outperformance['buy'].sum(axis=1).shift(1) + outperformance['sell'].sum(axis=1)) / 200000000
    pd.to_pickle(outperformance_all, out_path + 'improve_lr_50_factor.pkl')
    outperformance_all = pd.read_pickle(out_path + 'improve_mlp_all_factor.pkl')
    val_b = pd.read_hdf('/data/group/800319/junkClassification/val_b.h5', 'val_b')
    val_g = pd.read_hdf('/data/group/800319/junkClassification/val_g.h5', 'val_g')
    reformate_id(val_b)
    reformate_id(val_g)
    with_intraday = (1 + (val_g.pct_change() + outperformance_all).loc[outperformance_all.index]).cumprod()[1:]
    (with_intraday - val_g.loc[with_intraday.index] / val_g.loc[with_intraday.index].tolist()[0]).loc[:'20181231']  # - val_b.loc[with_intraday.index]/val_b.loc[with_intraday.index].tolist()[0]

    """


if __name__ == "__main__":
    main()
# from dataApi.getData import get_minute_1stock
# check = get_minute_1stock(code=415,start_datetime=201707040925,end_datetime=201707041500,factor_list=['close','high','low','open','vol'])
