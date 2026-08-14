# @Time : 2020/5/27 18:06
# @Author : Zhichen Lu
# @File : simulate_by_wrong_rate.py
"""
根据给定错误率随机生成信号
"""
import copy
import random

from backtest.OrderBackTest import *


def get_random_wrong_df(signal_df, wrong_rate):
    signal = copy.deepcopy(signal_df)
    for col in signal.columns:
        signal[col] = get_random_wrong_label(signal[col], wrong_rate)
        # print(col,(signal[col]==signal_df[col]).sum()/signal_df[col].count())
    return signal


def get_random_wrong_label(signal_series, wrong_rate):
    rise_down_index = signal_series[signal_series.isin([-1, 1])].index.tolist()
    zero_index = signal_series[signal_series == 0].index.tolist()
    wrong_rise_down = random.sample(rise_down_index, int(len(rise_down_index) * wrong_rate))
    signal_series.loc[wrong_rise_down] = signal_series.loc[wrong_rise_down] * -1
    wrong_zero = random.sample(zero_index, int(len(zero_index) * wrong_rate))
    wrong_zero_value = [1 for i in range(int(len(wrong_zero) / 2))] + [-1 for i in range(len(wrong_zero) - int(len(wrong_zero) / 2))]
    random.shuffle(wrong_zero_value)
    signal_series.loc[wrong_zero] = wrong_zero_value
    return signal_series


def main_2(wrong_rate):
    IBT = IntradayBackTest()
    close = arr2frame(IBT.close, IBT.index, IBT.columns)  # get_minute_1factor('close', start_datetime=201701030925, end_datetime=201912311500, code_list=TBT.p.columns.tolist())
    close[:242]
    time_list = [x[1] for x in close.index.tolist()[:242]]
    date_list = get_date_range(20170103, 20191231)
    n = 5

    close_arr = frame2arr(close)
    future_5m_twap = shift_back(ts_mean(close_arr, n), n)
    daily_twap = get_daily_1factor('twap', date_list=date_list, code_list=close.columns.tolist())
    daily_twap_arr = daily_twap.values
    # future_5m_pct = daily_twap_arr / close_arr - 1
    future_5m_pct = shift_back(close_arr, n) / close_arr - 1
    future_5m_pct[(future_5m_pct == np.inf) | (future_5m_pct == -np.inf)] = np.nan
    future_5m_pct[np.isnan(future_5m_pct)] = 100
    future_5m_pct[(future_5m_pct > 0)] = 1
    future_5m_pct[future_5m_pct < 0] = -1

    signal = arr2frame(future_5m_pct, index=IBT.index, columns=IBT.columns)
    IBT.calc_deal_price_3(signal, 0.0005, 'B')
    # hs300_weight = pd.read_hdf('/data/group/800319/junkData/daily/HS300_exdiv_weight.h5', 'HS300_exdiv_weight').loc[20170103:20191231]
    # isin = hs300_weight.sum()
    # isin = isin[isin>0]
    # hs300_weight = hs300_weight[isin.index]
    # signal_random_wrong = get_random_wrong_df(signal[hs300_weight.columns],wrong_rate)

    # buy_improve, sell_improve = IBT.run_backtest(signal, hs300_weight, hs300_weight, 0.0005)
    # pd.to_pickle([buy_improve, sell_improve],'/data/group/800319/junkData/IntraFactorModel/random_wrong/wrong_rate%s.pkl'%str(wrong_rate))
    # print(wrong_rate, 'done')