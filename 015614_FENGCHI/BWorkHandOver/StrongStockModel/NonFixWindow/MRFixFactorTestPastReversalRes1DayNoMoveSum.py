# @Time : 2021/9/27 14:08
# @Author : Zhichen Lu
# @File : MRFixFactorTestRutine.py
import sys

sys.path.extend(
    ['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python',
     '/data/user/015664/TriggeredTrading/StrongStockModel',
     '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
     '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
     '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training',
     '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes, get_sub_date_index, \
    get_desample_minute_dict, get_trade_date_interval, get_recent_trade_date
from dataApi.getData import get_daily_1factor
from dataApi.stockList import clean_stock_list, trans_windcode2int
import numpy as np
import pandas as pd
import bottleneck
import gc
# from dataApi.usefulTools import delay
def fill_nan(arr, l):
    return np.pad(arr, ((l,0),), mode='constant', constant_values=np.nan)

def delay(arr, l=1):
    return fill_nan(arr[:-l], l)

class ArrReshape(object):

    def to2d(self, arr):
        self.freq = arr.shape[1]
        if arr.dtype == np.float:
            arr = np.round(arr, 8)
        return arr.reshape(arr.shape[0] * arr.shape[1], arr.shape[2])

    def to3d(self, arr):
        if arr.dtype == np.float:
            arr = np.round(arr, 8)
        return arr.reshape(arr.shape[0] // self.freq, self.freq, arr.shape[1])

def no_rolling_move_sum_1d_arr(arr,l):
    delay_arr = [arr[None,:]]
    for i in range(1,l):
        delay_arr.append(delay(arr,i)[None,:])
    delay_arr = np.concatenate(delay_arr,axis=0)
    return delay_arr.sum(axis=0)

def dt_beta2(x, y, m3):
    x = x.copy()
    y = y.copy()
    shape = x.shape
    ar = ArrReshape()
    x = ar.to2d(x)
    y = ar.to2d(y)
    f = np.isfinite(x) & np.isfinite(y)
    x[~ f] = 0
    y[~ f] = 0
    cx = no_rolling_move_sum_1d_arr(x.sum(axis=1), m3)
    cy = no_rolling_move_sum_1d_arr(y.sum(axis=1), m3)
    cx2 = no_rolling_move_sum_1d_arr((x ** 2).sum(axis=1), m3)
    cxy = no_rolling_move_sum_1d_arr((x * y).sum(axis=1), m3)
    cn = no_rolling_move_sum_1d_arr((f.astype('float32')).sum(axis=1), m3)

    # cx = bottleneck.move_sum(x.sum(axis=1), m3, axis=0)
    # cy = bottleneck.move_sum(y.sum(axis=1), m3, axis=0)
    # cx2 = bottleneck.move_sum((x ** 2).sum(axis=1), m3, axis=0)
    # cxy = bottleneck.move_sum((x * y).sum(axis=1), m3, axis=0)
    # cn = bottleneck.move_sum((f.astype('float32')).sum(axis=1), m3, axis=0)
    a = (cn * cxy - cx * cy)
    b = (cn * cx2 - cx ** 2)
    beta = a / b  # np.divide(a, b, out=np.full(x.shape, np.nan), where=abs(b) > 1e-8)
    beta[cn < m3 / 2] = np.nan
    # beta = ar.to3d(beta)
    alpha = cy / cn - cx * beta / cn
    return alpha.reshape(shape[:2]), beta.reshape(shape[:2])


def find_trade_min(sign_min, delay_min=1, order_keep_min=5):
    sign_min = sign_min if sign_min < 242 else trade_minutes.index(sign_min)
    trade_min = [sign_min + delay_min + x for x in range(order_keep_min)]
    if trade_min[0] >= 241:
        trade_min = [242]
    elif trade_min[-1] >= 238:
        trade_min = list(range(min(trade_min[0], 238), 242))
    if len(trade_min) > order_keep_min:
        trade_min = trade_min[:order_keep_min - 1] + [241]
    elif trade_min == [242]:
        trade_min = [242] * order_keep_min
    elif len(trade_min) < order_keep_min:
        trade_min = trade_min + [241] * (order_keep_min - len(trade_min))
    return trade_min


def get_minute_pickle(factor, date_list, code_list=None,
                      address='/data/group/800080/PanelMinDataForZT/stock/', type='stock'):
    if type == 'bench':
        address = address + '/../index/'

    start_date = date_list[0]
    end_date = date_list[-1]

    month_list = sorted(list(set(get_date_range(start_date, end_date, 'M') + [end_date])))
    short_month_list = sorted(list({x // 100 for x in month_list}))
    month_start = get_recent_trade_date(short_month_list[0] * 100)
    month_end = get_recent_trade_date(short_month_list[-1] * 100)

    start_keep = get_trade_date_interval(start_date, month_start) * 242
    end_keep = (get_trade_date_interval(end_date, month_end) + 1) * 242
    df_list = [pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, x, factor)) for x in short_month_list]
    df_list[-1] = df_list[-1].iloc[:end_keep] if len(month_list) > 1 else df_list[-1].iloc[start_keep: end_keep]
    df_list[0] = df_list[0].iloc[start_keep:] if len(month_list) > 1 else df_list[0]

    df = pd.concat(df_list)
    df.columns = df.columns.map(trans_windcode2int)
    df = df.reindex(columns=code_list)
    df.index = pd.MultiIndex.from_product([date_list, trade_minutes])
    return df


def stats_range(date_index, date_list):
    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end


def calc_corr(x, y, x2, y2, xy, n):
    corr = (xy - x * y / n) / ((x2 - x ** 2 / n) * (y2 - y ** 2 / n)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    corr = np.where(n >= 4, corr, np.nan)
    corr = corr if corr.size > 1 else corr.item()
    return corr


def get_stock_pool(test_date_list, stock_list='ALL', no_ST=True, least_live_days=240, no_pause=True,
                   least_recover_days=1, no_pause_limit=0.5, no_pause_stats_days=120, no_limit_up=False,
                   no_limit_down=False, other_limit=None):
    stock_pool = clean_stock_list(stock_list=stock_list, no_ST=no_ST, least_live_days=least_live_days,
                                  no_pause=no_pause, least_recover_days=least_recover_days,
                                  no_pause_limit=no_pause_limit, no_pause_stats_days=no_pause_stats_days,
                                  no_limit_up=no_limit_up, no_limit_down=no_limit_down,
                                  other_limit=other_limit, trade_mode=True,
                                  start_date=test_date_list[0], end_date=test_date_list[-1])
    stock_pool = stock_pool > 0.5
    return stock_pool


def get_future(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=5):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_end_date = get_pre_trade_date(test_date_list[-1], - future_days)
    future_date_list = get_date_range(test_date_list[0], future_end_date)
    future = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    future = np.nanmean(future.values[idx], axis=2)
    future = future[future_days: test_date_num + future_days] / future[:test_date_num] - 1
    future = future.transpose(0, 2, 1)
    return future

def get_recent_pct_change(test_date_list, code_list, future_days=1, delay_min=1, order_keep_min=5):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_start_date = get_pre_trade_date(test_date_list[0], future_days)
    future_date_list = get_date_range(future_start_date,test_date_list[-1])
    future = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    future = np.nanmean(future.values[idx], axis=2)
    future = future[future_days:test_date_num+future_days]/future[: test_date_num ]  - 1
    future = future.transpose(0, 2, 1)
    return future

# from dataApi.stockList import get_all_stock_ever_appear
# dt_list = get_date_range(20210101,20210131)
# code_list = get_all_stock_ever_appear(dt_list[-1])
# future = get_future(dt_list,code_list=code_list)
# recent_pct_change = get_recent_pct_change(dt_list,code_list=code_list)



def get_nolimit(test_date_list, code_list):
    period_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    nolimit = get_minute_pickle('limit_status', test_date_list, code_list).values == 0
    nolimit = nolimit.reshape(len(test_date_list), 242, len(code_list))[
              :, [trade_minutes.index(x) for x in period_list]]
    nolimit = nolimit.transpose(0, 2, 1)
    return nolimit


def get_std_factor(factor, standardize_days=40, freq=7, test_drop_days=40):
    factor_finite = np.isfinite(factor)

    factor[~ factor_finite] = 0
    factor2 = factor ** 2

    d_cf = factor.sum(axis=1)
    d_cf2 = factor2.sum(axis=1)
    d_cn = factor_finite.sum(axis=1)

    rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
        d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
        d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

    rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
        d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
        d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

    rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
        d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
        d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

    rd_cn[rd_cn < standardize_days * freq / 2] = np.nan
    factor[~ factor_finite] = np.nan

    rd_mean = (rd_cf / rd_cn)[test_drop_days - standardize_days: -1]
    rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[test_drop_days - standardize_days: -1]
    rd_std[rd_std == 0] = np.nan

    factor = (factor[test_drop_days:] - rd_mean[:, None]) / rd_std[:, None]
    factor = factor.clip(-6, 6)
    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0

    del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn
    gc.collect()

    return factor, rd_mean, rd_std


def _get_future_by_30min(test_date_list, code_list, future_bar=1, delay_min=1, order_keep_min=30):
    period_list = [930, 1000, 1030, 1100, 1300, 1330, 1400, 1430]
    future_end_date = get_pre_trade_date(test_date_list[-1], - 1)
    future_date_list = get_date_range(test_date_list[0], future_end_date)
    close_badj = get_minute_pickle('close_adj', future_date_list, code_list)
    test_date_num = len(test_date_list)
    idx = np.arange(test_date_num + 1)[:, None, None] * 242 + np.asanyarray([find_trade_min(
        x, delay_min, order_keep_min) for x in period_list])[None, :, :]
    # idx = np.arange(test_date_num + future_days)[:, None, None] * 242 + np.array([[31]])[None, :, :]
    close_badj = np.nanmean(close_badj.values[idx], axis=2)
    close_badj_append = np.concatenate([close_badj[:-1], close_badj[1:]], axis=1)
    future = close_badj_append[:, future_bar:len(period_list) + future_bar, :] / close_badj_append[:, :len(period_list), :] - 1
    return future[:, 1:, :], future_date_list

class MRFixFactorTest(object):

    def __init__(self, calc_start_date=20140601, test_start_date=20140801, end_date=20210531, freq=7, seed=722):

        end_date = get_recent_trade_date(get_pre_trade_date(end_date, 2, dividing_point=18), 'M')

        period = 1 if freq == 242 else (30 if freq == 7 else 240 // freq)
        period_list = sorted(list(set(get_desample_minute_dict(
            period).values()))) if period > 1 else trade_minutes
        period_list = period_list[:-1] if freq == 7 else period_list
        period_num = len(period_list)

        test_date_list = get_date_range(test_start_date, end_date)
        calc_date_list = get_date_range(calc_start_date, end_date)
        test_start_date = test_date_list[0]
        calc_start_date = calc_date_list[0]
        end_date = test_date_list[-1]
        test_date_num = len(test_date_list)
        calc_date_num = len(calc_date_list)
        test_drop_days = calc_date_num - test_date_num

        self.freq = freq
        self.period = period
        self.period_list = period_list
        self.period_num = period_num
        self.test_date_list = test_date_list
        self.calc_date_list = calc_date_list
        self.test_start_date = test_start_date
        self.calc_start_date = calc_start_date
        self.test_date_num = test_date_num
        self.calc_date_num = calc_date_num
        self.test_drop_days = test_drop_days
        self.end_date = end_date
        self.seed = seed

    def set_stock_pool(self, stock_pool_name=None, stock_list='ALL', no_ST=True,
                       least_live_days=240, no_pause=True, least_recover_days=1, no_pause_limit=0.5,
                       no_pause_stats_days=120, no_limit_up=False, no_limit_down=False, other_limit=None,
                       stock_pool_address='/data/group/800442/800319/TrueSendStrategy/'):

        if stock_pool_name:
            stock_pool = get_daily_1factor(stock_pool_name, date_list=self.test_date_list,
                                           diy_address=stock_pool_address) > 0.5
            code_list = stock_pool.sum(axis=0) > 0.5
            code_list = sorted(code_list[code_list].index.to_list())
            stock_pool = stock_pool.reindex(columns=code_list)
        else:
            stock_pool = clean_stock_list(stock_list=stock_list, no_ST=no_ST, least_live_days=least_live_days,
                                          no_pause=no_pause, least_recover_days=least_recover_days,
                                          no_pause_limit=no_pause_limit, no_pause_stats_days=no_pause_stats_days,
                                          no_limit_up=no_limit_up, no_limit_down=no_limit_down,
                                          other_limit=other_limit, trade_mode=True,
                                          start_date=self.test_start_date, end_date=self.end_date)
            stock_pool = stock_pool > 0.5
            code_list = stock_pool.columns.to_list()

        stock_pool = stock_pool.values
        valid_daily_num = stock_pool.sum(axis=1)
        code_num = len(code_list)
        pool_d = stock_pool.sum(axis=1) * self.period_num

        sample = np.arange(stock_pool.flatten().shape[0])[stock_pool.flatten()]
        random_state = np.random.RandomState(self.seed)
        sample = sample[random_state.choice(sample.shape[0], 3000, replace=False)]

        self.valid_daily_num = valid_daily_num
        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.pool_d = pool_d
        self.sample = sample

        if hasattr(self, 'future_days'):
            self.set_future(self.future_days, self.delay_min, self.order_keep_min)

    def set_future_by_30min(self,future_bar,delay_min=1, order_keep_min=30):

        future,future_date_list = _get_future_by_30min(self.test_date_list,
            self.code_list,future_bar=future_bar,delay_min=delay_min,order_keep_min=order_keep_min)
        nolimit = get_minute_pickle('limit_status', future_date_list, self.code_list) == 0
        nolimit = nolimit.values.reshape(len(future_date_list), 242, len(self.code_list))[
                  :- 1, [trade_minutes.index(x) for x in self.period_list]]
        future_finite = np.isfinite(future) & self.stock_pool[:, None, :] & nolimit
        future2 = future.copy()
        future2[~ future_finite] = 0
        self.future = future
        self.future2 = future2
        self.future_finite = future_finite
        self.nolimit = nolimit
        self.future_bars = future_bar
        self.delay_min = delay_min
        self.order_keep_min = order_keep_min


    def set_future_old(self, future_days=1, delay_min=1, order_keep_min=30):

        future_end_date = get_pre_trade_date(self.end_date, - future_days - 1)
        future_date_list = get_date_range(self.test_start_date, future_end_date)
        future = get_minute_pickle('close_adj', future_date_list, self.code_list)
        idx = np.arange(self.test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
            x, delay_min, order_keep_min) for x in self.period_list])[None, :, :]
        future = np.nanmean(future.values[idx], axis=2)
        future = future[future_days: self.test_date_num + future_days] / future[:self.test_date_num] - 1

        nolimit = get_minute_pickle('limit_status', future_date_list, self.code_list) == 0
        nolimit = nolimit.values.reshape(len(future_date_list), 242, len(self.code_list))[
                  :- future_days - 1, [trade_minutes.index(x) for x in self.period_list]]
        future_finite = np.isfinite(future) & self.stock_pool[:, None, :] & nolimit
        future2 = future.copy()
        future2[~ future_finite] = 0

        self.future = future
        self.future2 = future2
        self.future_finite = future_finite
        self.nolimit = nolimit
        self.future_days = future_days
        self.delay_min = delay_min
        self.order_keep_min = order_keep_min

    def set_recent_pct_change(self, future_days=1, delay_min=-5, order_keep_min=5):

        recent_pct, _ = _get_future_by_30min(self.test_date_list,
            self.code_list, future_bar=8, delay_min=delay_min, order_keep_min=order_keep_min)
        recent_pct = np.pad(recent_pct[:-1,:,:],((1,0),(0,0),(0,0)),mode='constant',constant_values=np.nan)
        # return  future
        self.recent_pct_change = recent_pct
        self.recent_pct_change_days = future_days
        self.rct_delay_min = delay_min
        self.rct_order_keep_min = order_keep_min

    def test_factor(self, factor, standardize_days=40,reg_days=40, move_window=12,test_return=False,
                    top_tiles=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)):

        factor_finite = np.isfinite(factor)

        if standardize_days:
            factor[~ factor_finite] = 0
            factor2 = factor ** 2

            d_cf = factor.sum(axis=1)
            d_cf2 = factor2.sum(axis=1)
            d_cn = factor_finite.sum(axis=1)

            rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
                d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
                d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

            rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
                d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
                d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

            rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
                d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
                d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

            rd_cn[rd_cn < standardize_days * self.freq / 2] = np.nan
            factor[~ factor_finite] = np.nan

            rd_mean = (rd_cf / rd_cn)[self.test_drop_days - standardize_days: -1]
            rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[self.test_drop_days - standardize_days: -1]
            rd_std[rd_std == 0] = np.nan

            factor = (factor[self.test_drop_days:] - rd_mean[:, None]) / rd_std[:, None]
            factor = factor.clip(-6, 6)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn
            if reg_days:
                al,be = dt_beta2(factor,self.recent_pct_change,reg_days*7)
                factor = self.recent_pct_change - al[:,:,None] - be[:,:,None] *factor
            if test_return:
                return {},factor
        else:
            factor = factor[self.test_drop_days:]
            factor_finite = factor_finite[self.test_drop_days:]
            factor[~ factor_finite] = 0

        factor2 = factor.copy()
        factor_sample = factor[:, 0].flatten()[self.sample]
        month_split = get_sub_date_index(self.test_date_list, 'M')
        start_dates, end_dates = stats_range(month_split, self.test_date_list)

        def reduce_sum(arr, axis=0, keep_axis=()):

            keep_axis = (keep_axis,) if isinstance(keep_axis, int) else keep_axis
            left_axis = tuple(sorted(list(set(range(arr.ndim)) - {axis} - set(keep_axis))))
            if left_axis:
                arr = arr.sum(axis=left_axis)
            axis = np.searchsorted(keep_axis, axis)
            arr1 = np.add.reduceat(arr, month_split, axis=axis)
            return arr1

        def roll_sum(arr, axis=0, keep_axis=()):

            arr1 = reduce_sum(arr, axis=axis, keep_axis=keep_axis)
            keep_axis = (keep_axis,) if isinstance(keep_axis, int) else keep_axis
            axis = np.searchsorted(keep_axis, axis)
            arr1 = bottleneck.move_sum(arr1, window=move_window, axis=axis)
            return arr1

        def reduce_mean(arr, axis=0, keep_axis=()):

            finite = np.isfinite(arr)
            arr[~ finite] = 0
            arr1 = reduce_sum(arr, axis=axis, keep_axis=keep_axis)
            finite1 = reduce_sum(finite, axis=axis, keep_axis=keep_axis)
            mean = arr1 / finite1
            mean[~ np.isfinite(arr1)] = np.nan
            return mean

        def roll_mean(arr, axis=0, keep_axis=()):

            finite = np.isfinite(arr)
            arr[~ finite] = 0
            arr1 = roll_sum(arr, axis=axis, keep_axis=keep_axis)
            finite1 = roll_sum(finite, axis=axis, keep_axis=keep_axis)
            mean = arr1 / finite1
            mean[~ np.isfinite(arr1)] = np.nan
            return mean

        factor_complete = roll_sum(factor_finite & self.future_finite) / roll_sum(self.future_finite)

        x = factor2
        y = self.future2
        n = self.future_finite
        x[~ n] = 0
        x2 = x ** 2
        y2 = y ** 2
        xy = x * y

        c2x = x.sum(axis=2)
        c2y = y.sum(axis=2)
        c2x2 = x2.sum(axis=2)
        c2y2 = y2.sum(axis=2)
        c2xy = xy.sum(axis=2)
        c2n = n.sum(axis=2)

        ic_c = roll_mean(calc_corr(c2x, c2y, c2x2, c2y2, c2xy, c2n))
        ic_tc = roll_mean(calc_corr(c2x.sum(axis=1), c2y.sum(axis=1), c2x2.sum(axis=1),
                                    c2y2.sum(axis=1), c2xy.sum(axis=1), c2n.sum(axis=1)))

        ic_dc = np.nanmean(calc_corr(roll_sum(c2x, keep_axis=1), roll_sum(c2y, keep_axis=1),
                                     roll_sum(c2x2, keep_axis=1), roll_sum(c2y2, keep_axis=1),
                                     roll_sum(c2xy, keep_axis=1), roll_sum(c2n, keep_axis=1)), axis=1)

        ic_dtc = calc_corr(roll_sum(c2x), roll_sum(c2y), roll_sum(c2x2),
                           roll_sum(c2y2), roll_sum(c2xy), roll_sum(c2n))

        t2x = x.sum(axis=1)
        t2y = y.sum(axis=1)
        t2x2 = x2.sum(axis=1)
        t2y2 = y2.sum(axis=1)
        t2xy = xy.sum(axis=1)
        t2n = n.sum(axis=1)

        ic_t = roll_mean(calc_corr(t2x, t2y, t2x2, t2y2, t2xy, t2n))

        ic_dt = np.nanmean(calc_corr(roll_sum(t2x, keep_axis=1), roll_sum(t2y, keep_axis=1),
                                     roll_sum(t2x2, keep_axis=1), roll_sum(t2y2, keep_axis=1),
                                     roll_sum(t2xy, keep_axis=1), roll_sum(t2n, keep_axis=1)), axis=1)

        ic_d = np.nanmean(calc_corr(roll_sum(x, keep_axis=(1, 2)), roll_sum(y, keep_axis=(1, 2)),
                                    roll_sum(x2, keep_axis=(1, 2)), roll_sum(y2, keep_axis=(1, 2)),
                                    roll_sum(xy, keep_axis=(1, 2)), roll_sum(n, keep_axis=(1, 2))), axis=(1, 2))

        ic_direction = 2 * (ic_dt > 0) - 1
        ic_dtc *= ic_direction
        ic_dt *= ic_direction
        ic_tc *= ic_direction
        ic_dc *= ic_direction
        ic_d *= ic_direction
        ic_t *= ic_direction
        ic_c *= ic_direction

        # finite = factor_finite & self.future_finite
        # finite_m = reduce_sum(finite)
        # pool_len = finite_m.max()
        # months = len(start_dates)
        # data = np.full((months, pool_len), np.nan)
        # ret = np.full((months, pool_len), np.nan)
        # choose = np.arange(pool_len)[None, :] < finite_m[:, None]
        # data[choose] = factor2[finite]
        # ret[choose] = self.future[finite]
        # t_tiles = sorted(list(top_tiles))
        # tb_tiles = sorted(t_tiles + [100 - x for x in top_tiles])
        # tiles = np.nanquantile(data, [x / 100 for x in tb_tiles], axis=1)
        # tiles_low = tiles[:len(t_tiles)]
        # tiles_high = tiles[-1:-len(t_tiles)-1:-1]
        # ret_low = np.r_['0,2', tuple(np.nanmean(np.ma.array(ret, mask=data>tiles_low[x, :, None]), axis=1)
        #                              for x in range(len(t_tiles)))]
        # ret_high = np.r_['0,2', tuple(np.nanmean(np.ma.array(ret, mask=data<tiles_high[x, :, None]), axis=1)
        #                              for x in range(len(t_tiles)))]
        #
        result_ic = dict(
            factor_sample=factor_sample,
            start_dates=start_dates[move_window - 1:],
            end_dates=end_dates[move_window - 1:],
            factor_complete=factor_complete[move_window - 1:],
            ic_direction=ic_direction[move_window - 1:],
            ic_dtc=ic_dtc[move_window - 1:],
            ic_dt=ic_dt[move_window - 1:],
            ic_tc=ic_tc[move_window - 1:],
            ic_dc=ic_dc[move_window - 1:],
            ic_d=ic_d[move_window - 1:],
            ic_t=ic_t[move_window - 1:],
            ic_c=ic_c[move_window - 1:],
        )

        # result_ret = dict(
        #     start_dates=start_dates,
        #     end_dates=end_dates,
        #     t_tiles=t_tiles,
        #     tiles_low=tiles_low,
        #     tiles_high=tiles_high,
        #     ret_low=ret_low,
        #     ret_high=ret_high,
        # )
        return result_ic,factor


if __name__ == '__main__':

    import dask
    import time
    import os
    import re


    def multidask(lines, func, iterable, *args):

        print('多线程启动')
        batches = []
        for j in range(lines):
            sub_iter = iterable[j::lines]
            batches.append(dask.delayed(func)(sub_iter, *args, j))
        result = dask.compute(batches)
        print('等待%s条线程全部完成...' % lines)
        print('多线程结束！')
        return result


    def get_fix_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/FixRoll/data/'):

        if restore:
            factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
            freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
            factor_list = sorted(list({x[8:-4] for x in os.listdir(
                factor_address) if re.match('^Fix1[0134][03]0_', x)}))
            factor_list = [x for x in factor_list if len([y for y in os.listdir(
                factor_address) if x in y and len(x) == len(y) - 12]) == len(freq)]
        else:
            remove_list = ['idx_date', 'idx_time', 'idx_code', 'nolimit', 'future', 'raw_idx_date', 'raw_idx_code']
            factor_list = sorted(
                [x[:-4] for x in os.listdir(factor_address) if (x[:-4] not in remove_list) & (x[0] != '_')])
        return factor_list


    def _load_pickle_frame(file_name, date_list, code_list):

        factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        df_dic = {}
        for time in freq:
            df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
            df.index = df.index.map(int)
            df.columns = df.columns.map(trans_windcode2int)
            df = df.reindex(date_list, code_list)
            df_dic[time] = df
        return np.r_['0,3', tuple(df_dic[x].values for x in freq)].transpose(1, 0, 2)


    from xquant.compute.aimr import AIMR

    bar_num = 8#int(AIMR.getParam())
    today = 20220304#get_recent_trade_date()
    self = MRFixFactorTest(20140601, 20140801, today)
    self.set_stock_pool()
    self.set_recent_pct_change(delay_min=-5,order_keep_min=5)
    self.set_future_by_30min(future_bar=bar_num,delay_min=1)
    # len(self.test_date_list)
    # from dataApi.getData import get_minute_1factor
    # import itertools
    # index = pd.MultiIndex.from_tuples(itertools.product(self.test_date_list,[1000,1030,1100,1300,1330,1400,1430]))
    # recent_pct =pd.DataFrame(self.recent_pct_change.reshape(self.future.shape[0]*7,len(self.code_list)),index=index,columns=self.code_list)
    #
    # close = get_minute_1factor('close_badj', 20140801, 20140805)
    # close_pct_change = close.rolling(5).mean().pct_change(242).shift(1)
    # close_pct_change = close_pct_change.loc[recent_pct.loc[:20140805].index]
    base_dir = '/data/group/800442/800319/HFfactor/PreMinutes__RealTimeFixRollRobustReversalResRct1Day8Bar/'
    save_address = f'{base_dir}/data/'
    result_address = f'{base_dir}/ic_month/Future_{bar_num}_bar/'

    if not os.path.exists(result_address):
        os.makedirs(result_address)
    if not os.path.exists(save_address):
        os.makedirs(save_address)

    fix_factor_list = get_fix_factor_list(True, '/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/')

    from dataApi.LoadingTool import trans_df2arr
    import itertools

    # arr,date_lst,code_lst = self.future,self.test_date_list,self.code_list
    def formated(arr,date_lst,code_lst,save_path=None,return_val=False):
        index = pd.MultiIndex.from_tuples(list(itertools.product([get_pre_trade_date(date_lst[0])]+date_lst,[1000, 1030, 1100, 1300, 1330, 1400, 1430])))
        arr = np.pad(arr,((1,0),(0,0),(0,0)),mode='constant',constant_values=np.nan)
        df = pd.DataFrame(arr.reshape(len(date_lst)*7+7,len(code_lst)),index=index,columns=code_lst)
        arr_flt = trans_df2arr(df,date_lst[0],date_lst[-1],roll=True)
        arr_flt = np.ascontiguousarray(arr_flt.astype('float32'))
        if not save_path is None:
            np.save(save_path,arr_flt)
        if return_val:
            return arr_flt
    formated(self.future,self.test_date_list,self.code_list,f"{save_address}/future_30_order_keep.npy")
    formated(self.recent_pct_change,self.test_date_list,self.code_list,f"{save_address}/rct_pct.npy")

    fix_factor_list = list(filter(lambda name :not (os.path.exists(f'{result_address}/{name}') and os.path.exists(f"{save_address}/{name}.npy")),fix_factor_list))

    def _func(sub_list, line=0):
        for name in sub_list:

            factor = _load_pickle_frame(name, self.calc_date_list, self.code_list)
            result,processed_factor = self.test_factor(factor,reg_days=1, move_window=12,test_return=False)
            if not os.path.exists(f"{save_address}/{name}.npy"):
                formated(processed_factor,self.test_date_list,self.code_list,f"{save_address}/{name}.npy")
            pd.to_pickle(result, f'{result_address}/{name}')
            print(time.strftime('%Y%m%d %H:%M:%S'), name)


    # _func(fix_factor_list)
    multidask(36, _func, fix_factor_list)


# from dataApi.FixFactorRollPrepare import