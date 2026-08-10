from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_ti4_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti4_cfg, self).__init__(required_columns=['close_zz500', 'amount_zz500', 'weight_boolean_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # Arms技术指标，用来显示成交额是否跟随价格上涨或者价格下跌
        weight_mask = data_dict['weight_boolean_zz500']
        stk_close = data_dict['close_zz500']
        stk_amount = data_dict['amount_zz500']
        price_diff = ts_delta(stk_close, 1)
        up_num = ((price_diff[weight_mask]) >= 0).sum(axis=1)
        down_num = ((price_diff[weight_mask]) < 0).sum(axis=1)
        up_amount = stk_amount[price_diff>=0][weight_mask].sum(axis=1)
        down_amount = stk_amount[price_diff<0][weight_mask].sum(axis=1)
        factor_raw = (up_num / down_num) / (up_amount / down_amount)
        factor_mean = -ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor