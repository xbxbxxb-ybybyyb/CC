from dataApi.tradeDate import get_date_range, get_pre_trade_date
from HFfactor.MinFactorLab.RealTime.UsefulList import MaterialList
from HFfactor.MinFactorLab.Research.AnalyseProgram import get_program_factor, analyse_program
from HFfactor.MinFactorLab.RealTime.Operators import *
import pandas as pd
import numpy as np
import gc
import re
import warnings

warnings.filterwarnings("ignore")


def load_material(name, start_date, end_date, address='/arch1/group/800442/800319/MinFactor/'):
    middle_name = 'Material' if name in MaterialList else 'Label'
    middle_len = 1 if 'stock_pool' in name else 242
    unit_size = 1 if ('stock_pool' in name) or (name == 'limit_status') else 4
    dtype = 'bool' if ('stock_pool' in name) or (name == 'limit_status') else 'float32'
    code_num = len(pd.read_pickle(f'{address}/DateCode/code_list.pkl'))
    date_list = np.load(f'{address}/DateCode/date_list.npy').tolist()
    start_idx = date_list.index(start_date)
    end_idx = date_list.index(end_date)
    offset = 128 + start_idx * middle_len * code_num * unit_size
    shape = (end_idx - start_idx + 1, middle_len, code_num)
    arr = np.empty(shape, dtype=dtype)
    fp = np.memmap(f'{address}/{middle_name}/{name}.npy', dtype=dtype, offset=offset, shape=shape)
    arr[:] = fp[:]
    del fp
    return arr


class SimpleFactorVal(object):

    def __init__(self, test_start_date=20140701, end_date=20150630, test_drop_days=80, standardize_days=40,
                 stock_pool='stock_pool', store='FactorData', address='/arch1/group/800442/800319/MinFactor/'):

        test_date_list = get_date_range(test_start_date, end_date)
        test_start_date = test_date_list[0]
        end_date = test_date_list[-1]
        calc_start_date = get_pre_trade_date(test_start_date, test_drop_days)
        _stock_pool = load_material(stock_pool, test_start_date, end_date, address)

        calc_date_list = get_date_range(calc_start_date, end_date)
        test_date_num = len(test_date_list)
        calc_date_num = len(calc_date_list)

        self._calc_start_date = calc_start_date
        self._end_date = end_date
        self._stock_pool = _stock_pool
        self._calc_date_num = calc_date_num
        self._test_date_num = test_date_num
        self._standardize_days = standardize_days
        self._test_drop_days = test_drop_days
        self._store = store
        self._address = address
        self.Material = {}

    def __factor_val(self, factor):
        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = bottleneck.move_sum(d_cf, self._standardize_days, axis=0)
        rd_cf2 = bottleneck.move_sum(d_cf2, self._standardize_days, axis=0)
        rd_cn = bottleneck.move_sum(d_cn.astype('float32'), self._standardize_days, axis=0)
        rd_cn[rd_cn < self._standardize_days * 242 / 2] = np.nan

        rd_mean = rd_cf / rd_cn
        rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
        rd_std[rd_std == 0] = np.nan

        factor = (factor[self._test_drop_days:] - rd_mean[self._test_drop_days - 1: -1, None]
                  ) / rd_std[self._test_drop_days - 1: -1, None]
        factor = factor.clip(-6, 6)
        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0
        return factor

    def factor_val(self, program):
        program = program.replace('\n', '').replace(' ', '').replace(',', ', ')
        for basic_factor in get_program_factor(program):
            if basic_factor not in self.Material:
                self.Material[basic_factor] = load_material(
                    basic_factor, self._calc_start_date, self._end_date)
        replace = lambda x: x[1] + ("self.Material['%s']") % x[2] + x[3]
        program = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, program)
        factor = eval(program)
        factor = self.__factor_val(factor)
        gc.collect()
        return factor


if __name__ == '__main__':
    ft = SimpleFactorVal(20200715, 20210715)
    factor = ft.factor_val('ts_cumsum(ret_close)')