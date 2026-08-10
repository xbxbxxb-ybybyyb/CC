from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor


import talib
class fast_fac_4_df(FutureFactor): 
    
    def __init__(self, ticker, freq = 1):
        super().__init__()
        self.ticker = ticker
        self.freq = freq

        self.days_past = int(freq) * 1 # different product should be different
        self.required_columns = ['close']        
        self.normalize_size = int(3000/self.freq)
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        
    def calculate(self, data):
        unit = self.freq
        aaa = nanmax_np([2, int(5 / unit)])
        bbb = int(20 / unit)
        ccc = int(3000 / unit)
        coef = self.bars_dict[self.ticker]/self.freq        
        fac_raw1 = talib.LINEARREG_ANGLE(data['close'][-aaa:],aaa)[-1]
        fac_raw2 = talib.LINEARREG_ANGLE(data['close'][-bbb:],bbb)[-1]
        factor = 3 * fac_raw2 - fac_raw1
        return factor
        