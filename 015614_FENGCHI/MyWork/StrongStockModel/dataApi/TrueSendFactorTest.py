import os
import re
import time

import numpy as np
import pandas as pd
import psutil

from dataApi.getData import get_daily_1factor, get_minute_1factor
from dataApi.stockList import clean_stock_list
from dataApi.tradeDate import get_date_range, get_desample_minute_dict, get_pre_trade_date, trade_minutes, \
    get_sub_date_index


def _memory_used():

    info = psutil.virtual_memory()
    used = round((info.total - info.available) / 1024 ** 3, 2)
    return used

def _get_fix_factor_list():

    factor_address = '/data/group/800319/VeryJunkFix/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    factor_list = sorted(list({x[8:-3] for x in os.listdir(factor_address) if re.match('^Fix1[0134][03]0_', x)}))
    factor_list = [x for x in factor_list if len([y for y in os.listdir(
        factor_address) if x in y and len(x) == len(y) - 11]) == len(freq)]
    return factor_list


def stats_range(date_index, date_list):

    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end

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

def count_excess_ratio(arr, limit):

    return np.sum(arr > limit, axis=-1) / arr.shape[-1]

class TrueSendFactorTest(object):


    def __init__(self, start_date=20140102, end_date=20190628, code_list=None, hold_days=5):

        date_list = get_date_range(start_date, end_date)
        start_date = date_list[0]
        end_date = date_list[-1]
        date_num = len(date_list)

        if code_list is None:
            code_list = get_daily_1factor('stock_list', date_list).sum() > 0
            code_list = code_list[code_list].index.to_list()
        code_num = len(code_list)

        if isinstance(hold_days, int):
            hold_days = list(range(1, hold_days + 1))
        elif not isinstance(hold_days, list):
            raise TypeError('hold_days must be int or list')
        hold_days_max = max(hold_days)
        hold_days_num = len(hold_days)
        _hold_end_date = get_pre_trade_date(end_date, - hold_days_max - 1)

        _close = get_minute_1factor('close_badj', start_date, _hold_end_date, code_list=code_list).values
        _amt = get_minute_1factor('amt', start_date, _hold_end_date, code_list=code_list).values
        _vol = get_minute_1factor('vol', start_date, _hold_end_date, code_list=code_list).values

        _close[_close < 0.1] = np.nan

        self.start_date = start_date
        self.end_date = end_date
        self.date_list = date_list
        self.date_num = date_num

        self.code_list = code_list
        self.code_num = code_num
        self.hold_days = hold_days
        self.hold_days_max = hold_days_max
        self.hold_days_num = hold_days_num
        self._hold_end_date = _hold_end_date
        self._close = _close
        self._amt = _amt
        self._vol = _vol

    def set_stock_pool(self, stock_pool_name=None, stock_list='ALL', no_ST=True,
                       least_live_days=240, no_pause=True, least_recover_days=1, no_pause_limit=0.5,
                       no_pause_stats_days=120, no_limit_up=True, no_limit_down=True, other_limit=None,
                       stock_pool_address='/data/group/800319/TrueSendStrategy/'):

        if stock_pool_name:
            stock_pool = get_daily_1factor(stock_pool_name, date_list=self.date_list, code_list=self.code_list,
                                           diy_address=stock_pool_address) > 0.5
        else:
            stock_pool = clean_stock_list(stock_list=stock_list, no_ST=no_ST, least_live_days=least_live_days,
                                          no_pause=no_pause, least_recover_days=least_recover_days,
                                          no_pause_limit=no_pause_limit, no_pause_stats_days=no_pause_stats_days,
                                          no_limit_up=no_limit_up, no_limit_down=no_limit_down,
                                          other_limit=other_limit, start_date=self.start_date, end_date=self.end_date)
            stock_pool = stock_pool.reindex(columns=self.code_list) > 0.5
            stock_pool_name = 'customize'

        stock_pool = stock_pool.values[:, :, None]
        self.stock_pool_name = stock_pool_name
        self.stock_pool = stock_pool

    def define_transaction_assumption(self, freq='Fix', delay_min=1, order_keep_min=10):

        if freq is 'Fix':
            freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        elif isinstance(freq, int):
            freq = sorted(list(set(get_desample_minute_dict(freq).values())))
        elif not isinstance(freq, list):
            raise TypeError("freq must be int or List(int) object.")
        freq_num = len(freq)

        idx = np.arange(self.date_num + self.hold_days_max)[:, None, None] * 242 + np.array([find_trade_min(
            x, delay_min, order_keep_min) for x in freq])[None, :, :]
        close = self._close[idx].copy()
        amt = self._amt[idx].copy()
        vol = self._vol[idx].copy()
        close *= vol
        close = np.nansum(close, axis=2)
        amt = np.nansum(amt, axis=2)
        vol = np.nansum(vol, axis=2)
        close = np.where(close > 0, close / vol, np.nan)
        amt = amt.transpose(0, 2, 1)
        close = close.transpose(0, 2, 1)

        future = np.r_['0,4', tuple(close[x: self.date_num + x] / close[:self.date_num] - 1 for x in self.hold_days)]
        future[~ np.isfinite(future)] = 0

        amt_buy = amt[:self.date_num]
        amt_sell = np.r_['0,4', tuple(amt[x: self.date_num + x] for x in self.hold_days)]

        self.freq = freq
        self.future = future
        self.amt_buy = amt_buy
        self.amt_sell = amt_sell
        self.freq_num = freq_num
        self.delay_min = delay_min
        self.order_keep_min = order_keep_min

    def load_factor(self, factor_name, factor_type='fix', base_date=20130101,
                    factor_address='/data/group/800319/VeryJunkFix/'):

        if factor_type == 'fix':
            factor = np.r_['0,3', tuple(get_daily_1factor('Fix%s_%s' % (x, factor_name),
                                                          date_list=self.date_list,
                                                          code_list=self.code_list,
                                                          diy_address=factor_address).values
                                        for x in self.freq)].transpose(1, 2, 0)
        elif factor_type == 'daily':
            factor = get_daily_1factor(factor_name, self.date_list, self.code_list,
                                       diy_address=factor_address).values[:, :, None]
        elif factor_type == 'minute':
            factor = get_minute_1factor(factor_name, self.start_date, self.end_date, 240 // self.freq_num, self.code_list,
                                        base_date=base_date, diy_address=factor_address).values.reshape(
                self.date_num, self.freq_num, self.code_num).transpose(0, 2, 1)
        elif factor_type == 'integrated_fix':
            base_date_list = get_date_range(20140102, 20190628)
            start_idx = base_date_list.index(self.start_date) * 7
            end_idx = base_date_list.index(self.end_date) * 7 + 7
            factor = pd.read_hdf(factor_address + factor_name + '.h5', factor_name, start=start_idx, stop=end_idx).reindex(self.code_list, axis=1).values
            factor = factor.reshape(factor.shape[0] // 7, 7, factor.shape[1]).transpose(0, 2, 1)
        else:
            raise ValueError("factor_type must be fix, daily or minute.")

        self.factor_type = factor_type
        self.factor_name = factor_name
        self.factor = factor

    def calc_ic(self, period='Y'):

        clean = np.isfinite(self.factor) & self.stock_pool

        arr_date = (np.arange(self.date_num)[:, None, None] + np.zeros((
            self.code_num, self.freq_num), dtype=int))[clean]
        arr_factor = self.factor[clean]
        arr_future = self.future[:, clean]

        arr_date_idx = sorted(list(set(arr_date)))
        arr_date_list = list(np.array(self.date_list)[arr_date_idx])
        arr_sub_date_index = get_sub_date_index(arr_date_list, period=period)
        arr_sub_date_idx = np.array(arr_date_idx)[arr_sub_date_index]
        arr_date_divide_idx = [list(arr_date).index(x) for x in arr_sub_date_idx]
        start_dates, end_dates = stats_range(arr_sub_date_index, arr_date_list)

        x = arr_factor
        y = arr_future
        x2 = arr_factor ** 2
        y2 = arr_future ** 2
        xy = arr_factor * arr_future
        n = np.ones_like(x)

        cx = np.add.reduceat(x, arr_date_divide_idx, axis=-1)
        cy = np.add.reduceat(y, arr_date_divide_idx, axis=-1)
        cx2 = np.add.reduceat(x2, arr_date_divide_idx, axis=-1)
        cy2 = np.add.reduceat(y2, arr_date_divide_idx, axis=-1)
        cxy = np.add.reduceat(xy, arr_date_divide_idx, axis=-1)
        cn = np.add.reduceat(n, arr_date_divide_idx, axis=-1)

        ic = (cn * cxy - cx * cy) / np.sqrt((cn * cx2 - cx ** 2) * (cn * cy2 - cy ** 2))

        direction = ((ic > 0).sum() / (ic < 0).sum() > 1) * 2 - 1

        ic = pd.DataFrame(ic.T, index=pd.MultiIndex.from_arrays([start_dates, end_dates], names=[
            'start_date', 'end_date']), columns=self.hold_days)

        self.arr_date_idx = arr_date_idx
        self.arr_factor = arr_factor
        self.direction = direction
        self.arr_date = arr_date
        self.period = period
        self.clean = clean
        self.ic = ic

        return ic

    def calc_top_ret(self, roll_window=240, top_quantile=0.1):

        arr_factor = self.arr_factor * self.direction
        factor = self.factor * self.direction

        top_quantile = top_quantile if isinstance(top_quantile, list) else [top_quantile]
        top_quantile = [x if x > 0.5 else 1 - x for x in top_quantile]
        top_quantile_num = len(top_quantile)

        arr_date_list_main = self.arr_date_idx[roll_window:]
        arr_date_idx_main = np.arange(len(self.arr_date))[np.r_[[True], np.diff(self.arr_date) > 0.5]]
        factor_limit = np.array([np.quantile(arr_factor[arr_date_idx_main[x]: arr_date_idx_main[
            x + roll_window]], top_quantile) for x in range(len(arr_date_idx_main) - roll_window)]).T

        factor_top = (factor[None, :, :, :][
                      :, arr_date_list_main] >= factor_limit[:, :, None, None]) & self.clean[arr_date_list_main]
        factor_top = factor_top.cumsum(axis=-1).cumsum(axis=-1) == 1

        arr_date_list_main_date_list = list(np.array(self.date_list)[arr_date_list_main])
        arr_date_list_main_sub_date_index = get_sub_date_index(arr_date_list_main_date_list, period=self.period)
        main_start_dates, main_end_dates = stats_range(arr_date_list_main_sub_date_index, arr_date_list_main_date_list)
        main_index = pd.MultiIndex.from_arrays([main_start_dates, main_end_dates], names=['start_date', 'end_date'])
        main_period_num = len(main_start_dates)

        time_sign_num = factor_top.sum(axis=1).sum(axis=1)
        date_sign_num = factor_top.sum(axis=-1).sum(axis=-1)
        period_sign_num = np.add.reduceat(date_sign_num, arr_date_list_main_sub_date_index, axis=-1)

        top_ret_sum = np.full((top_quantile_num, self.hold_days_num, main_period_num), np.nan)
        top_ret_mean = np.full((top_quantile_num, self.hold_days_num, main_period_num), np.nan)
        top_ret_pos = np.full((top_quantile_num, self.hold_days_num, main_period_num), np.nan)
        top_ret_pl = np.full((top_quantile_num, self.hold_days_num, main_period_num), np.nan)

        for j in range(top_quantile_num):

            top_date = (np.arange(len(arr_date_list_main_date_list))[:, None, None] + np.zeros(
                (self.code_num, self.freq_num), dtype=int))[factor_top[j]]
            top_future = self.future[:, arr_date_list_main][:, factor_top[j]]

            top_date_idx = sorted(list(set(top_date)))
            top_date_list = list(np.array(arr_date_list_main_date_list)[top_date_idx])
            top_sub_date_index = get_sub_date_index(top_date_list, period=self.period)
            top_sub_date_idx = np.array(top_date_idx)[top_sub_date_index]
            top_date_divide_idx = [list(top_date).index(x) for x in top_sub_date_idx]

            _top_ret_sum = np.full((self.hold_days_max, main_period_num), np.nan)
            _top_pos_num = np.full((self.hold_days_max, main_period_num), np.nan)
            _top_pos_sum = np.full((self.hold_days_max, main_period_num), np.nan)

            _top_ret_sum[:, period_sign_num[j] > 0] = np.add.reduceat(top_future, top_date_divide_idx, axis=-1)
            _top_pos_num[:, period_sign_num[j] > 0] = np.add.reduceat(top_future > 0, top_date_divide_idx, axis=-1)
            _top_pos_sum[:, period_sign_num[j] > 0] = np.add.reduceat(
                np.where(top_future > 0, top_future, 0), top_date_divide_idx, axis=-1)

            top_ret_sum[j] = _top_ret_sum
            top_ret_mean[j] = top_ret_sum[j] / period_sign_num[j]
            top_ret_pos[j] = _top_pos_num / period_sign_num[j]
            top_ret_pl[j] = _top_pos_sum / (_top_pos_sum - top_ret_sum[j]) * (1 - top_ret_pos[j]) / top_ret_pos[j]

        time_sign_num = pd.DataFrame(time_sign_num, index=top_quantile, columns=self.freq)
        period_sign_num = pd.DataFrame(period_sign_num.T, index=main_index, columns=top_quantile)

        self.arr_date_list_main = arr_date_list_main
        self.top_quantile_num = top_quantile_num
        self.period_sign_num = period_sign_num
        self.main_index = main_index
        self.time_sign_num = time_sign_num
        self.top_ret_sum = top_ret_sum
        self.top_ret_mean = top_ret_mean
        self.top_ret_pos = top_ret_pos
        self.top_ret_pl = top_ret_pl
        self.factor_top = factor_top
        self.roll_window = roll_window
        self.top_quantile = top_quantile

    def calc_finish_ratio(self, amt_limit=5e5):

        buy_ratio = np.array([count_excess_ratio(self.amt_buy[self.arr_date_list_main][self.factor_top[x]], amt_limit)
                              for x in range(self.top_quantile_num)])
        sell_ratio = np.array([count_excess_ratio(self.amt_sell[:, self.arr_date_list_main][:, self.factor_top[x]],
                                                  amt_limit) for x in range(self.top_quantile_num)])
        finish_ratio = pd.DataFrame(np.c_[buy_ratio, sell_ratio],
                                    index=self.top_quantile, columns=[0] + self.hold_days)
        self.finish_ratio = finish_ratio
        self.amt_limit = amt_limit
        return finish_ratio

    def output(self, output_address):

        params = pd.Series(dict(
            start_date=self.start_date,
            end_date=self.end_date,
            hold_days=self.hold_days,
            freq=self.freq,
            stock_pool_name=self.stock_pool_name,
            factor_name=self.factor_name,
            factor_type=self.factor_type,
            delay_min=self.delay_min,
            order_keep_min=self.order_keep_min,
            amt_limit=self.amt_limit,
            period=self.period,
            roll_window=self.roll_window,
            top_quantile=self.top_quantile,
        ), name='params')

        with pd.ExcelWriter('%s/%s.xlsx' % (output_address, self.factor_name)) as writer:

            params.to_excel(writer, 'params')
            self.ic.to_excel(writer, 'ic')
            self.finish_ratio.to_excel(writer, 'finish_ratio')
            self.time_sign_num.to_excel(writer, 'time_sign_num')
            self.period_sign_num.to_excel(writer, 'period_sign_num')

            for j in range(self.top_quantile_num):
                pd.DataFrame(self.top_ret_sum[j].T, index=self.main_index, columns=self.hold_days).to_excel(
                    writer, 'top_ret_sum_%s' % self.top_quantile[j])
                pd.DataFrame(self.top_ret_mean[j].T, index=self.main_index, columns=self.hold_days).to_excel(
                    writer, 'top_ret_mean_%s' % self.top_quantile[j])
                pd.DataFrame(self.top_ret_pos[j].T, index=self.main_index, columns=self.hold_days).to_excel(
                    writer, 'top_ret_pos_%s' % self.top_quantile[j])
                pd.DataFrame(self.top_ret_pl[j].T, index=self.main_index, columns=self.hold_days).to_excel(
                    writer, 'top_ret_pl_%s' % self.top_quantile[j])

if __name__ == '__main__':

    start_date = 20140102
    end_date = 20190628
    code_list = None
    hold_days = 5
    freq = 'Fix'

    stock_pool_name = 'strong'
    delay_min = 1
    order_keep_min = 10
    period = 'Y'  # 'ALL'
    roll_window = 245
    top_quantile = [0.05, 0.1, 0.15]
    amt_limit = 5e5
    output_address = '/data/user/hanxu/TrueSendStrategy/Fix_test_common'

    t = time.time()
    factor_list = _get_fix_factor_list()
    tsft = TrueSendFactorTest(start_date, end_date, code_list, hold_days)
    tsft.set_stock_pool(stock_list='ALL', other_limit={'mkt_cap_ard': 0.05})
    tsft.define_transaction_assumption(freq, delay_min, order_keep_min)
    print('memory_used=', _memory_used(), ' time_used=', time.time() - t)

    from tqdm import tqdm
    for factor_name in tqdm(factor_list):

        tsft.load_factor(factor_name)
        tsft.calc_ic(period)
        tsft.calc_top_ret(roll_window, top_quantile)
        tsft.calc_finish_ratio(amt_limit)
        tsft.output(output_address)
