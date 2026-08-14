import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.tradeDate import get_date_range, get_trade_date_interval, get_pre_trade_date
from HFfactor.MinFactorSuper.Utility.LoadBigData import load_material
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import get_numpy_head
from HFfactor.MinFactorSuper.Utility.MachineFactor import get_program_factor
from HFfactor.MinFactorSuper.RealTime.UsefulList import ResearchMinuteList
from HFfactor.MinFactorSuper.RealTime.Operators import *
import numpy as np
import bottleneck
import time
import gc
import os
import re


class FactorVal(object):

    def __init__(self, test_start_date=20140701, end_date=20150630, test_drop_days=80, standardize_days=40,
                 reduce=False, stock_pool='stock_pool', store='FactorData',
                 address='/arch1/group/800442/800319/MinFactorSuper/'):
        test_date_list = get_date_range(test_start_date, end_date)
        test_start_date = test_date_list[0]
        end_date = test_date_list[-1]
        calc_start_date = get_pre_trade_date(test_start_date, test_drop_days)
        _stock_pool = load_material(stock_pool, test_start_date, end_date, address=address)

        idx_date = np.load(f'{address}/{store}/Label/idx_date.npy')
        idx_time = np.load(f'{address}/{store}/Label/idx_time.npy')
        if reduce:
            idx_time = [ResearchMinuteList[6:-1:5].index(x) for x in idx_time]
        else:
            idx_time = [231 if x not in ResearchMinuteList[4: -6] else
                        ResearchMinuteList[4: -6].index(x) - 1 for x in idx_time]
        store_drop_days = max(get_trade_date_interval(idx_date[0], test_start_date) + 1, 0)
        if get_pre_trade_date(test_start_date) > idx_date[0]:
            old_pool = load_material(stock_pool, idx_date[0], get_pre_trade_date(test_start_date), address)
            old_shape = old_pool.sum()
            offset = old_shape * len(idx_time) * 4 + 128
        else:
            offset = 128
            old_shape = 0
        shape = (_stock_pool[store_drop_days:].sum(), len(idx_time))
        head = get_numpy_head((shape[0] + old_shape, shape[1]), 'float32')
        idx_time_diff = np.arange(len(idx_time) - 1)[np.diff(np.array(idx_time)) < 0]
        idx_time = slice(None) if idx_time == list(range(47 if reduce else 232)) else idx_time
        if idx_time_diff.shape[0]:
            calc_start_date = get_pre_trade_date(calc_start_date)
        if not os.path.exists(f'{address}/{store}/Factor/'):
            os.makedirs(f'{address}/{store}/Factor/')
        calc_date_list = get_date_range(calc_start_date, end_date)
        test_date_num = len(test_date_list)
        calc_date_num = len(calc_date_list)

        self._calc_start_date = calc_start_date
        self._end_date = end_date
        self._stock_pool = _stock_pool
        self.stock_pool = _stock_pool
        self._calc_date_num = calc_date_num
        self._test_date_num = test_date_num
        self._test_start_date = test_start_date
        self._standardize_days = standardize_days
        self._test_drop_days = test_drop_days
        self._store_drop_days = store_drop_days
        self._idx_time_diff = idx_time_diff
        self._idx_time = idx_time
        self._offset = offset
        self._shape = shape
        self._head = head
        self._store = store
        self._address = address
        self._reduce = reduce
        self.Material = {}

    def _factor_mv(self, factor):
        factor_finite = np.isfinite(factor)
        bottleneck2.clip_array_3d(factor)
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = bottleneck2.dt_sum(d_cf, self._standardize_days)
        rd_cf2 = bottleneck2.dt_sum(d_cf2, self._standardize_days)
        rd_cn = bottleneck.move_sum(d_cn.astype('float32'), self._standardize_days, axis=0)
        rd_cn[rd_cn < self._standardize_days * factor.shape[1] / 2] = np.nan

        rd_mean = rd_cf / rd_cn
        rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
        rd_std[rd_std == 0] = np.nan

        rd_mean = rd_mean[self._test_drop_days - 1: -1]
        rd_std = rd_std[self._test_drop_days - 1: -1]
        return rd_mean, rd_std

    def factor_calc(self, factor):
        factor_finite = np.isfinite(factor)
        bottleneck2.clip_array_3d(factor)
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = bottleneck2.dt_sum(d_cf, self._standardize_days)
        rd_cf2 = bottleneck2.dt_sum(d_cf2, self._standardize_days)
        rd_cn = bottleneck.move_sum(d_cn.astype('float32'), self._standardize_days, axis=0)
        rd_cn[rd_cn < self._standardize_days * factor.shape[1] / 2] = np.nan

        rd_mean = rd_cf / rd_cn
        rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
        rd_std[rd_std == 0] = np.nan

        factor[~ factor_finite] = np.nan
        factor = (factor[self._test_drop_days:] - rd_mean[self._test_drop_days - 1: -1, None]
                  ) / rd_std[self._test_drop_days - 1: -1, None]
        factor = factor[:, :-1].clip(-6, 6) if self._reduce else factor[:, 4: -6].clip(-6, 6)
        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0
        return factor

    def factor_val(self, factor_line):
        name, program = factor_line[0], factor_line[1]
        program = program.replace('\n', '').replace(' ', '').replace(',', ', ')
        for basic_factor in get_program_factor(program):
            if basic_factor not in self.Material:
                self.Material[basic_factor] = load_material(
                    basic_factor, self._calc_start_date, self._end_date, self._reduce)
        replace = lambda x: x[1] + ("self.Material['%s']") % x[2] + x[3]
        program1 = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, program)
        factor = eval(program1)
        factor = self.factor_calc(factor)
        return factor

    def factor_mv(self, factor_line):
        name, program = factor_line[0], factor_line[1]
        program = program.replace('\n', '').replace(' ', '').replace(',', ', ')
        for basic_factor in get_program_factor(program):
            if basic_factor not in self.Material:
                self.Material[basic_factor] = load_material(
                    basic_factor, self._calc_start_date, self._end_date, self._reduce)
        replace = lambda x: x[1] + ("self.Material['%s']") % x[2] + x[3]
        program1 = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, program)
        factor = eval(program1)
        mean, std = self._factor_mv(factor)
        return mean, std

    def factor_store(self, factor_line):
        name, program = factor_line[0], factor_line[1]
        factor = self.factor_val(factor_line)
        print(time.strftime('%Y-%m-%d %H:%M:%S'), name, f'{self._test_start_date}-{self._end_date}')
        if self._idx_time_diff.shape[0]:
            pre_idx_time = self._idx_time[: self._idx_time_diff[0] + 1]
            idx_time = self._idx_time[self._idx_time_diff[0] + 1:]
            factor = np.concatenate([factor[self._store_drop_days:-1, pre_idx_time],
                                     factor[self._store_drop_days + 1:, idx_time]], axis=1)
        else:
            factor = factor[self._store_drop_days:, self._idx_time]
        factor = factor.transpose(0, 2, 1)[self._stock_pool[self._store_drop_days:, 0]]
        if not os.path.exists(f'{self._address}/{self._store}/Factor/{name}.npy'):
            np.save(f'{self._address}/{self._store}/Factor/{name}.npy', np.array([], dtype='float32'))
        fp = np.memmap(f'{self._address}/{self._store}/Factor/{name}.npy',
                       dtype='uint8', mode='r+', offset=0, shape=128)
        fp[:] = self._head
        del fp
        fp = np.memmap(f'{self._address}/{self._store}/Factor/{name}.npy',
                       dtype='float32', mode='r+', offset=self._offset, shape=self._shape)
        fp[:] = factor[:]
        del fp, factor
        gc.collect()
        # print(time.strftime('%Y-%m-%d %H:%M:%S'), name, f'{self._test_start_date}-{self._end_date}')#TODO


