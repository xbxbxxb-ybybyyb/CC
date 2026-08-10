from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc7_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc7_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # as follows
        stk_close = data['close_hs300']
        stk_ret = ts_pct_change(stk_close, 5)
        b = ts_mean(stk_ret, 30)
        c = ts_std(stk_ret, 30)
        factor_init = 3 * b + c
        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 35)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
