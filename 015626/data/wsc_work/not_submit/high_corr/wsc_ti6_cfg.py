from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_ti6_cfg(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_ti6_cfg, self).__init__(required_columns=['close_zz500', 'weight_zz500'],
                                          lookback_bars=2000)

    def on_bar(self, data_dict):
        # 计算当下分钟上涨股票的权重和
        stk_weight = data_dict['weight_zz500']
        stk_close = data_dict['close_zz500']
        price_diff = ts_delta(stk_close, 1)
        up_ratio = stk_weight[stk_diff>0].sum(axis=1)
        factor_raw = up_ratio
        factor_mean = ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor