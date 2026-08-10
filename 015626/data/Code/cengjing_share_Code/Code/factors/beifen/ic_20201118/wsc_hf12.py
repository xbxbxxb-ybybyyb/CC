from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf12(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf12, self).__init__(required_columns=['amount_500', 'BuyTradeMoney_500'],
                                      lookback_bars=3000)

    def on_bar(self, hf_data):
        # factor logic
        amount_500 = hf_data['amount_500']
        y = ts_mean(amount_500.sum(axis=1), 20)
        y[abs(y)<1e-8] = np.nan
        factor_raw = hf_data['BuyTradeMoney_500'].sum(axis=1) / y
        factor_mean = ts_mean(factor_raw, 90)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor