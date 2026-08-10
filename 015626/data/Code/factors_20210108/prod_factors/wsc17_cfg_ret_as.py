import pandas as pd
import numpy as np
import bottleneck as bk
from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc17_cfg_ret_as(FactorGeneratorComplex):
    def __init__(self):
        super(wsc17_cfg_ret_as, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                               lookback_bars=2000)

    def on_bar(self, data):
        # 长江金工高频因子八，偏度因子
        # 计算close的偏度，偏度＞0时，大于价格均值的价格比小于价格均值的价格少，个股成交集中在价格相对较低的水平，反之亦然，因此认为偏度越小的股票未来价格更可能上升。
        # 取当分钟rolling_skew前50%的股票，计算它们的过去一分钟return，作为因子值，再套相应的mask，因为每期选出的票都不一样，所以为了时序上可比，要做一定的归一化处理。
        bool_mask = data['weight_boolean_zz500']
        stk_close = data['close_zz500']
        stk_amount = data['amount_zz500']
        stk_ret = ts_pct_change(stk_close, 1)[bool_mask]
        stk_skew = ts_skew(stk_close, 30)[bool_mask]
        skew_long = stk_skew.gt(stk_skew.quantile(0.5, axis=1), axis=0)
        factor_init = stk_ret[skew_long]

        factor_raw = (factor_init * stk_amount).sum(axis=1) / (stk_amount * skew_long).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = rolling_norm(factor_mean, 1200)

        factor = factor.to_frame()
        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
