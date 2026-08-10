from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc6_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc6_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        #mask
        stk_weight = data['weight_hs300']

        # 计算长短期收益率之差，并只保留大于0的部分
        stk_close = data['close_hs300']
        stk_ret_short = ts_pct_change(stk_close, 10)
        stk_ret_long = ts_pct_change(stk_close, 60)
        factor_init = stk_ret_long - stk_ret_short
        factor_init[factor_init<0] = 0
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 240*2)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
