from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import replace_zero
from operators_wsc import *



class wsc_ti20_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti20_cfg, self).__init__(required_columns=['close_zz500', 'high_zz500', 'low_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # mfi技术指标
        stk_close = data_dict['close_zz500']
        stk_high = data_dict['high_zz500']
        stk_low = data_dict['low_zz500']
        stk_volume = data_dict['volume_zz500']
        price1 = (stk_high + stk_low + stk_close) / 3
        amount1 = price1 * stk_volume
        amount2 = amount1.copy()
        n = 30
        price1_diff = ts_delta(price1, 1)
        amount1[price1_diff<0] = 0
        amount2[price1_diff>0] = 0
        a = ts_sum(amount1.sum(axis=1), n)
        b = ts_sum(amount2.sum(axis=1), n)
        b = replace_zero(b)
        factor_raw = (100 - 100 / (1 + a/b))
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor