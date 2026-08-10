from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc22_cfg_search_as_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc22_cfg_search_as_if, self).__init__(required_columns=['open_hs300', 'amount_hs300', 'weight_boolean_hs300'],
                                                     lookback_bars=3000)

    def on_bar(self, data):
        # mask
        stk_amount = data['amount_hs300']
        bool_mask = data['weight_boolean_hs300']
        amount_mask = stk_amount[bool_mask]

        # 算子搜索
        stk_open = data['open_hs300']
        a = ts_delta(stk_open, 25)
        factor_init = ts_median(a, 25)
        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 5)
        factor = ts_rank(factor_mean, 240*10)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=0] = 0
        return factor
