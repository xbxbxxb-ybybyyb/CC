from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf10(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf10, self).__init__(required_columns=['close_500', 'BuyTradeMoney_500'],
                                      lookback_bars=3000)

    def on_bar(self, hf_data):
        # factor logic
        close_500 = hf_data['close_500']
        close_500[abs(close_500) < 1e-8] = np.nan
        stk_ret = ts_pct_change(close_500, 20)
        x = hf_data['BuyTradeMoney_500'].rank(axis=1, pct=True) * 2 - 1
        stk_ret = ts_pct_change(close_500, 1).replace([-np.inf, np.inf], np.nan)
        factor_raw = (x*stk_ret).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 75)
        factor = ts_rank(factor_mean, 2400)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor