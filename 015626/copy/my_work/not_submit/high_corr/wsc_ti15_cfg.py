from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti13_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti13_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                           lookback_bars=2000)

    def on_bar(self, data_dict):
        # dpo技术指标， 将长周期从价格中剔除出去，只反映价格的短期趋势
        stk_close = data_dict['close_zz500']
        stk_weight = data_dict['weight_zz500']
        n = 20
        dpo = stk_close - ts_delay(ts_mean(stk_close, n), int(n/2)+1)
        factor_raw = (dpo*stk_weight).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor