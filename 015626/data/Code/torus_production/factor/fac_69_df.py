from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import bottleneck as bk

def cci(typical_price, time_period=14):
    typical_price_ma = move_mean_bk(typical_price,window = time_period, min_count = int(time_period/2))
    tmp = abs(typical_price - typical_price_ma)
    typical_price_mean_deviation = move_mean_bk(tmp,window = time_period,min_count = int(time_period/2))
    price_cci = (typical_price - typical_price_ma) / (typical_price_mean_deviation)
    return price_cci

class fac_69_df(FutureFactor): 
    
    def __init__(self,ticker,freq = 1):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 1 # different product should be different
        self.required_columns = ['close_secmain']        
        self.normalize_size = 1500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.hclose_list = []
        
    def calculate(self, data):
        cls = data['close_secmain'][-200:]
        hlow = move_min_bk(cls,window=30,min_count=15)
        hclose = cls
        lltc_ind_r = -(hlow- (hclose))
        cls_diff = cls[1:] - cls[:-1]
        co = nanstd_np(cls_diff[-10:],ddof = 1)
        if abs(co) < 1e-8:
            co = np.nan
        #co = move_std_bk(cls_diff,window = 10, min_count=1)
        fac_raw = lltc_ind_r + move_mean_bk(lltc_ind_r,window=5,min_count=1)
        fac_cci = cci(fac_raw, 60)[-1]
        factor = fac_cci / co
        return factor