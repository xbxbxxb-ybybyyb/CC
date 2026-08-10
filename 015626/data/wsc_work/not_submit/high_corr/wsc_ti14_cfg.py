from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti13_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti13_cfg, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # CVI技术指标
        stk_close = data_dict['close_zz500']
        stk_amount = data_dict['amount_zz500']
        weight_mask = data_dict['weight_boolean_zz500']
        price_diff = ts_delta(stk_close, 1)
        up_amount = stk_amount[price_diff>=0][weight_mask].sum(axis=1)
        down_amount = stk_amount[price_diff<0][weight_mask].sum(axis=1)
        amount_diff = up_amount - down_amount
        amount_diff_cumsum = amount_diff.cumsum()
        factor_raw = ts_mean(amount_diff_cumsum, 5) - ts_mean(amount_diff_cumsum, 20)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor