import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num
from operators_all_wsc import cci

# vma_std
class fac_44_2_df(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'open', 'main_mask']

        super(fac_44_2_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        aaa = 10
        bbb = 40
        ccc = 1
        mask = data['main_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        ts_open = data['open']

        def calc_vma(high, low, ts_open, close, roll_win=20, mask = mask):
            price = (high + low + ts_open + close) / 4
            vma = price.rolling(roll_win, min_periods = 1).mean()
            vma_diff = close.rolling(3, min_periods = 1).mean() - vma
            return vma_diff[mask].mean(axis = 1)

        factor_name = 'vma_std'
        roll_win = aaa
        std_win = bbb
        ts_pct_win = 300 * ccc
        score = calc_vma(high, low, ts_open, close, roll_win)
        co = (cross_hub_num(data['close'], 30)[mask].mean(axis = 1)) + 1
        vol = data['close'].diff().rolling(20, min_periods = 1).std()[mask].mean(axis = 1)
        score = score + score.rolling(std_win, min_periods = 1).mean()
        vma_std = ts_rank(cci(score/co/r(vol), 120), ts_pct_win)
        hclose = data['close'][mask].mean(axis = 1)
        coef = int(np.nanmedian(mask.groupby(mask.index.date).count()))
        cs = vma_std.rolling(int(coef/ 2), min_periods = 5).corr(hclose)
        cl = vma_std.rolling(int(coef * 2) ,min_periods = 5).corr(hclose)
        vma_std[(cs <cl) | (cl < 0)] = 0
        ##### format factor #####
        vma_std.name = self.__class__.__name__
        factor = pd.DataFrame(vma_std)
        return factor
