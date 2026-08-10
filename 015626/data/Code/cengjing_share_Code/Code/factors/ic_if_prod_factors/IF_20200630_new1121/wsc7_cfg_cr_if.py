from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_cr_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_cr_if, self).__init__(required_columns=['close_hs300', 'stk_index_corr_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        corr_mask = data['stk_index_corr_hs300']
        corr_rank_mask = 2 * corr_mask.rank(axis=1, pct=True) - 1

        # as follows
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = b + c
        factor_raw = (factor_init * corr_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*10)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        return factor
