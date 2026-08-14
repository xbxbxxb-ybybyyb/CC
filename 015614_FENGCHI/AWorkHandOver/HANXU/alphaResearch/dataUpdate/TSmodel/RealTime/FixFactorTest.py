import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.tradeDate import get_date_range, get_pre_trade_date, trade_minutes, get_sub_date_index, \
    get_desample_minute_dict, get_trade_date_interval, get_recent_trade_date
from dataApi.getData import get_daily_1factor
from dataApi.stockList import clean_stock_list, trans_windcode2int
import numpy as np
import pandas as pd
import gc

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


class RealTimeModelFactorTest(object):

    def __init__(self, calc_start_date=20140101, test_start_date=20140601, end_date=20181231, freq=48):

        end_date = min(end_date, get_pre_trade_date(dividing_point=18))

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

        self.valid_daily_num = valid_daily_num
        self.stock_pool = stock_pool
        self.code_list = code_list
        self.code_num = code_num
        self.pool_d = pool_d

        if hasattr(self, 'future_days'):
            self.set_future(self.future_days, self.delay_min, self.order_keep_min)

    def set_future(self, future_days=1, delay_min=1, order_keep_min=5):

        future_end_date = get_pre_trade_date(self.end_date, - future_days - 1)
        future_date_list = get_date_range(self.test_start_date, future_end_date)
        future = get_minute_pickle('close_adj', future_date_list, self.code_list)
        idx = np.arange(self.test_date_num + future_days)[:, None, None] * 242 + np.asanyarray([find_trade_min(
            x, delay_min, order_keep_min) for x in self.period_list])[None, :, :]
        future = np.nanmean(future.values[idx], axis=2)
        future = future[future_days: self.test_date_num + future_days] / future[:self.test_date_num] - 1
        nolimit = get_minute_pickle('limit_status', future_date_list, self.code_list) == 0
        nolimit = nolimit.reshape(len(future_date_list), 242, len(self.code_list))[
            :-1, [trade_minutes.index(x) for x in self.period_list]]
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

    def test_factor(self, factor, standardize_days=40, top_tile=0.05, no_test=False):

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

            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1) + standardize_days
            factor = (factor[self.test_drop_days:] - rd_mean[:, None]) / rd_std[:, None]
            factor = factor.clip(-6, 6)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            if not no_test:
                factor2 = factor.copy()
                factor2[~ self.future_finite] = 0

            del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn

        else:
            d_cn = factor_finite.sum(axis=1)
            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1)
            factor = factor[self.test_drop_days:]
            factor_finite = factor_finite[self.test_drop_days:]
            factor[~ factor_finite] = 0
            if not no_test:
                factor2 = factor.copy()
                factor2[~ self.future_finite] = 0
            rd_mean = np.full(self.test_date_num, np.nan)
            rd_std = np.full(self.test_date_num, np.nan)

        if no_test:
            return factor, rd_mean, rd_std

        factor_complete = (factor_finite & self.future_finite).sum() / self.future_finite.sum()
        half_year_split = get_sub_date_index(self.test_date_list, 'H')
        start_dates, end_dates = stats_range(half_year_split, self.test_date_list)

        def reduce_sum(arr):

            arr = np.add.reduceat(arr, half_year_split, axis=0)
            arr_total = arr.sum(axis=0)
            return arr, arr_total

        def reduce_mean(arr):

            finite = np.isfinite(arr)
            arr[~ finite] = 0
            finite = finite.sum(axis=tuple(range(1, arr.ndim)))
            finite = np.add.reduceat(finite, half_year_split)
            arr = arr.sum(axis=tuple(range(1, arr.ndim)))
            arr = np.add.reduceat(arr, half_year_split)
            arr_total = arr.sum() / finite.sum()
            arr /= finite
            arr[~ np.isfinite(arr)] = np.nan
            return arr, arr_total

        x = factor2
        y = self.future2
        n = self.future_finite
        x2 = x ** 2
        y2 = y ** 2
        xy = x * y

        c2x = x.sum(axis=2)
        c2y = y.sum(axis=2)
        c2x2 = x2.sum(axis=2)
        c2y2 = y2.sum(axis=2)
        c2xy = xy.sum(axis=2)
        c2n = n.sum(axis=2)

        ic_half_c, ic_all_c = reduce_mean(calc_corr(c2x, c2y, c2x2, c2y2, c2xy, c2n))
        ic_half_tc, ic_all_tc = reduce_mean(calc_corr(c2x.sum(axis=1), c2y.sum(axis=1), c2x2.sum(axis=1),
                                                      c2y2.sum(axis=1), c2xy.sum(axis=1), c2n.sum(axis=1)))

        c2d1x, c2d0x = reduce_sum(c2x)
        c2d1y, c2d0y = reduce_sum(c2y)
        c2d1x2, c2d0x2 = reduce_sum(c2x2)
        c2d1y2, c2d0y2 = reduce_sum(c2y2)
        c2d1xy, c2d0xy = reduce_sum(c2xy)
        c2d1n, c2d0n = reduce_sum(c2n)

        ic_half_dc = np.nanmean(calc_corr(c2d1x, c2d1y, c2d1x2, c2d1y2, c2d1xy, c2d1n), axis=1)
        ic_all_dc = np.nanmean(calc_corr(c2d0x, c2d0y, c2d0x2, c2d0y2, c2d0xy, c2d0n))

        del c2d1x, c2d0x, c2d1y, c2d0y, c2d1x2, c2d0x2, c2d1y2, c2d0y2, c2d1xy, c2d0xy, c2d1n, c2d0n

        c2dt1x, c2dt0x = reduce_sum(c2x.sum(axis=1))
        c2dt1y, c2dt0y = reduce_sum(c2y.sum(axis=1))
        c2dt1x2, c2dt0x2 = reduce_sum(c2x2.sum(axis=1))
        c2dt1y2, c2dt0y2 = reduce_sum(c2y2.sum(axis=1))
        c2dt1xy, c2dt0xy = reduce_sum(c2xy.sum(axis=1))
        c2dt1n, c2dt0n = reduce_sum(c2n.sum(axis=1))

        ic_half_dtc = calc_corr(c2dt1x, c2dt1y, c2dt1x2, c2dt1y2, c2dt1xy, c2dt1n)
        ic_all_dtc = calc_corr(c2dt0x, c2dt0y, c2dt0x2, c2dt0y2, c2dt0xy, c2dt0n)

        del c2dt1x, c2dt0x, c2dt1y, c2dt0y, c2dt1x2, c2dt0x2, c2dt1y2, c2dt0y2, c2dt1xy, c2dt0xy, c2dt1n, c2dt0n
        del c2x, c2y, c2x2, c2y2, c2xy, c2n

        t2x = x.sum(axis=1)
        t2y = y.sum(axis=1)
        t2x2 = x2.sum(axis=1)
        t2y2 = y2.sum(axis=1)
        t2xy = xy.sum(axis=1)
        t2n = n.sum(axis=1)

        ic_half_t, ic_all_t = reduce_mean(calc_corr(t2x, t2y, t2x2, t2y2, t2xy, t2n))

        t2d1x, t2d0x = reduce_sum(t2x)
        t2d1y, t2d0y = reduce_sum(t2y)
        t2d1x2, t2d0x2 = reduce_sum(t2x2)
        t2d1y2, t2d0y2 = reduce_sum(t2y2)
        t2d1xy, t2d0xy = reduce_sum(t2xy)
        t2d1n, t2d0n = reduce_sum(t2n)

        ic_half_dt = np.nanmean(calc_corr(t2d1x, t2d1y, t2d1x2, t2d1y2, t2d1xy, t2d1n), axis=1)

        ic_all_dt_every_code = calc_corr(t2d0x, t2d0y, t2d0x2, t2d0y2, t2d0xy, t2d0n)
        ic_all_dt = np.nanmean(ic_all_dt_every_code)

        del t2d1x, t2d0x, t2d1y, t2d0y, t2d1x2, t2d0x2, t2d1y2, t2d0y2, t2d1xy, t2d0xy, t2d1n, t2d0n
        del t2x, t2y, t2x2, t2y2, t2xy, t2n

        d1x, d0x = reduce_sum(x)
        d1y, d0y = reduce_sum(y)
        d1x2, d0x2 = reduce_sum(x2)
        d1y2, d0y2 = reduce_sum(y2)
        d1xy, d0xy = reduce_sum(xy)
        d1n, d0n = reduce_sum(n)

        ic_half_d = np.nanmean(calc_corr(d1x, d1y, d1x2, d1y2, d1xy, d1n), axis=(1, 2))
        ic_all_d = np.nanmean(calc_corr(d0x, d0y, d0x2, d0y2, d0xy, d0n))

        del d1x, d0x, d1y, d0y, d1x2, d0x2, d1y2, d0y2, d1xy, d0xy, d1n, d0n
        del x, y, x2, y2, xy, n

        ic_direction = 2 * (ic_all_dt > 0) - 1

        ic_all_dtc *= ic_direction
        ic_all_dt *= ic_direction
        ic_all_tc *= ic_direction
        ic_all_dc *= ic_direction
        ic_all_d *= ic_direction
        ic_all_t *= ic_direction
        ic_all_c *= ic_direction

        ic_half_dtc *= ic_direction
        ic_half_dt *= ic_direction
        ic_half_tc *= ic_direction
        ic_half_dc *= ic_direction
        ic_half_d *= ic_direction
        ic_half_t *= ic_direction
        ic_half_c *= ic_direction

        ic_all_dt_every_code *= ic_direction
        ic_all_dt_every_code = ic_all_dt_every_code.flatten()
        ic_all_dt_every_code[~ np.isfinite(ic_all_dt_every_code)] = 0

        factor *= ic_direction
        factor2 *= ic_direction
        factor2[~ (factor_finite & self.future_finite)] = np.nan

        top_tile = top_tile if top_tile > 0.5 else 1 - top_tile
        factor2 = factor2.reshape(self.test_date_num * self.period_num, self.code_num)
        sign_threshold = np.nanquantile(factor2, top_tile, axis=0)
        factor2 = factor2.reshape(self.test_date_num, self.period_num, self.code_num)
        sign = (factor2 >= sign_threshold) & self.future_finite

        future2 = self.future2.copy()
        future2[~ sign] = 0
        positive = future2 > 0

        ret_dt = future2.sum(axis=2)
        ret_dc = future2.sum(axis=1)

        sign_dt = sign.sum(axis=2)
        sign_dc = sign.sum(axis=1)

        pos_dt = positive.sum(axis=2)
        pos_dc = positive.sum(axis=1)

        # mix mode
        sign_d = sign_dc.sum(axis=1)
        pos_d = pos_dc.sum(axis=1)
        ret_d = ret_dc.sum(axis=1)

        sign_mix_half = np.add.reduceat(sign_d, half_year_split)
        pool_mix_half = np.add.reduceat(self.pool_d, half_year_split)
        pos_mix_half = np.add.reduceat(pos_d, half_year_split)
        ret_mix_half = np.add.reduceat(ret_d, half_year_split)

        sign_ratio_mix_half = sign_mix_half / pool_mix_half
        pos_ratio_mix_half = pos_mix_half / sign_mix_half
        ret_ratio_mix_half = ret_mix_half / sign_mix_half
        pool_ratio_mix_half = pool_mix_half / pool_mix_half.sum()

        sign_ratio_mix_all = sign_mix_half.sum() / pool_mix_half.sum()
        pos_ratio_mix_all = pos_mix_half.sum() / sign_mix_half.sum()
        ret_ratio_mix_all = ret_mix_half.sum() / sign_mix_half.sum()

        # time mean then mix mode
        _ret_dc_mean = ret_dc / sign_dc
        _sign_dc_mean = np.isfinite(_ret_dc_mean)
        _pos_dc_mean = _ret_dc_mean > 0
        _ret_dc_mean[~ _sign_dc_mean] = 0

        ret_dc_mean = _ret_dc_mean.sum(axis=1)
        sign_dc_mean = _sign_dc_mean.sum(axis=1)
        pos_dc_mean = _pos_dc_mean.sum(axis=1)

        sign_dc_mean_half = np.add.reduceat(sign_dc_mean, half_year_split)
        pool_dc_mean_half = np.add.reduceat(self.pool_d / self.period_num, half_year_split)
        pos_dc_mean_half = np.add.reduceat(pos_dc_mean, half_year_split)
        ret_dc_mean_half = np.add.reduceat(ret_dc_mean, half_year_split)

        sign_ratio_dc_mean_half = sign_dc_mean_half / pool_dc_mean_half
        pos_ratio_dc_mean_half = pos_dc_mean_half / sign_dc_mean_half
        ret_ratio_dc_mean_half = ret_dc_mean_half / sign_dc_mean_half

        sign_ratio_dc_mean_all = sign_dc_mean_half.sum() / pool_dc_mean_half.sum()
        pos_ratio_dc_mean_all = pos_dc_mean_half.sum() / sign_dc_mean_half.sum()
        ret_ratio_dc_mean_all = ret_dc_mean_half.sum() / sign_dc_mean_half.sum()

        # time code mix mean then date mode
        ret_d_mean = ret_d / sign_d
        sign_d_mean = np.isfinite(ret_d_mean)
        pos_d_mean = ret_d_mean > 0
        ret_d_mean[~ sign_d_mean] = 0
        pool_d_mean = self.pool_d > 0

        sign_d_mean_half = np.add.reduceat(sign_d_mean, half_year_split)
        pool_d_mean_half = np.add.reduceat(pool_d_mean, half_year_split)
        pos_d_mean_half = np.add.reduceat(pos_d_mean, half_year_split)
        ret_d_mean_half = np.add.reduceat(ret_d_mean, half_year_split)

        sign_ratio_d_mean_half = sign_d_mean_half / pool_d_mean_half
        pos_ratio_d_mean_half = pos_d_mean_half / sign_d_mean_half
        ret_ratio_d_mean_half = ret_d_mean_half / sign_d_mean_half
        pool_ratio_d_mean_half = pool_d_mean_half / pool_d_mean_half.sum()

        sign_ratio_d_mean_all = sign_d_mean_half.sum() / pool_d_mean_half.sum()
        pos_ratio_d_mean_all = pos_d_mean_half.sum() / sign_d_mean_half.sum()
        ret_ratio_d_mean_all = ret_d_mean_half.sum() / sign_d_mean_half.sum()

        # time mean then code mean then date mode
        _ret_d_mean = _ret_dc_mean.sum(axis=1) / _sign_dc_mean.sum(axis=1)
        _pos_d_mean = _ret_d_mean > 0
        _ret_d_mean[~ sign_d_mean] = 0

        _pos_d_mean_half = np.add.reduceat(_pos_d_mean, half_year_split)
        _ret_d_mean_half = np.add.reduceat(_ret_d_mean, half_year_split)

        _pos_ratio_d_mean_half = _pos_d_mean_half / sign_d_mean_half
        _ret_ratio_d_mean_half = _ret_d_mean_half / sign_d_mean_half

        _pos_ratio_d_mean_all = _pos_d_mean_half.sum() / sign_d_mean_half.sum()
        _ret_ratio_d_mean_all = _ret_d_mean_half.sum() / sign_d_mean_half.sum()

        # date code mix then time
        sign_dt_half = np.add.reduceat(sign_dt, half_year_split, axis=0)
        pos_dt_half = np.add.reduceat(pos_dt, half_year_split, axis=0)
        ret_dt_half = np.add.reduceat(ret_dt, half_year_split, axis=0)

        sign_ratio_dt_half = sign_dt_half / sign_dt_half.sum(axis=1, keepdims=True)
        pos_ratio_dt_half = pos_dt_half / sign_dt_half
        ret_ratio_dt_half = ret_dt_half / sign_dt_half

        sign_ratio_dt_all = sign_dt_half.sum(axis=0) / sign_dt_half.sum()
        pos_ratio_dt_all = pos_dt_half.sum(axis=0) / sign_dt_half.sum(axis=0)
        ret_ratio_dt_all = ret_dt_half.sum(axis=0) / sign_dt_half.sum(axis=0)

        # date time mix then code
        sign_c_half = np.add.reduceat(sign_dc, half_year_split, axis=0)
        pos_c_half = np.add.reduceat(pos_dc, half_year_split, axis=0)
        ret_c_half = np.add.reduceat(ret_dc, half_year_split, axis=0)
        pool_c_half = np.add.reduceat(self.stock_pool, half_year_split, axis=0) * self.period_num

        sign_ratio_c_half = sign_c_half / pool_c_half
        pos_ratio_c_half = pos_c_half / sign_c_half
        ret_ratio_c_half = ret_c_half / sign_c_half
        pool_ratio_c_half = pool_c_half / pool_c_half.sum(axis=1, keepdims=True)

        sign_ratio_c_all = sign_c_half.sum(axis=0) / pool_c_half.sum(axis=0)
        pos_ratio_c_all = pos_c_half.sum(axis=0) / sign_c_half.sum(axis=0)
        ret_ratio_c_all = ret_c_half.sum(axis=0) / sign_c_half.sum(axis=0)
        pool_ratio_c_all = pool_c_half.sum(axis=0) / pool_c_half.sum()

        # time mean then date mean then code
        _sign_c_half = np.add.reduceat(_sign_dc_mean, half_year_split, axis=0)
        _pos_c_half = np.add.reduceat(_pos_dc_mean, half_year_split, axis=0)
        _ret_c_half = np.add.reduceat(_ret_dc_mean, half_year_split, axis=0)

        _sign_ratio_c_half = _sign_c_half / pool_c_half * self.period_num
        _pos_ratio_c_half = _pos_c_half / _sign_c_half
        _ret_ratio_c_half = _ret_c_half / _sign_c_half

        _sign_ratio_c_all = _sign_c_half.sum(axis=0) / pool_c_half.sum(axis=0) * self.period_num
        _pos_ratio_c_all = _pos_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)
        _ret_ratio_c_all = _ret_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)

        del sign
        gc.collect()

        result = dict(

            # basic information
            date_list=self.test_date_list,
            date_num=self.test_date_num,
            date_invalid_num=invalid_days,
            date_half_year_starts=start_dates,
            date_half_year_ends=end_dates,
            date_standardize_days=standardize_days,

            code_list=self.code_list,
            code_num=self.code_num,

            future_days=self.future_days,
            future_delay_min=self.delay_min,
            future_order_keep_min=self.order_keep_min,
            future_top_tile=top_tile,

            factor_complete=factor_complete,

            # IC
            ic_direction=ic_direction,

            ic_all_dtc=ic_all_dtc,
            ic_all_dt=ic_all_dt,
            ic_all_tc=ic_all_tc,
            ic_all_dc=ic_all_dc,
            ic_all_d=ic_all_d,
            ic_all_t=ic_all_t,
            ic_all_c=ic_all_c,

            ic_all_dt_every_code=ic_all_dt_every_code,
            ic_half_dtc=ic_half_dtc,
            ic_half_dt=ic_half_dt,
            ic_half_tc=ic_half_tc,
            ic_half_dc=ic_half_dc,
            ic_half_d=ic_half_d,
            ic_half_t=ic_half_t,
            ic_half_c=ic_half_c,

            # dtc mode
            dtc_half_sign=sign_ratio_mix_half,
            dtc_half_pos=pos_ratio_mix_half,
            dtc_half_ret=ret_ratio_mix_half,
            dtc_half_pool=pool_ratio_mix_half,

            dtc_all_sign=sign_ratio_mix_all,
            dtc_all_pos=pos_ratio_mix_all,
            dtc_all_ret=ret_ratio_mix_all,

            # t_dc mode
            t_dc_half_sign=sign_ratio_dc_mean_half,
            t_dc_half_pos=pos_ratio_dc_mean_half,
            t_dc_half_ret=ret_ratio_dc_mean_half,

            t_dc_all_sign=sign_ratio_dc_mean_all,
            t_dc_all_pos=pos_ratio_dc_mean_all,
            t_dc_all_ret=ret_ratio_dc_mean_all,

            # tc_d_mode
            tc_d_half_sign=sign_ratio_d_mean_half,
            tc_d_half_pos=pos_ratio_d_mean_half,
            tc_d_half_ret=ret_ratio_d_mean_half,
            tc_d_half_pool=pool_ratio_d_mean_half,

            tc_d_all_sign=sign_ratio_d_mean_all,
            tc_d_all_pos=pos_ratio_d_mean_all,
            tc_d_all_ret=ret_ratio_d_mean_all,

            tc_d_ret=ret_d_mean,

            # t_c_d_mode
            t_c_d_half_pos=_pos_ratio_d_mean_half,
            t_c_d_half_ret=_ret_ratio_d_mean_half,

            t_c_d_all_pos=_pos_ratio_d_mean_all,
            t_c_d_all_ret=_ret_ratio_d_mean_all,

            t_c_d_ret=_ret_d_mean,

            # dc_t mode
            dc_t_half_sign=sign_ratio_dt_half,
            dc_t_half_pos=pos_ratio_dt_half,
            dc_t_half_ret=ret_ratio_dt_half,

            dc_t_all_sign=sign_ratio_dt_all,
            dc_t_all_pos=pos_ratio_dt_all,
            dc_t_all_ret=ret_ratio_dt_all,

            # dt_c mode
            dt_c_half_sign=sign_ratio_c_half,
            dt_c_half_pos=pos_ratio_c_half,
            dt_c_half_ret=ret_ratio_c_half,
            dt_c_half_pool=pool_ratio_c_half,

            dt_c_all_sign=sign_ratio_c_all,
            dt_c_all_pos=pos_ratio_c_all,
            dt_c_all_ret=ret_ratio_c_all,
            dt_c_all_pool=pool_ratio_c_all,

            # t_d_c mode
            t_d_c_half_sign=_sign_ratio_c_half,
            t_d_c_half_pos=_pos_ratio_c_half,
            t_d_c_half_ret=_ret_ratio_c_half,

            t_d_c_all_sign=_sign_ratio_c_all,
            t_d_c_all_pos=_pos_ratio_c_all,
            t_d_c_all_ret=_ret_ratio_c_all,
        )

        return result, factor, rd_mean, rd_std
