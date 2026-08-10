from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti18_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti18_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500', 'high_zz500', 'low_zz500', 'amount_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # kvo技术指标
        stk_close = data_dict['close_zz500']
        stk_high = data_dict['high_zz500']
        stk_low = data_dict['low_zz500']
        stk_amount = data_dict['amount_zz500']
        stk_weight = data_dict['weight_zz500']
        price1 = stk_close + stk_low + stk_high
        price1 = (ts_delta(price1, 1) > 0) + 0
        price1[price1<1] = -1
        price2 = stk_high - stk_low
        amount_power = stk_amount * abs(2 * price2 / ts_sum(price2, 15) - 1) * price1 
        factor_raw = (amount_power * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor