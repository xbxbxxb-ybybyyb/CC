from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc8_cfg_as_if(FactorGeneratorComplex):
    def __init__(self):
        super(wsc8_cfg_as_if, self).__init__(required_columns=['close_hs300', 'volume_hs300', 'weight_boolean_hs300', 'amount_hs300'],
                                             lookback_bars=2000)

    def on_bar(self, data):
        # mask
        bool_mask = data['weight_boolean_hs300']
        amount_mask = data['amount_hs300'][bool_mask]

        # close和volume的价量背离
        stk_close = data['close_hs300']
        stk_volume = data['volume_hs300']
        factor_init = stk_close.rolling(55, min_periods=15).cov(stk_volume)
        factor_raw = (factor_init * amount_mask).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 15)
        factor = ts_rank(factor_mean, 240*3)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor<=-0.5] = np.nan
        # factor[factor>=0.5] = np.nan
        return factor
