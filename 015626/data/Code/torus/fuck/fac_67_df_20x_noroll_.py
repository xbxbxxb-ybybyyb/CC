from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import bottleneck as bk



class fac_67_df_20x_noroll_(FutureFactor): 
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 9
        self.required_columns = ['close']
        self.normalize_size = int(self.bars_dict[ticker] * 50 / freq)
        normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        
    def calculate(self, data):
        cls = data['close'][-2000:]
        cls_diff = cls[1:] - cls[:-1]
        cls_diff_std = nanstd_np(cls_diff[-300:],ddof = 1)
        cls_diff_aaa = cls[60:] - cls[:-60]
        cls_diff_sign = np.sign(cls_diff_aaa)
        cls_diff_aaa_std = move_sum_bk(cls_diff_aaa ** 2, window = 1000, min_count = 500)
        factor_raw = cls_diff_sign * cls_diff_aaa_std
        
        factor_ema = ema_1(factor_raw[-900:], 900, 1/301)
        if abs(cls_diff_std) < 1e-7:
            cls_diff_std = np.nan
        factor = factor_ema / cls_diff_std
        return factor