from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti20_cfg_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti20_cfg_if, self).__init__(required_columns=['close_hs300', 'high_hs300', 'low_hs300'],
                                              lookback_bars=2000)

    def on_bar(self, data_dict):
        # mfi技术指标
        stk_low = data_dict['low_hs300']
        stk_close = data_dict['close_hs300']
        stk_high = data_dict['high_hs300']
        price1 = (stk_high + stk_low + stk_close) / 3
        amount1 = price1 * stk_volume
        amount2 = amount1.copy()
        n = 20
        price1_diff = ts_delta(price1, 1)
        amount1[price1_diff<0] = 0
        amount2[price1_diff>0] = 0
        a = ts_sum(amount1.sum(axis=1), n)
        b = ts_sum(amount2.sum(axis=1), n)
        b = replace_zero(b)
        factor_raw = (100 - 100 / (1 + a/b))
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor