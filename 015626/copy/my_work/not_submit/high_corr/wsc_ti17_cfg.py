from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti13_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti13_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'open_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # imi技术指标
        stk_close = data_dict['close_zz500']
        stk_open = data_dict['open_zz500']
        stk_weight = data_dict['weight_zz500']
        n = 20
        a = stk_close - stk_open
        a[a<0] = 0
        b = stk_open - stk_close
        b[b<0] = 0
        inc = ts_sum(a, n)
        dec = ts_sum(b, n)
        factor_raw = (inc / replace_zero(inc + dec) * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor