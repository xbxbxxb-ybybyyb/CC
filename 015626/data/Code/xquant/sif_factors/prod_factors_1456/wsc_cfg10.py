import pandas as pd
import numpy as np
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_cfg10(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_cfg10, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'close_spot', 'weight_boolean_zz500'],
                                        lookback_bars=2000)

    def on_bar(self, data):
        # 计算截面上过去15分钟涨幅最大的前10%的股票加权平均涨幅（权重为weight）
        bool_mask = data['weight_boolean_zz500']
        close = data['close_zz500']
        ret = close.pct_change(15, fill_method=None)[bool_mask]
        # ret_mean = ret.mean(axis=1)
        # ret_std = ret.std(axis=1)
        ret_flag = ret.gt(ret.quantile(0.9, axis=1), axis=0)
        ret_long = ret[ret_flag]
        weight_long = data['weight_zz500'][ret_flag]
        # factor = factor.rolling(10, min_periods=5).mean()
        # factor = factor.sum(axis=1)

        factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - data['close_spot'].pct_change(15, fill_method=None)
        # factor = ((ret_long * data['weight_zz500']).sum(axis=1)) / weight_long.sum(axis=1) - (ret * data['weight_zz500']).sum(axis=1)
        factor = factor.rolling(15, min_periods=2).mean()
        factor = factor.to_frame()   
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[columnname] = ts_rank(factor, 300*4)
        # factor.to_excel('/data/user/017024/count_ts.xlsx')
        #factor[factor<=-0.5] = np.nan
        # factor[factor>0] = 0
        return factor
