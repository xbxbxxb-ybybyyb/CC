from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import bottleneck as bk
def ema_1(factor_array,d,alpha):
    factor_array = np.array(factor_array)
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    flag = np.isnan(factor_array) | np.isnan(weight)
    flag1 = np.sum(flag, axis=-1)  # 缺失值个数
    flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
    factor_array[flag] = np.nan
    weight[flag] = np.nan
    factor = nansum_np(factor_array[-d:] * weight) / nansum_np(weight) # truncate_ema_1
    return factor

def ema_span_1(factor_array, d, span):
    return ema_1(factor_array, d = d, alpha=2 / (span + 1))

class fac_66_orig_1min_df(FutureFactor): 

    def __init__(self,ticker, freq = 1):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 11
        self.required_columns = ['close']        
        self.normalize_size = 2000
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        #self.unit = 0
    
    def calculate(self, data):
        cls = data['close'][-2560:]
        pct = cls[1:]/cls[:-1]-1
        cls = cls[-160:]
        # calc unit
        short_window = 10
        long_window = 30
        vol_threshold = 15
        
        short_ma = move_mean_bk(cls,window=short_window,min_count=short_window) # need 3
        long_ma = move_mean_bk(cls,window=long_window,min_count=long_window) # need 25
        volatility = move_std_bk(pct,window = vol_threshold, min_count = vol_threshold) # need 10        
        vol_median = move_median_bk(volatility,window = 2400,min_count = 600) 
        vol_id = volatility.copy()
        vol_id[volatility - vol_median < 1e-8] = 1
        vol_id[volatility - vol_median > 1e-8] = 0
        
        short_ma = short_ma[-120:]
        long_ma = long_ma[-120:]
        vol_id = vol_id[-120:]
        ma_cross_distance = (short_ma - long_ma) / long_ma * vol_id
        ma_cross_distance_ema_span1 = ema_span_1(ma_cross_distance[-30:],30,10)
        ma_cross_distance_ema_span2 = ema_span_1(ma_cross_distance[-120:],120,40)        
        factor = 0.5 * ma_cross_distance[-1] + ma_cross_distance_ema_span1 +  2 * ma_cross_distance_ema_span2
        return factor