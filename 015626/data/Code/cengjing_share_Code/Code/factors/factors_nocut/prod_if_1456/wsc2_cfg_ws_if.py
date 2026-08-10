from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc2_cfg_ws_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc2_cfg_ws_if, self).__init__(required_columns=['close_hs300', 'open_hs300', 'weight_hs300', 'volume_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # 假设持仓30分钟，min_30_earning表示那一分钟这笔持仓的盈亏
        stk_close = data['close_hs300']
        stk_open = data['open_hs300']
        stk_weight = data['weight_hs300']
        stk_volume = data['volume_hs300']
        factor_init = (stk_close - stk_open.shift(30)) * stk_volume
        factor_raw = (factor_init * stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        # factor[factor<=-0.5] = 0
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
