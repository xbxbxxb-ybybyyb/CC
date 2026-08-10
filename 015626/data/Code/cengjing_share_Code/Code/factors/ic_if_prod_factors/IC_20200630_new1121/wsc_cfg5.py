import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg5(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg5, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_zz500', 'weight_boolean_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 选取每个截面上过去3分钟收益率最高的前10%的股票，然后求它们的加权交易额（权重为weight）
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amt = data['amount_zz500']
        stk_ret = stk_close.pct_change(3, fill_method=None)[bool_mask]
        stk_ret_long = stk_ret.gt(stk_ret.quantile(0.9, axis=1), axis=0)
        factor = stk_amt[stk_ret_long]#.rolling(30, min_periods=20).mean()
        # factor = stk_ret.rolling(30*2, min_periods=15).cov(stk_amt)
        factor = (factor * data['weight_zz500']).sum(axis=1)
        #factor = factor.rolling(5, min_periods=1).mean()
        factor = factor.rolling(20, min_periods=7).mean()

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 200*6)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        # factor[factor<=-0.5] = np.nan
        #factor[factor>=0.5] = np.nan
        return factor
