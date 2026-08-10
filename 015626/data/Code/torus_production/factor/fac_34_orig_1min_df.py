from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np



class fac_34_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker # 'AG.SHF', 'A.DCE'
        self.freq = freq # 1, 3, 5, 15

        self.days_past = 1 * freq
        self.required_columns = ['close', 'open', 'high', 'low']
        self.normalize_size = 3 * self.bars_dict[ticker]
        self.normalize_type = 'ts_rank'
        
        self.factor_name = self.__class__.__name__
        # 定义预计算缓存序列，想定义几个就定义几个
        self.t_pcor2_list = []
        self.t_pcor2_10_list = []
    
    def calculate(self, data):
        mean_num = 5
        hh = nanmax_np(data['high'][-mean_num:]) - nanmin_np(data['low'][-mean_num:])
        if abs(hh) < 1e-8:
            hh = np.nan
        temp = -1 * (nanmean_np(data['open'][-mean_num:]) - data['close'][-1]) / hh
        temp = 0 if np.isinf(temp) else temp
        self.t_pcor2_list.append(temp)
        self.t_pcor2_list = self.t_pcor2_list[-15:]
        
        self.t_pcor2_10_list.append(nanmean_np(self.t_pcor2_list))
        self.t_pcor2_10_list = self.t_pcor2_10_list[-100:]
        return ema_1(self.t_pcor2_10_list, 100, 1/46)

    def pre_calculate(self, data):
        self.t_pcor2_list = []
        self.t_pcor2_10_list = []
    
        mean_num = 5
        for i in range(121):
            if i == 0:

                hh = nanmax_np(data['high'][-(i + mean_num):]) - nanmin_np(data['low'][-(i + mean_num):])
                if abs(hh) < 1e-8:
                    hh = np.nan
                if len(data['close']) > i +1:
                    _t = data['close'][-(i+1)]
                else:
                    if len(data['close']) == 0:
                        _t = np.nan
                    else:
                        _t = data['close'][0]
                temp = -1 * (nanmean_np(data['open'][-(i + mean_num):]) - _t) / hh
            else:

                hh = nanmax_np(data['high'][-(i + mean_num):-i]) - nanmin_np(data['low'][-(i + mean_num):-i])
                if abs(hh) < 1e-8:
                    hh = np.nan
                if len(data['close']) > i +1:
                    _t = data['close'][-(i+1)]
                else:
                    if len(data['close']) == 0:
                        _t = np.nan
                    else:
                        _t = data['close'][0]
                temp = -1 * (nanmean_np(data['open'][-(i + mean_num):-i]) - _t) / hh
            temp = 0 if np.isinf(temp) else temp
            self.t_pcor2_list.append(temp)
        self.t_pcor2_list.reverse()
        n = 15
        for i in range(121):
            if i == 0:
                self.t_pcor2_10_list.append(nanmean_np(self.t_pcor2_list[-n:]))
            else:
                self.t_pcor2_10_list.append(nanmean_np(self.t_pcor2_list[-(i+n):-i]))
        self.t_pcor2_10_list.reverse()