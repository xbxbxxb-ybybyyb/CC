from tradeDate import get_date_range, trade_minutes, get_sub_date_index, get_desample_minute_dict
from FactorList import FactorList, OperatorList, Config
from operators import *
import pandas as pd
import numpy as np
import requests
import json
import pickle
import time
import dask
import gc
import re
import os

import warnings
warnings.filterwarnings("ignore")

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

def get_program_factor(formula):

    program = formula.replace('*', ' ').replace('/', ' ').replace('+', ' ').replace(
        '-', ' ').replace('&', ' ').replace('|', ' ').replace('%', ' ').replace(
        ',', ' ').replace('(', ' ').replace(')', ' ').split()
    factors = sorted(list(set(program) & set(FactorList)))
    return factors

def stats_range(date_index, date_list):
    date_list = np.asanyarray(date_list)
    date_index = np.asanyarray(date_index + [len(date_list)])
    start = date_list[date_index[:-1]]
    end = date_list[date_index[1:] - 1]
    return start, end

def save_pickle(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def load_pickle(file):
    with open(file, 'rb') as f:
        data = pickle.load(f)
    return data

def calc_corr(x, y, x2, y2, xy, n):
    corr = (xy - x * y / n) / ((x2 - x ** 2 / n) * (y2 - y ** 2 / n)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    corr = corr if corr.size > 1 else corr.item()
    return corr

def send_message(users, msg):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    if isinstance(users, list):
        users = '|'.join(users)

    data = {"touser": users,
            "msgtype": "text",
            "agentid": 1000033,
            "text": {"content": msg}}
    json_data = json.dumps(data)
    requests.post(post_url, json_data)

def calc_raw_corr(x, y):

    cx2 = (x ** 2).sum()
    cy2 = (y ** 2).sum(axis=-1)
    cxy = (x * y).sum(axis=-1)
    cn = x.size
    cx = x.sum()
    cy = y.sum(axis=-1)
    corr = (cxy - cx * cy / cn) / ((cx2 - cx ** 2 / cn) * (cy2 - cy ** 2 / cn)) ** 0.5
    corr = np.where(np.isfinite(corr), corr, 0)
    corr = corr if corr.size > 1 else corr.item()
    return corr

def load_pickles(address3, ic_half_dt_every_code, factor_sample):

    _corr_files3 = [x for x in os.listdir(address3) if x.isdigit()]
    time_file = str(max([int(x) for x in _corr_files3] + [0]) + 1).zfill(4)

    ic_half_dt_compare3 = []
    factor_compare3 = []
    corr_files3 = []

    for file in _corr_files3:
        dic = load_pickle(address3 + file)
        if not dic['corr_ignore']:
            corr_files3.append(file)
            ic_half_dt_compare3.append(dic['ic_all_dt_every_code'])
            factor_compare3.append(dic['factor_sample'])

    if len(corr_files3) == 0:
        ic_half_dt_compare = np.array([0.])
        factor_compare = np.array([0.])
    else:
        ic_half_dt_compare = np.atleast_2d(np.asanyarray(ic_half_dt_compare3))
        ic_half_dt_compare = calc_raw_corr(ic_half_dt_every_code, ic_half_dt_compare)

        factor_compare = np.atleast_2d(np.asanyarray(factor_compare3))
        factor_compare = np.r_['0,2', tuple(calc_raw_corr(factor_sample[1000 * x: 1000 * (x + 1)],
                                                          factor_compare[:, 1000 * x: 1000 * (x + 1)])
                                            for x in range(3))]
        factor_compare = np.nanmedian(factor_compare, axis=0) + 0.03

    ic_half_dt_compare = np.fmax(ic_half_dt_compare, factor_compare)

    return corr_files3, ic_half_dt_compare, time_file

def recover_number(s):

    try:
        return int(s)
    except:
        try:
            return float(s)
        except:
            return s

def _formula2program(formula):

    program =  formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]
    return program

def _check_complete(formula):

    program =  formula.replace(',', ' ').replace('(', ' ').replace(')', ' ').split()
    program = [recover_number(x) for x in program]

    terminal_stack = []

    for item in program:

        if item in OperatorList:
            terminal_stack.append(1 if not item[-1].isdigit() else int(item[-1]))
        elif item in FactorList:
            terminal_stack[-1] -= 1
            while terminal_stack[-1] == 0:
                terminal_stack.pop()
                if not terminal_stack:
                    return True
                terminal_stack[-1] -= 1
        elif isinstance(item, str):
            raise ValueError("Any basic factor or operator created without permission is not allowed.")
    return False

class FactorTest2(object):

    def __init__(self):

        self.fold = time.strftime('%Y%m%d%H%M%S')
        os.mkdir('/data/group/800442/800319/junkBigFactorPool/' + self.fold)

        random_state = np.random.RandomState(3251)
        self._sample = random_state.choice(135013152, 3000, replace=False)

        self._future_finite = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/future_finite.npy')
        self._future = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/future.npy')
        self._code_list = list(np.load('/data/group/800442/800319/junkBigFactorPool/back_data/code_list.npy'))
        self._stock_pool = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/stock_pool.npy')

        calc_start_date = 20140101
        test_start_date = 20140601
        end_date = 20181231
        freq = 48

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

        valid_daily_num = self._stock_pool.sum(axis=1)
        code_num = len(self._code_list)
        pool_d = self._stock_pool.sum(axis=1) * period_num

        self._future_days = 1
        self._delay_min = 1
        self._order_keep_min = 5
        self._standardize_days = 40
        self._top_tile = 0.05
        self._freq = freq
        self.freq = freq
        self._period = period
        self.code_list = self._code_list.copy()
        self._period_list = period_list
        self._period_num = period_num
        self._test_date_list = test_date_list
        self.calc_date_list = calc_date_list
        self._test_start_date = test_start_date
        self.calc_start_date = calc_start_date
        self._test_date_num = test_date_num
        self.calc_date_num = calc_date_num
        self._test_drop_days = test_drop_days
        self._end_date = end_date
        self.end_date = end_date
        self._valid_daily_num = valid_daily_num
        self._code_num = code_num
        self._pool_d = pool_d

    def test_factor(self, factor):

        factor_finite = np.isfinite(factor)

        if self._standardize_days:
            factor[~ factor_finite] = 0
            factor2 = factor ** 2

            d_cf = factor.sum(axis=1)
            d_cf2 = factor2.sum(axis=1)
            d_cn = factor_finite.sum(axis=1)

            rd_cf = bottleneck.move_sum(d_cf, self._standardize_days, axis=0)
            rd_cf2 = bottleneck.move_sum(d_cf2, self._standardize_days, axis=0)
            rd_cn = bottleneck.move_sum(d_cn, self._standardize_days, axis=0)
            rd_cn[rd_cn < self._standardize_days * self._freq / 2] = np.nan

            rd_mean = rd_cf / rd_cn
            rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
            rd_std[rd_std == 0] = np.nan
            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1) + self._standardize_days
            factor = (factor[self._test_drop_days:] - rd_mean[self._test_drop_days - 1: -1, None]
                      ) / rd_std[self._test_drop_days - 1: -1, None]
            factor = factor.clip(-10, 10)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            factor2 = factor.copy()
            factor2[~ self._future_finite] = 0

            del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn, rd_mean, rd_std

        else:
            d_cn = factor_finite.sum(axis=1)
            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1)
            factor = factor[self._test_drop_days:]
            factor = factor.clip(-6, 6)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            factor2 = factor.copy()
            factor2[~ self._future_finite] = 0

        factor_complete = (factor_finite & self._future_finite).sum() / self._future_finite.sum()

        half_year_split = get_sub_date_index(self._test_date_list, 'H')
        start_dates, end_dates = stats_range(half_year_split, self._test_date_list)

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
        y = self._future
        n = self._future_finite
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
        factor2[~ (factor_finite & self._future_finite)] = np.nan

        top_tile = self._top_tile if self._top_tile > 0.5 else 1 - self._top_tile
        factor2 = factor2.reshape(self._test_date_num * self._period_num, self._code_num)
        sign_threshold = np.nanquantile(factor2, top_tile, axis=0)
        factor2 = factor2.reshape(self._test_date_num, self._period_num, self._code_num)
        sign = (factor2 >= sign_threshold) & self._future_finite

        future2 = self._future.copy()
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
        pool_mix_half = np.add.reduceat(self._pool_d, half_year_split)
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
        pool_dc_mean_half = np.add.reduceat(self._pool_d / self._period_num, half_year_split)
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
        pool_d_mean = self._pool_d > 0

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
        pool_c_half = np.add.reduceat(self._stock_pool, half_year_split, axis=0) * self._period_num

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

        _sign_ratio_c_half = _sign_c_half / pool_c_half * self._period_num
        _pos_ratio_c_half = _pos_c_half / _sign_c_half
        _ret_ratio_c_half = _ret_c_half / _sign_c_half

        _sign_ratio_c_all = _sign_c_half.sum(axis=0) / pool_c_half.sum(axis=0) * self._period_num
        _pos_ratio_c_all = _pos_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)
        _ret_ratio_c_all = _ret_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)

        del sign
        gc.collect()

        result = dict(

            # basic information
            date_list=self._test_date_list,
            date_num=self._test_date_num,
            date_invalid_num=invalid_days,
            date_half_year_starts=start_dates,
            date_half_year_ends=end_dates,
            date_standardize_days=self._standardize_days,

            code_list=self._code_list,
            code_num=self._code_num,

            future_days=self._future_days,
            future_delay_min=self._delay_min,
            future_order_keep_min=self._order_keep_min,
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

        return result, factor

    def test_good_program(self, program, noprint=False, admin=None):

        address2 = '/data/group/800442/800319/junkBigFactorPool/%s/' % self.fold

        if program['program_class'] not in ('绝对收益类', '相对收益类', '价量相关类',
                                            '波动率类', '换手率类', '估值类', '机器挖掘'):
            raise ValueError("Please input correct program class.")

        if not (program['program_manual'] | (program['program_class'] == '机器挖掘')):
            raise ValueError("Please input correct program class.")

        if not program['program_manual'] | (program['program_logic'] == '无知无畏'):
            raise ValueError("Please input correct program logic.")

        if not program['program_manual'] | (program['program_reference'] == '无知无畏'):
            raise ValueError("Please input correct program reference.")

        if len(program['program_reference']) < 4:
            raise ValueError("Please input correct and complete program refer.")

        if len(program['program_logic']) < 4:
            raise ValueError("Please input correct and complete program logic.")

        if not (program['program_author'].isdigit() & (len(program['program_author']) == 6)):
            raise ValueError("Please input correct program author.")

        if program['program_complex']:
            if 'complex_simplified' in program:
                if program['complex_simplified']:
                    program['program_code'] = program['program_code'].replace(
                        '\n', '').replace(' ', '').replace(',', ', ')
                    for basic_factor in get_program_factor(program['program_code']):
                        if basic_factor not in globals():
                            globals()[basic_factor] = np.load(
                                '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
                    factor = eval(program['program_code'])
                else:
                    raise ValueError("The key complex_simplified must always be True once used.")
            else:
                indent = re.search('\n([ ]+)[\w+]', program['program_code'])[1]
                program_code = program['program_code'].replace('\n' + indent, '\n')

                def _gec_fac(self):
                    factor = 0
                    loc = {'factor': factor, 'self': self}
                    eval(compile(program_code, '', 'exec'), {}, loc)
                    factor = loc['factor']
                    return factor

                factor = _gec_fac(self)
                if isinstance(factor, pd.DataFrame):
                    index = pd.MultiIndex.from_product([self.calc_date_list, self._period_list], names=['date', 'time'])
                    factor = factor.reindex(index=index, columns=self._code_list)
                    factor = factor.values.reshape(self.calc_date_num, self._period_num, self._code_num)
                if np.isfinite(np.unique(factor[-1])).sum() < 2:
                    raise ValueError("Please ensure that no future data mixed in.")
        else:
            program['program_code'] = program['program_code'].replace('\n', '').replace(' ', '').replace(',', ', ')
            if re.search('[\+\-\*/]', program['program_code']):
                raise SyntaxError("Please check your simple program code --overloaded operator is not allowed.")
            if '((' in program['program_code']:
                raise SyntaxError("Please check your simple program code. --unnecessary brackets is not allowed.")
            if not _check_complete(program['program_code']):
                raise SyntaxError("Please check your simple program code. --replacing factor by number is not allowed.")
            for basic_factor in get_program_factor(program['program_code']):
                if basic_factor not in globals():
                    globals()[basic_factor] = np.load(
                        '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
            factor = eval(program['program_code'])

        result, factor = self.test_factor(factor)
        factor = factor.transpose(0, 2, 1)[self._stock_pool[:, :, None].repeat(
            self.freq, axis=2)].astype(np.float32)

        important_items = ['ic_direction', 'date_invalid_num', 'ic_all_dtc', 'ic_all_dt', 'ic_all_c',
                           'ic_all_t', 'ic_all_d', 'dtc_all_sign', 'dtc_all_ret', 't_dc_all_ret',
                           'tc_d_all_ret', 't_c_d_all_ret', 'ic_half_dt', 'ic_half_dc', 'ic_half_tc',
                           'ic_half_d', 'ic_half_t', 'ic_half_c', 'factor_complete']

        simple_result = {x : result[x] for x in important_items}
        ic_all_dt_every_code = result['ic_all_dt_every_code']

        factor_sample = factor[self._sample]

        judge = {True : '复杂表达式', False : '简单表达式'}

        test_report = 'Factor Test Report'.center(64, '*') + '\n'
        test_report += 'Introduction'.center(64, '-') + '\n'
        file_time = time.strftime('%Y-%m-%d %H:%M:%S')
        test_report += file_time +  '\n'
        file_time = file_time.replace('-', '').replace(' ', '').replace(':', '') + str(np.random.randint(100, 1000))

        test_report += (program['program_author'] + ' ' + judge[program['program_complex']]
                        + ' ' + program['program_class'] + '\n')

        if program['program_manual']:
            test_report += program['program_logic'] + '\n'
            test_report += program['program_reference'] + '\n'

        if not program['program_complex']:
            test_report += program['program_code'] + '\n'
        else:
            test_report += [x for x in program['program_code'].split('\n') if x != ''][-1] + '\n'

        judge = {True : '', False : 'Fail'}

        date_invalid_num = simple_result['date_invalid_num'] < Config['date_invalid_num']
        ic_all_dtc = simple_result['ic_all_dtc'] > (
            Config['ic_all_dtc'][0] if program['program_manual'] else Config['ic_all_dtc'][1])
        ic_all_dt = simple_result['ic_all_dt'] > (
            Config['ic_all_dt'][0] if program['program_manual'] else Config['ic_all_dt'][1])
        ic_all_c = simple_result['ic_all_c'] > (
            Config['ic_all_c'][0] if program['program_manual'] else Config['ic_all_c'][1])
        ic_all_t = simple_result['ic_all_t'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_t'][1])
        ic_all_d = simple_result['ic_all_d'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_d'][1])
        _top_ret = (simple_result['dtc_all_ret'] + simple_result['t_dc_all_ret'] +
                   simple_result['tc_d_all_ret'] + simple_result['t_c_d_all_ret'])
        top_ret = _top_ret > (Config['top_ret'][0] if program['program_manual'] else Config['top_ret'][1])
        dtc_all_sign = (Config['dtc_all_sign'][0][0] < simple_result['dtc_all_sign'] < Config['dtc_all_sign'][0][1]
                        ) if program['program_manual'] else (Config['dtc_all_sign'][1][0] < simple_result[
            'dtc_all_sign'] < Config['dtc_all_sign'][1][1])
        half_ic = (simple_result['ic_half_dt'] < 0).sum() <= (
            Config['ic_half'][0] if program['program_manual'] else Config['ic_half'][1])

        program['corr_ignore'] = False
        corr = True

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            corr_files2, ic_all_dt_compare, _ = load_pickles(address2, ic_all_dt_every_code, factor_sample)
            corr_max = round(ic_all_dt_compare.max(), 4)

            if corr_max < Config['corr_limit']:
                corr = True
            elif (ic_all_dt_compare >= Config['corr_limit']).sum() > 1:
                corr = False
            else:
                corr_bench = np.arange(len(ic_all_dt_compare)).dot(ic_all_dt_compare >= Config['corr_limit'])
                corr_bench_file = address2, corr_files2[corr_bench]
                corr_bench_ic = load_pickle(corr_bench_file[0] + corr_bench_file[1])
                if (corr_bench_ic['ic_all_dt'] + corr_bench_ic['ic_all_c'] + 2 * corr_bench_ic['ic_all_dtc'] <
                        simple_result['ic_all_dt'] + simple_result['ic_all_c'] + 2 * simple_result['ic_all_dtc']):
                    corr = True
                    corr_bench_ic['corr_ignore'] = True
                    corr_bench_ic['corr_best_file'] = file_time
                    program['corr_bench_file'] = corr_bench_file[1]
                    save_pickle(corr_bench_file[0] + corr_bench_file[1], corr_bench_ic)
                else:
                    corr = False
                    program['corr_bench_file'] = corr_bench_file[1]

        test_report += 'Conclusion'.center(64, '-') + '\n'

        program.update(simple_result)
        program.update({'ic_all_dt_every_code': ic_all_dt_every_code.astype(np.float32)})
        program.update({'factor_sample': factor_sample.astype(np.float32)})

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign & corr:
            test_report += '山重水复疑无路，柳暗花明又一村。\n'
            test_report += 'Congratulations! Your factor test SUCCEEDED as expected!\n'
            program.update(result)
            save_pickle(address2 + file_time, program)

        else:
            test_report += '证券投资部是一支年轻的队伍，年轻没有失败。\n'
            test_report += 'We regret to tell you that your factor test FAILED!\n'

        test_report += 'Details'.center(64, '-') + '\n'

        test_report += 'Factor Direction:'.ljust(18) + str(simple_result['ic_direction']).ljust(6) + '\n'

        test_report += 'Invalid Days:'.ljust(18) + str(simple_result['date_invalid_num']
                                                       ).ljust(6) + ''.ljust(13) + judge[date_invalid_num] +'\n'

        test_report += 'Completeness:'.ljust(18) + str(round(simple_result['factor_complete'], 4)
                                                       ).ljust(6) + '\n'

        test_report += 'Global IC:'.ljust(18) + str(round(simple_result['ic_all_dtc'], 4)
                                                    ).ljust(6) + ''.ljust(13) + judge[ic_all_dtc] +'\n'

        test_report += 'Cross Section IC:'.ljust(18) + str(round(simple_result['ic_all_c'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_c] + '\n'

        test_report += 'Time Series IC:'.ljust(18) + str(round(simple_result['ic_all_dt'], 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[ic_all_dt] +'\n'

        test_report += 'Intraday IC:'.ljust(18) + str(round(simple_result['ic_all_t'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_t] + '\n'

        test_report += 'Interday IC:'.ljust(18) + str(round(simple_result['ic_all_d'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_d] + '\n'

        test_report += 'Top Return:'.ljust(18) + str(round(_top_ret, 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[top_ret] + '\n'
        test_report += 'Top Ratio:'.ljust(18) + str(round(simple_result['dtc_all_sign'], 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[dtc_all_sign] + '\n'
        _ic_half_dt = list(simple_result['ic_half_dt'].round(4))
        test_report += 'Half Year IC:'.ljust(18) + str(_ic_half_dt[:2]) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[2:4]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[4:6]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[6:8]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[8:]).ljust(18)
        test_report += '  ' + judge[half_ic] + '\n'

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            test_report += 'Corr Max:'.ljust(18) + str(round(corr_max, 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[corr] + '\n'
        if 'corr_bench_file' in program:
            test_report += 'Corr Related:'.ljust(18) + program['corr_bench_file'] + '\n'
        test_report += 'The End'.center(64, '*') + '\n'

        if admin == 95238:
            return simple_result
        else:
            if not noprint:
                print(test_report)

    def test_all_program(self, program, noprint=False, admin=None):

        address2 = '/data/group/800442/800319/junkBigFactorPool/%s/' % self.fold

        if program['program_class'] not in ('绝对收益类', '相对收益类', '价量相关类',
                                            '波动率类', '换手率类', '估值类', '机器挖掘'):
            raise ValueError("Please input correct program class.")

        if not (program['program_manual'] | (program['program_class'] == '机器挖掘')):
            raise ValueError("Please input correct program class.")

        if not program['program_manual'] | (program['program_logic'] == '无知无畏'):
            raise ValueError("Please input correct program logic.")

        if not program['program_manual'] | (program['program_reference'] == '无知无畏'):
            raise ValueError("Please input correct program reference.")

        if len(program['program_reference']) < 4:
            raise ValueError("Please input correct and complete program refer.")

        if len(program['program_logic']) < 4:
            raise ValueError("Please input correct and complete program logic.")

        if not (program['program_author'].isdigit() & (len(program['program_author']) == 6)):
            raise ValueError("Please input correct program author.")

        if program['program_complex']:
            if 'complex_simplified' in program:
                if program['complex_simplified']:
                    program['program_code'] = program['program_code'].replace(
                        '\n', '').replace(' ', '').replace(',', ', ')
                    for basic_factor in get_program_factor(program['program_code']):
                        if basic_factor not in globals():
                            globals()[basic_factor] = np.load(
                                '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
                    factor = eval(program['program_code'])
                else:
                    raise ValueError("The key complex_simplified must always be True once used.")
            else:
                indent = re.search('\n([ ]+)[\w+]', program['program_code'])[1]
                program_code = program['program_code'].replace('\n' + indent, '\n')

                def _gec_fac(self):
                    factor = 0
                    loc = {'factor': factor, 'self': self}
                    eval(compile(program_code, '', 'exec'), {}, loc)
                    factor = loc['factor']
                    return factor

                factor = _gec_fac(self)
                if isinstance(factor, pd.DataFrame):
                    index = pd.MultiIndex.from_product([self.calc_date_list, self._period_list], names=['date', 'time'])
                    factor = factor.reindex(index=index, columns=self._code_list)
                    factor = factor.values.reshape(self.calc_date_num, self._period_num, self._code_num)
                if np.isfinite(np.unique(factor[-1])).sum() < 2:
                    raise ValueError("Please ensure that no future data mixed in.")
        else:
            program['program_code'] = program['program_code'].replace('\n', '').replace(' ', '').replace(',', ', ')
            if re.search('[\+\-\*/]', program['program_code']):
                raise SyntaxError("Please check your simple program code --overloaded operator is not allowed.")
            if '((' in program['program_code']:
                raise SyntaxError("Please check your simple program code. --unnecessary brackets is not allowed.")
            if not _check_complete(program['program_code']):
                raise SyntaxError("Please check your simple program code. --replacing factor by number is not allowed.")
            for basic_factor in get_program_factor(program['program_code']):
                if basic_factor not in globals():
                    globals()[basic_factor] = np.load(
                        '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
            factor = eval(program['program_code'])

        result, factor = self.test_factor(factor)
        factor = factor.transpose(0, 2, 1)[self._stock_pool[:, :, None].repeat(
            self.freq, axis=2)].astype(np.float32)

        important_items = ['ic_direction', 'date_invalid_num', 'ic_all_dtc', 'ic_all_dt', 'ic_all_c',
                           'ic_all_t', 'ic_all_d', 'dtc_all_sign', 'dtc_all_ret', 't_dc_all_ret',
                           'tc_d_all_ret', 't_c_d_all_ret', 'ic_half_dt', 'ic_half_dc', 'ic_half_tc',
                           'ic_half_d', 'ic_half_t', 'ic_half_c', 'factor_complete']

        simple_result = {x : result[x] for x in important_items}

        factor_sample = factor[self._sample]

        judge = {True : '复杂表达式', False : '简单表达式'}

        test_report = 'Factor Test Report'.center(64, '*') + '\n'
        test_report += 'Introduction'.center(64, '-') + '\n'
        file_time = time.strftime('%Y-%m-%d %H:%M:%S')
        test_report += file_time +  '\n'
        file_time = file_time.replace('-', '').replace(' ', '').replace(':', '') + str(np.random.randint(100, 1000))

        test_report += (program['program_author'] + ' ' + judge[program['program_complex']]
                        + ' ' + program['program_class'] + '\n')

        if program['program_manual']:
            test_report += program['program_logic'] + '\n'
            test_report += program['program_reference'] + '\n'

        if not program['program_complex']:
            test_report += program['program_code'] + '\n'
        else:
            test_report += [x for x in program['program_code'].split('\n') if x != ''][-1] + '\n'

        judge = {True : '', False : 'Fail'}

        date_invalid_num = simple_result['date_invalid_num'] < Config['date_invalid_num']
        ic_all_dtc = simple_result['ic_all_dtc'] > (
            Config['ic_all_dtc'][0] if program['program_manual'] else Config['ic_all_dtc'][1])
        ic_all_dt = simple_result['ic_all_dt'] > (
            Config['ic_all_dt'][0] if program['program_manual'] else Config['ic_all_dt'][1])
        ic_all_c = simple_result['ic_all_c'] > (
            Config['ic_all_c'][0] if program['program_manual'] else Config['ic_all_c'][1])
        ic_all_t = simple_result['ic_all_t'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_t'][1])
        ic_all_d = simple_result['ic_all_d'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_d'][1])
        _top_ret = (simple_result['dtc_all_ret'] + simple_result['t_dc_all_ret'] +
                   simple_result['tc_d_all_ret'] + simple_result['t_c_d_all_ret'])
        top_ret = _top_ret > (Config['top_ret'][0] if program['program_manual'] else Config['top_ret'][1])
        dtc_all_sign = (Config['dtc_all_sign'][0][0] < simple_result['dtc_all_sign'] < Config['dtc_all_sign'][0][1]
                        ) if program['program_manual'] else (Config['dtc_all_sign'][1][0] < simple_result[
            'dtc_all_sign'] < Config['dtc_all_sign'][1][1])
        half_ic = (simple_result['ic_half_dt'] < 0).sum() <= (
            Config['ic_half'][0] if program['program_manual'] else Config['ic_half'][1])
        test_report += 'Conclusion'.center(64, '-') + '\n'

        program.update({'factor_sample': factor_sample.astype(np.float32)})
        program.update(result)
        save_pickle(address2 + file_time, program)

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            test_report += '山重水复疑无路，柳暗花明又一村。\n'
            test_report += 'Congratulations! Your factor test SUCCEEDED as expected!\n'

        else:
            test_report += '证券投资部是一支年轻的队伍，年轻没有失败。\n'
            test_report += 'We regret to tell you that your factor test FAILED!\n'

        test_report += 'Details'.center(64, '-') + '\n'

        test_report += 'Factor Direction:'.ljust(18) + str(simple_result['ic_direction']).ljust(6) + '\n'

        test_report += 'Invalid Days:'.ljust(18) + str(simple_result['date_invalid_num']
                                                       ).ljust(6) + ''.ljust(13) + judge[date_invalid_num] +'\n'

        test_report += 'Completeness:'.ljust(18) + str(round(simple_result['factor_complete'], 4)
                                                       ).ljust(6) + '\n'

        test_report += 'Global IC:'.ljust(18) + str(round(simple_result['ic_all_dtc'], 4)
                                                    ).ljust(6) + ''.ljust(13) + judge[ic_all_dtc] +'\n'

        test_report += 'Cross Section IC:'.ljust(18) + str(round(simple_result['ic_all_c'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_c] + '\n'

        test_report += 'Time Series IC:'.ljust(18) + str(round(simple_result['ic_all_dt'], 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[ic_all_dt] +'\n'

        test_report += 'Intraday IC:'.ljust(18) + str(round(simple_result['ic_all_t'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_t] + '\n'

        test_report += 'Interday IC:'.ljust(18) + str(round(simple_result['ic_all_d'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_d] + '\n'

        test_report += 'Top Return:'.ljust(18) + str(round(_top_ret, 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[top_ret] + '\n'
        test_report += 'Top Ratio:'.ljust(18) + str(round(simple_result['dtc_all_sign'], 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[dtc_all_sign] + '\n'
        _ic_half_dt = list(simple_result['ic_half_dt'].round(4))
        test_report += 'Half Year IC:'.ljust(18) + str(_ic_half_dt[:2]) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[2:4]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[4:6]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[6:8]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[8:]).ljust(18)
        test_report += '  ' + judge[half_ic] + '\n'

        test_report += 'The End'.center(64, '*') + '\n'

        if admin == 95238:
            return simple_result
        else:
            if not noprint:
                print(test_report)

class FactorTest(object):

    def __init__(self):

        random_state = np.random.RandomState(3251)
        self._sample = random_state.choice(135013152, 3000, replace=False)

        self._future_finite = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/future_finite.npy')
        self._future = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/future.npy')
        self._code_list = list(np.load('/data/group/800442/800319/junkBigFactorPool/back_data/code_list.npy'))
        self._stock_pool = np.load('/data/group/800442/800319/junkBigFactorPool/back_data/stock_pool.npy')

        calc_start_date = 20140101
        test_start_date = 20140601
        end_date = 20181231
        freq = 48

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

        valid_daily_num = self._stock_pool.sum(axis=1)
        code_num = len(self._code_list)
        pool_d = self._stock_pool.sum(axis=1) * period_num

        self._future_days = 1
        self._delay_min = 1
        self._order_keep_min = 5
        self._standardize_days = 40
        self._top_tile = 0.05
        self._freq = freq
        self.freq = freq
        self._period = period
        self.code_list = self._code_list.copy()
        self._period_list = period_list
        self._period_num = period_num
        self._test_date_list = test_date_list
        self.calc_date_list = calc_date_list
        self._test_start_date = test_start_date
        self.calc_start_date = calc_start_date
        self._test_date_num = test_date_num
        self.calc_date_num = calc_date_num
        self._test_drop_days = test_drop_days
        self._end_date = end_date
        self.end_date = end_date
        self._valid_daily_num = valid_daily_num
        self._code_num = code_num
        self._pool_d = pool_d

    def __test_factor(self, factor):

        factor_finite = np.isfinite(factor)

        if self._standardize_days:
            factor[~ factor_finite] = 0
            factor2 = factor ** 2

            d_cf = factor.sum(axis=1)
            d_cf2 = factor2.sum(axis=1)
            d_cn = factor_finite.sum(axis=1)

            rd_cf = bottleneck.move_sum(d_cf, self._standardize_days, axis=0)
            rd_cf2 = bottleneck.move_sum(d_cf2, self._standardize_days, axis=0)
            rd_cn = bottleneck.move_sum(d_cn, self._standardize_days, axis=0)
            rd_cn[rd_cn < self._standardize_days * self._freq / 2] = np.nan

            rd_mean = rd_cf / rd_cn
            rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
            rd_std[rd_std == 0] = np.nan
            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1) + self._standardize_days
            factor = (factor[self._test_drop_days:] - rd_mean[self._test_drop_days - 1: -1, None]
                      ) / rd_std[self._test_drop_days - 1: -1, None]
            factor = factor.clip(-6, 6)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            factor2 = factor.copy()
            factor2[~ self._future_finite] = 0

            del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn, rd_mean, rd_std

        else:
            d_cn = factor_finite.sum(axis=1)
            invalid_days = np.searchsorted(d_cn.sum(axis=1), 1)
            factor = factor[self._test_drop_days:]
            factor = factor.clip(-5, 5)
            factor_finite = np.isfinite(factor)
            factor[~ factor_finite] = 0
            factor2 = factor.copy()
            factor2[~ self._future_finite] = 0

        factor_complete = (factor_finite & self._future_finite).sum() / self._future_finite.sum()

        half_year_split = get_sub_date_index(self._test_date_list, 'H')
        start_dates, end_dates = stats_range(half_year_split, self._test_date_list)

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
        y = self._future
        n = self._future_finite
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
        factor2[~ (factor_finite & self._future_finite)] = np.nan

        top_tile = self._top_tile if self._top_tile > 0.5 else 1 - self._top_tile
        factor2 = factor2.reshape(self._test_date_num * self._period_num, self._code_num)
        sign_threshold = np.nanquantile(factor2, top_tile, axis=0)
        factor2 = factor2.reshape(self._test_date_num, self._period_num, self._code_num)
        sign = (factor2 >= sign_threshold) & self._future_finite

        future2 = self._future.copy()
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
        pool_mix_half = np.add.reduceat(self._pool_d, half_year_split)
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
        pool_dc_mean_half = np.add.reduceat(self._pool_d / self._period_num, half_year_split)
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
        pool_d_mean = self._pool_d > 0

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
        pool_c_half = np.add.reduceat(self._stock_pool, half_year_split, axis=0) * self._period_num

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

        _sign_ratio_c_half = _sign_c_half / pool_c_half * self._period_num
        _pos_ratio_c_half = _pos_c_half / _sign_c_half
        _ret_ratio_c_half = _ret_c_half / _sign_c_half

        _sign_ratio_c_all = _sign_c_half.sum(axis=0) / pool_c_half.sum(axis=0) * self._period_num
        _pos_ratio_c_all = _pos_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)
        _ret_ratio_c_all = _ret_c_half.sum(axis=0) / _sign_c_half.sum(axis=0)

        del sign
        gc.collect()

        result = dict(

            # basic information
            date_list=self._test_date_list,
            date_num=self._test_date_num,
            date_invalid_num=invalid_days,
            date_half_year_starts=start_dates,
            date_half_year_ends=end_dates,
            date_standardize_days=self._standardize_days,

            code_list=self._code_list,
            code_num=self._code_num,

            future_days=self._future_days,
            future_delay_min=self._delay_min,
            future_order_keep_min=self._order_keep_min,
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

        return result, factor

    def simulate_test_factor(self, program_code, admin=None):

        test_report = 'Simulate Test Report'.center(64, '*') + '\n'

        address0 = '/data/group/800442/800319/junkBigFactorPool/level0_unfinished/fail/'
        address2 = '/data/group/800442/800319/junkBigFactorPool/level2_waiting/'

        if isinstance(program_code, str):
            program_code = program_code.replace('\n', '').replace(' ', '').replace(',', ', ')
            for basic_factor in get_program_factor(program_code):
                if basic_factor not in globals():
                    globals()[basic_factor] = np.load(
                        '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
            test_report += program_code + '\n'
            factor = eval(program_code)
        elif isinstance(program_code, np.ndarray):
            factor = program_code
        else:
            raise TypeError("Invalid program code type.")

        result, factor = self.__test_factor(factor)
        factor = factor.transpose(0, 2, 1)[self._stock_pool[:, :, None].repeat(
            self.freq, axis=2)].astype(np.float32)
        factor_sample = factor[self._sample]


        important_items = ['ic_direction', 'date_invalid_num', 'ic_all_dtc', 'ic_all_dt', 'ic_all_c',
                           'ic_all_t', 'ic_all_d', 'dtc_all_sign', 'dtc_all_ret', 't_dc_all_ret',
                           'tc_d_all_ret', 't_c_d_all_ret', 'ic_half_dt', 'ic_half_dc', 'ic_half_tc',
                           'ic_half_d', 'ic_half_t', 'ic_half_c', 'factor_complete']

        simple_result = {x : result[x] for x in important_items}
        ic_all_dt_every_code = result['ic_all_dt_every_code']

        judge = {True : '', False : 'Fail'}

        date_invalid_num = simple_result['date_invalid_num'] < Config['date_invalid_num']
        ic_all_dtc = simple_result['ic_all_dtc'] > Config['ic_all_dtc'][0]
        ic_all_dt = simple_result['ic_all_dt'] > Config['ic_all_dt'][0]
        ic_all_c = simple_result['ic_all_c'] > Config['ic_all_c'][0]
        ic_all_t = simple_result['ic_all_t'] > Config['ic_all_t'][0]
        ic_all_d = simple_result['ic_all_d'] > Config['ic_all_d'][0]
        _top_ret = (simple_result['dtc_all_ret'] + simple_result['t_dc_all_ret'] +
                   simple_result['tc_d_all_ret'] + simple_result['t_c_d_all_ret'])
        top_ret = _top_ret > Config['top_ret'][0]
        dtc_all_sign = Config['dtc_all_sign'][0][0] < simple_result['dtc_all_sign'] < Config['dtc_all_sign'][0][1]

        half_ic = (simple_result['ic_half_dt'] < 0).sum() <= Config['ic_half'][0]

        corr = True
        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:

            corr_files2, ic_all_dt_compare, _ = load_pickles(address2, ic_all_dt_every_code, factor_sample)
            corr_max = round(ic_all_dt_compare.max(), 4)

            if corr_max < Config['corr_limit']:
                corr = True
            elif (ic_all_dt_compare >= Config['corr_limit']).sum() > 1:
                corr = False
            else:
                corr_bench = np.arange(len(ic_all_dt_compare)).dot(ic_all_dt_compare >= Config['corr_limit'])
                corr_bench_file = address2, corr_files2[corr_bench]
                corr_bench_ic = load_pickle(corr_bench_file[0] + corr_bench_file[1])
                if (corr_bench_ic['ic_all_dt'] + corr_bench_ic['ic_all_c'] + 2 * corr_bench_ic['ic_all_dtc'] <
                        simple_result['ic_all_dt'] + simple_result['ic_all_c'] + 2 * simple_result['ic_all_dtc']):
                    corr = True
                else:
                    corr = False

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign & corr:
            simple_result['pass_test'] = True
            test_report += 'Conclusion: PASS.\n'
        else:
            test_report += 'Conclusion: FAIL.\n'
            simple_result['pass_test'] = False


        test_report += 'Factor Direction:'.ljust(18) + str(simple_result['ic_direction']).ljust(6) + '\n'

        test_report += 'Invalid Days:'.ljust(18) + str(simple_result['date_invalid_num']
                                                       ).ljust(6) + ''.ljust(13) + judge[date_invalid_num] +'\n'

        test_report += 'Global IC:'.ljust(18) + str(round(simple_result['ic_all_dtc'], 4)
                                                    ).ljust(6) + ''.ljust(13) + judge[ic_all_dtc] +'\n'

        test_report += 'Cross Section IC:'.ljust(18) + str(round(simple_result['ic_all_c'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_c] + '\n'

        test_report += 'Time Series IC:'.ljust(18) + str(round(simple_result['ic_all_dt'], 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[ic_all_dt] +'\n'

        test_report += 'Intraday IC:'.ljust(18) + str(round(simple_result['ic_all_t'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_t] + '\n'

        test_report += 'Interday IC:'.ljust(18) + str(round(simple_result['ic_all_d'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_d] + '\n'

        test_report += 'Top Return:'.ljust(18) + str(round(_top_ret, 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[top_ret] + '\n'
        test_report += 'Top Ratio:'.ljust(18) + str(round(simple_result['dtc_all_sign'], 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[dtc_all_sign] + '\n'
        _ic_half_dt = list(simple_result['ic_half_dt'].round(4))
        test_report += 'Half Year IC:'.ljust(18) + str(_ic_half_dt[:2]) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[2:4]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[4:6]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[6:8]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[8:]).ljust(18)
        test_report += '  ' + judge[half_ic] + '\n'
        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            test_report += 'Corr Max:'.ljust(18) + str(round(corr_max, 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[corr] + '\n'
            if (ic_all_dt_compare >= Config['corr_limit']).sum() == 1:
                test_report += 'Corr Related:'.ljust(18) + corr_bench_file[1] + '\n'
        test_report += 'The End'.center(64, '*') + '\n'

        if isinstance(program_code, str):
            if (not re.search('[\+\-\*/]', program_code)) and (
                    '((' not in program_code) and _check_complete(program_code):
                simple_result.update({
                    'program_code': program_code,
                    'ic_all_dt_every_code': ic_all_dt_every_code,
                    'program_complex': False,
                    'factor_sample': factor_sample})
                file_time = time.strftime('%Y%m%d%H%M%S') + str(np.random.randint(100, 1000))
                save_pickle(address0 + file_time, simple_result)

        if admin == 95238:
            return simple_result
        else:
            print(test_report)

    def test_factor(self, program, noprint=False, admin=None):

        address0 = '/data/group/800442/800319/junkBigFactorPool/level0_unfinished/fail/'
        #address1 = '/data/group/800442/800319/junkBigFactorPool/level1_confidence/'
        address2 = '/data/group/800442/800319/junkBigFactorPool/level2_waiting/'
        factor_address = '/data/group/800442/800319/junkBigFactorPool/back_factor/'

        if program['program_class'] not in ('绝对收益类', '相对收益类', '价量相关类',
                                            '波动率类', '换手率类', '估值类', '机器挖掘'):
            raise ValueError("Please input correct program class.")

        if not (program['program_manual'] | (program['program_class'] == '机器挖掘')):
            raise ValueError("Please input correct program class.")

        if not program['program_manual'] | (program['program_logic'] == '无知无畏'):
            raise ValueError("Please input correct program logic.")

        if not program['program_manual'] | (program['program_reference'] == '无知无畏'):
            raise ValueError("Please input correct program reference.")

        if len(program['program_reference']) < 4:
            raise ValueError("Please input correct and complete program refer.")

        if len(program['program_logic']) < 4:
            raise ValueError("Please input correct and complete program logic.")

        if not (program['program_author'].isdigit() & (len(program['program_author']) == 6)):
            raise ValueError("Please input correct program author.")

        if program['program_complex']:
            if 'complex_simplified' in program:
                if program['complex_simplified']:
                    program['program_code'] = program['program_code'].replace(
                        '\n', '').replace(' ', '').replace(',', ', ')
                    for basic_factor in get_program_factor(program['program_code']):
                        if basic_factor not in globals():
                            globals()[basic_factor] = np.load(
                                '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
                    factor = eval(program['program_code'])
                else:
                    raise ValueError("The key complex_simplified must always be True once used.")
            else:
                indent = re.search('\n([ ]+)[\w+]', program['program_code'])[1]
                program_code = program['program_code'].replace('\n' + indent, '\n')

                def _gec_fac(self):
                    factor = 0
                    loc = {'factor': factor, 'self': self}
                    eval(compile(program_code, '', 'exec'), {}, loc)
                    factor = loc['factor']
                    return factor

                factor = _gec_fac(self)
                if isinstance(factor, pd.DataFrame):
                    index = pd.MultiIndex.from_product([self.calc_date_list, self._period_list], names=['date', 'time'])
                    factor = factor.reindex(index=index, columns=self._code_list)
                    factor = factor.values.reshape(self.calc_date_num, self._period_num, self._code_num)
                if np.isfinite(np.unique(factor[-1])).sum() < 2:
                    raise ValueError("Please ensure that no future data mixed in.")
        else:
            program['program_code'] = program['program_code'].replace('\n', '').replace(' ', '').replace(',', ', ')
            if re.search('[\+\-\*/]', program['program_code']):
                raise SyntaxError("Please check your simple program code --overloaded operator is not allowed.")
            if '((' in program['program_code']:
                raise SyntaxError("Please check your simple program code. --unnecessary brackets is not allowed.")
            if not _check_complete(program['program_code']):
                raise SyntaxError("Please check your simple program code. --replacing factor by number is not allowed.")
            for basic_factor in get_program_factor(program['program_code']):
                if basic_factor not in globals():
                    globals()[basic_factor] = np.load(
                        '/data/group/800442/800319/junkBigFactorPool/back_data/%s.npy' % basic_factor)
            factor = eval(program['program_code'])

        result, factor = self.__test_factor(factor)
        factor = factor.transpose(0, 2, 1)[self._stock_pool[:, :, None].repeat(
            self.freq, axis=2)].astype(np.float32)

        important_items = ['ic_direction', 'date_invalid_num', 'ic_all_dtc', 'ic_all_dt', 'ic_all_c',
                           'ic_all_t', 'ic_all_d', 'dtc_all_sign', 'dtc_all_ret', 't_dc_all_ret',
                           'tc_d_all_ret', 't_c_d_all_ret', 'ic_half_dt', 'ic_half_dc', 'ic_half_tc',
                           'ic_half_d', 'ic_half_t', 'ic_half_c', 'factor_complete']

        simple_result = {x : result[x] for x in important_items}
        ic_all_dt_every_code = result['ic_all_dt_every_code']

        factor_sample = factor[self._sample]

        judge = {True : '复杂表达式', False : '简单表达式'}

        test_report = 'Factor Test Report'.center(64, '*') + '\n'
        test_report += 'Introduction'.center(64, '-') + '\n'
        file_time = time.strftime('%Y-%m-%d %H:%M:%S')
        test_report += file_time +  '\n'
        file_time = file_time.replace('-', '').replace(' ', '').replace(':', '') + str(np.random.randint(100, 1000))

        test_report += (program['program_author'] + ' ' + judge[program['program_complex']]
                        + ' ' + program['program_class'] + '\n')

        if program['program_manual']:
            test_report += program['program_logic'] + '\n'
            test_report += program['program_reference'] + '\n'

        if not program['program_complex']:
            test_report += program['program_code'] + '\n'
        else:
            test_report += [x for x in program['program_code'].split('\n') if x != ''][-1] + '\n'

        judge = {True : '', False : 'Fail'}

        date_invalid_num = simple_result['date_invalid_num'] < Config['date_invalid_num']
        ic_all_dtc = simple_result['ic_all_dtc'] > (
            Config['ic_all_dtc'][0] if program['program_manual'] else Config['ic_all_dtc'][1])
        ic_all_dt = simple_result['ic_all_dt'] > (
            Config['ic_all_dt'][0] if program['program_manual'] else Config['ic_all_dt'][1])
        ic_all_c = simple_result['ic_all_c'] > (
            Config['ic_all_c'][0] if program['program_manual'] else Config['ic_all_c'][1])
        ic_all_t = simple_result['ic_all_t'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_t'][1])
        ic_all_d = simple_result['ic_all_d'] > (
            Config['ic_all_d'][0] if program['program_manual'] else Config['ic_all_d'][1])
        _top_ret = (simple_result['dtc_all_ret'] + simple_result['t_dc_all_ret'] +
                   simple_result['tc_d_all_ret'] + simple_result['t_c_d_all_ret'])
        top_ret = _top_ret > (Config['top_ret'][0] if program['program_manual'] else Config['top_ret'][1])
        dtc_all_sign = (Config['dtc_all_sign'][0][0] < simple_result['dtc_all_sign'] < Config['dtc_all_sign'][0][1]
                        ) if program['program_manual'] else (Config['dtc_all_sign'][1][0] < simple_result[
            'dtc_all_sign'] < Config['dtc_all_sign'][1][1])
        half_ic = (simple_result['ic_half_dt'] < 0).sum() <= (
            Config['ic_half'][0] if program['program_manual'] else Config['ic_half'][1])

        program['corr_ignore'] = False
        corr = True

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            corr_files2, ic_all_dt_compare, _ = load_pickles(address2, ic_all_dt_every_code, factor_sample)
            corr_max = round(ic_all_dt_compare.max(), 4)

            if corr_max < Config['corr_limit']:
                corr = True
            elif (ic_all_dt_compare >= Config['corr_limit']).sum() > 1:
                corr = False
            else:
                corr_bench = np.arange(len(ic_all_dt_compare)).dot(ic_all_dt_compare >= Config['corr_limit'])
                corr_bench_file = address2, corr_files2[corr_bench]
                corr_bench_ic = load_pickle(corr_bench_file[0] + corr_bench_file[1])
                if (corr_bench_ic['ic_all_dt'] + corr_bench_ic['ic_all_c'] + 2 * corr_bench_ic['ic_all_dtc'] <
                        simple_result['ic_all_dt'] + simple_result['ic_all_c'] + 2 * simple_result['ic_all_dtc']):
                    corr = True
                    corr_bench_ic['corr_ignore'] = True
                    corr_bench_ic['corr_best_file'] = file_time
                    program['corr_bench_file'] = corr_bench_file[1]
                    save_pickle(corr_bench_file[0] + corr_bench_file[1], corr_bench_ic)
                else:
                    corr = False
                    program['corr_bench_file'] = corr_bench_file[1]

        test_report += 'Conclusion'.center(64, '-') + '\n'

        program.update(simple_result)
        program.update({'ic_all_dt_every_code': ic_all_dt_every_code.astype(np.float32)})
        program.update({'factor_sample': factor_sample.astype(np.float32)})
        save_pickle(address0 + file_time, program)

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign & corr:
            test_report += '山重水复疑无路，柳暗花明又一村。\n'
            test_report += 'Congratulations! Your factor test SUCCEEDED as expected!\n'
            program.update(result)
            save_pickle(address2 + file_time, program)

            np.save(factor_address + '%s.npy' % file_time, factor)
        else:
            test_report += '证券投资部是一支年轻的队伍，年轻没有失败。\n'
            test_report += 'We regret to tell you that your factor test FAILED!\n'
            if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
                program.update(result)
                #save_pickle(address1 + file_time, program)

        test_report += 'Details'.center(64, '-') + '\n'

        test_report += 'Factor Direction:'.ljust(18) + str(simple_result['ic_direction']).ljust(6) + '\n'

        test_report += 'Invalid Days:'.ljust(18) + str(simple_result['date_invalid_num']
                                                       ).ljust(6) + ''.ljust(13) + judge[date_invalid_num] +'\n'

        test_report += 'Completeness:'.ljust(18) + str(round(simple_result['factor_complete'], 4)
                                                       ).ljust(6) + '\n'

        test_report += 'Global IC:'.ljust(18) + str(round(simple_result['ic_all_dtc'], 4)
                                                    ).ljust(6) + ''.ljust(13) + judge[ic_all_dtc] +'\n'

        test_report += 'Cross Section IC:'.ljust(18) + str(round(simple_result['ic_all_c'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_c] + '\n'

        test_report += 'Time Series IC:'.ljust(18) + str(round(simple_result['ic_all_dt'], 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[ic_all_dt] +'\n'

        test_report += 'Intraday IC:'.ljust(18) + str(round(simple_result['ic_all_t'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_t] + '\n'

        test_report += 'Interday IC:'.ljust(18) + str(round(simple_result['ic_all_d'], 4)
                                                           ).ljust(6) + ''.ljust(13) + judge[ic_all_d] + '\n'

        test_report += 'Top Return:'.ljust(18) + str(round(_top_ret, 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[top_ret] + '\n'
        test_report += 'Top Ratio:'.ljust(18) + str(round(simple_result['dtc_all_sign'], 4)
                                                     ).ljust(6) + ''.ljust(13) + judge[dtc_all_sign] + '\n'
        _ic_half_dt = list(simple_result['ic_half_dt'].round(4))
        test_report += 'Half Year IC:'.ljust(18) + str(_ic_half_dt[:2]) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[2:4]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[4:6]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[6:8]).ljust(18) + '\n'
        test_report += ''.ljust(18) + str(_ic_half_dt[8:]).ljust(18)
        test_report += '  ' + judge[half_ic] + '\n'

        if date_invalid_num & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            test_report += 'Corr Max:'.ljust(18) + str(round(corr_max, 4)
                                                         ).ljust(6) + ''.ljust(13) + judge[corr] + '\n'
        if 'corr_bench_file' in program:
            test_report += 'Corr Related:'.ljust(18) + program['corr_bench_file'] + '\n'
        test_report += 'The End'.center(64, '*') + '\n'

        if admin == 95238:
            return simple_result
        elif corr & ic_all_dtc & ic_all_dt & ic_all_c & top_ret & half_ic & dtc_all_sign:
            if not noprint:
                print(test_report)
            #send_message(list({'015836', program['program_author']}), test_report)
        else:
            if not noprint:
                print(test_report)

if __name__ == '__main__':


    ft = FactorTest()
    address2 = '/data/group/800442/800319/junkBigFactorPool/level2_waiting/'
    fold = '/data/group/800442/800319/junkBigFactorPool/%s/' % ft.fold
    wait_programs = sorted([x for x in os.listdir(address2) if x.isdigit()])
    finished_program = [load_pickle(fold + x)['raw_file'] for x in os.listdir(fold)]
    wait_programs = sorted(list(set(wait_programs) - set(finished_program)))

    def batch_test(programs, line=0):

        for name in programs:

            program = load_pickle(address2 + name)
            new_program = {x : program[x] for x in program.keys() if x[:7] == 'program'}
            if 'complex_simplified' in program:
                new_program.update({'complex_simplified': program['complex_simplified']})
            new_program['raw_file'] = name
            ft.test_all_program(new_program)

    multidask(24, batch_test, wait_programs)


if __name__ == '__main__':

    import pandas as pd
    ft = FactorTest()
    #wait_programs = df5.name.to_list()
    address = '/data/group/800442/800319/junkBigFactorPool/level0_unfinished/202012031314/'
    wait_programs = sorted([x for x in os.listdir(address) if x.isdigit()])
    finished = pd.read_pickle('/data/user/015836/20201203good_factor_select')['name'].to_list()
    wait_programs = sorted(list(set(wait_programs) - set(finished)))
    def batch_test(programs, line=0):

        for name in programs:

            program = load_pickle(address + name)
            new_program = {x : program[x] for x in program.keys() if x[:7] == 'program'}
            if 'complex_simplified' in program:
                new_program.update({'complex_simplified': program['complex_simplified']})
            new_program['raw_file'] = name
            ft.test_factor(new_program)

    multidask(24, batch_test, wait_programs)


