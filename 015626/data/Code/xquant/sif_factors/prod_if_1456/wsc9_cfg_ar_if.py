from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc9_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc9_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300', 'close_spot_if'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 比较股票和指数涨幅大小，大则置1，小则置0
        stk_close = data['close_hs300']
        index_close = data['close_spot_if']
        index_return = index_close.pct_change(3, fill_method=None)
        stk_return = stk_close.pct_change(3, fill_method=None)
        return_difference = stk_return.sub(index_return, axis=0)
        return_difference[return_difference > 0] = 1
        return_difference[return_difference <= 0] = 0
        temp = ts_sum(return_difference, 120)
        temp[abs(temp)<1e-8] = np.nan
        factor_init = ts_sum(return_difference, 20) / temp
        factor_init = factor_init.replace([-np.inf, np.inf], np.nan)

        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 45)
        factor = ts_rank(factor_mean, 240*5)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0] = 0
        return factor
