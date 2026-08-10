from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc5_cfg_ar_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc5_cfg_ar_if, self).__init__(required_columns=['close_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]
        amount_rank_mask = 2 * amount_mask.rank(axis=1, pct=True) - 1

        # 计算长短两条均线包围的面积
        stk_close = data['close_hs300']
        ma_long = ts_mean(stk_close, 90)
        ma_short = ts_mean(stk_close, 15)
        ma_diff = ma_short - ma_long
        factor_init = ma_diff
        factor_raw = (factor_init * amount_rank_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 10)
        factor = ts_rank(factor_mean, 240)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