if __name__ == '__main__':
    import pandas as pd
    from HFfactor.MinFactorSuper.Utility.Parallel import multidask
    from HFfactor.MinFactorSuper.Utility.LoadBigData import make_label, make_idx
    # make_idx(13, 'stock_pool', 'FactorFixData')
    # make_label('stock_pool', 'FactorFixData')
    # time.sleep(4000)
    # time.sleep(3000)
    fv = FactorVal(20140701, 20201231, reduce=True, store='FactorFixData')
    desample_factor_list = pd.read_pickle(
        '/data/group/800442/800319/strategy_HFfactor3/20210722/DateCode/desample_factor_list.pkl')
    def _func(sub_list):
        for factor_line in sub_list:
            fv.factor_store(factor_line)
    multidask('calc_5m', [[_func, (desample_factor_list[x::24],)] for x in range(24)])
    del fv
    gc.collect()
    fv = FactorVal(20210101, 20210901, reduce=True, store='FactorFixData')
    desample_factor_list = pd.read_pickle(
        '/data/group/800442/800319/strategy_HFfactor3/20210722/DateCode/desample_factor_list.pkl')
    def _func(sub_list):
        for factor_line in sub_list:
            fv.factor_store(factor_line)
    multidask('calc_5m', [[_func, (desample_factor_list[x::24],)] for x in range(24)])
    del fv
    gc.collect()

    # for year in [2014, 2015, 2016, 2017, 2018, 2019, 2020]:#TODO
    for year in [2014]:
        start = year * 10000 + 701
        end = year * 10000 + (10630 if year < 2021 else 10901)
        fv = FactorVal(start, end, reduce=False, store='FactorFixData')
        factor_list = pd.read_pickle('/data/group/800442/800319/strategy_HFfactor2/20210823_old/DateCode/factor_list.pkl')
        def _func(sub_list):
            for factor_line in sub_list:
                fv.factor_store(factor_line)
        multidask('calc_1m', [[_func, (factor_list[x::24],)] for x in range(24)])
        del fv
        gc.collect()