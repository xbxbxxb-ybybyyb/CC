from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA



class fac_47_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * int(self.freq))
        self.required_columns = [ 'close', 'volume', 'high', 'low']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 3000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__

        self.index_close_list = []
        self.log_ret_weight_list = []
        self.log_ret_list = []
        self.factor_raw_list = []

    
    def calculate(self, data):
        aaa = 30
        bbb = 5
        ccc = 12
        ddd = 10
        
        norm_price = (data['close'][-1:] + data['high'][-1:] + data['low'][-1:]) / 3
        index_close = nanmean_np(norm_price)
        self.index_close_list.append(index_close)
        index_volume = nanmean_np(data['volume'][-1:])
        
        log_ret = (self.index_close_list[-1] - self.index_close_list[-2])
        self.log_ret_list.append(log_ret)
        ret_std = nanstd_np(self.log_ret_list[-aaa:], ddof = 1)
        log_ret_weight = log_ret / r(index_volume) * ret_std
        self.log_ret_weight_list.append(log_ret_weight)
        factor_raw = nansum_np(self.log_ret_weight_list[-bbb:])
        self.factor_raw_list.append(factor_raw)
        factor_mean = ema_1(self.factor_raw_list[-ccc*3:], ccc*3, 1/(ccc+1))
        return factor_mean


    
    def pre_calculate(self, data):
        aaa = 30
        bbb = 5
        ccc = 12
        ddd = 10
        
        for i in range(100, -1, -1):
            if i == 0:
                norm_price = (data['close'][-1:] + data['high'][-1:] + data['low'][-1:]) / 3
                index_close = nanmean_np(norm_price)
                index_volume = nanmean_np(data['volume'][-1:])
                self.index_close_list.append(index_close)
            else:
                norm_price = (data['close'][-1 - i: -i] + data['high'][-1- i: -i] + data['low'][-1- i: -i]) / 3
                index_close = nanmean_np(norm_price)
                index_volume = nanmean_np(data['volume'][-1- i: -i])
                self.index_close_list.append(index_close)


            if len(self.index_close_list) > 1:
                log_ret = (self.index_close_list[-1] - self.index_close_list[-2])
                self.log_ret_list.append(log_ret)
                ret_std = nanstd_np(self.log_ret_list[-aaa:], ddof = 1)
                log_ret_weight = log_ret / r(index_volume) * ret_std
                self.log_ret_weight_list.append(log_ret_weight)
                factor_raw = nansum_np(self.log_ret_weight_list[-bbb:])
                self.factor_raw_list.append(factor_raw)
