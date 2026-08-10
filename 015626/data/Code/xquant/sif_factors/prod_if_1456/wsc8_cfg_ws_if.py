from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'weight_hs300', 'volume_hs300'],
                                             lookback_bars=3000)

    def on_bar(self, data):
        #mask
        stk_weight = data['weight_hs300']

        # close和volume的价量背离
        stk_close = data['close_hs300']
        stk_volume = data['volume_hs300']
        factor_init = stk_close.rolling(45, min_periods=15).cov(stk_volume)
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 240*8)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
