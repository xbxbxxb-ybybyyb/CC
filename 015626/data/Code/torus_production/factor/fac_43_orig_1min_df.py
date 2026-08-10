from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np
import numpy as np
from numba import njit
from utils_zsj import SMA
#@njit
def SMA1(x, n, m):
    """
    Y(t) = (A(t)*m + Y(t-1)*(n-m))/n
    fill value"""
    N = len(x)
    y = np.zeros(N)
    for i in range(N):
        if i == 0:
            y[i] = x[i]
        else:
            y[i] = (y[i-1]*(n-m) + x[i] * m) / n

    return y[-1]

def cross_hub_num_array(data_array, d):
    # 过去一段时间曲线穿越中枢的次数
    data_centralized = data_array - move_mean_bk(data_array,window = d,min_count = int(d/2))
    flag = (data_centralized[1:] * data_centralized[:-1]) < 0
    output = nansum_np(flag[-d:])
    return output
    
class fac_43_orig_1min_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(2 * int(self.freq))
        self.required_columns = ['high', 'low', 'close', 'dt']
        self.instrument_type = 'main' #second_main
        self.normalize_size = int(int(self.bars_dict[self.ticker] / int(self.freq)) * 3)
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.high_list = []
        self.low_list = []
        self.ulb_list = []
        self.ulb_zscore_list = []

    
    def calculate(self, data):

        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        dhigh = nanmax_np(data['high'][-2:])
        dlow = nanmin_np(data['low'][-2:])
        dclose = data['close'][-21:]
        self.high_list.append(dhigh)
        self.low_list.append(dlow)
        roll_win = 15
        ma_win = int(coef / 4)
        upper = SMA1(self.high_list[-roll_win * 6:], roll_win, 1)
        lower = SMA1(self.low_list[-roll_win * 6:], roll_win, 1)
        ulb = upper - lower
        self.ulb_list.append(ulb)
        
        ulb_avg = nanmean_np(np.array(self.ulb_list[-roll_win:]))
        ulb_std = nanstd_np(np.array(self.ulb_list[-roll_win:]), ddof = 1)
        mid = (upper + lower) / 2
        ulb_zscore = ((dclose[-1] - mid) - ulb_avg) / r(ulb_std)
        self.ulb_zscore_list.append(ulb_zscore)
        ulb_zscore_mean = nanmean_np(self.ulb_zscore_list[-ma_win:])
        return ulb_zscore_mean

        
        
        
    def pre_calculate(self, data):
        coef = int(self.bars_dict[self.ticker] / int(self.freq))
        roll_win = 15
        ma_win = int(coef / 4)

        
        for i in range(300, -1, -1):
            if len(data['high']) < 2 + i:
                self.high_list.append(np.nan)
                self.low_list.append(np.nan)
                self.ulb_list.append(np.nan)
                continue
            if i == 0:
                dhigh = nanmax_np(data['high'][-2:])
                dlow = nanmin_np(data['low'][-2:])
                dclose = data['close'][-21:]
                ddt = data['dt'][-1]

            else:
                dhigh = nanmax_np(data['high'][-2 - i: -i])
                dlow = nanmin_np(data['low'][-2 - i: -i])
                dclose = data['close'][-21 - i:-i]
                ddt = data['dt'][-1 - i]


            self.high_list.append(dhigh)
            self.low_list.append(dlow)
            roll_win = 15
            ma_win = int(coef / 4)
            upper = SMA1(self.high_list[-roll_win * 6:], roll_win, 1)
            lower = SMA1(self.low_list[-roll_win * 6:], roll_win, 1)
            ulb = upper - lower
            self.ulb_list.append(ulb)
            
            ulb_avg = nanmean_np(np.array(self.ulb_list[-roll_win:]))
            ulb_std = nanstd_np(np.array(self.ulb_list[-roll_win:]), ddof = 1)
            mid = (upper + lower) / 2
            ulb_zscore = ((dclose[-1] - mid) - ulb_avg) / r(ulb_std)
            self.ulb_zscore_list.append(ulb_zscore)
