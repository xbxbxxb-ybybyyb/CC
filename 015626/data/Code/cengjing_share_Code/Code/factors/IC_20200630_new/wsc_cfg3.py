import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg3(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg3, self).__init__(required_columns=['close_zz500', 'close_spot', 'weight_zz500'],
                                       lookback_bars=2000)

    def on_bar(self, data):
        # 比较过去一段时间成分股和指数收益率大小，统计那一分钟涨幅小于指数的成分股数量
        index_return = data['close_spot'].pct_change(periods=60, fill_method=None)
        stock_return = data['close_zz500'].pct_change(periods=60, fill_method=None)
        excess_return = (stock_return.subtract(index_return, axis=0))  # .skew(axis=1)
        excess_return_weight = data['weight_zz500'][excess_return < 0].sum(axis=1)
        excess_return_weight = excess_return_weight.rolling(10, min_periods=5).mean()

        factor = excess_return_weight.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 1200)
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
