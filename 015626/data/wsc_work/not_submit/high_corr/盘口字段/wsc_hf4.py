from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_hf4(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf4, self).__init__(required_columns=['BidP0_500', 'AskP0_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # factor_logic: first bid-ask apread, then weight sum
        bidp0 = data['BidP0_500']
        askp0 = data['AskP0_500']
        weight_500 = data['weight_500']
        price_spread = bidp0 - askp0
        factor_raw = (price_spread*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 8)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        factor[factor>=0] = 0
        return factor