from factor_generator_complex import FactorGeneratorComplex
from help_functions_wsc import *



class wsc_hf6(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf6, self).__init__(required_columns=['BuyTradeMoney_500', 'BuyTradeNum_500', 'weight_500'],
                                      lookback_bars=2000)

    def on_bar(self, data):
        # BuyTradeMoney_500/BuyTradeNum_500衡量平均每个主动买单的金额，大单涌入股票后续往往会涨
        a = data['BuyTradeMoney_500']
        b = data['BuyTradeNum_500']
        weight_500 = data['weight_500']
        b[abs(b)<1e-8] = np.nan
        factor_raw = ((a/b)*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= -0.5] = 0
        # factor[factor>=0] = 0
        return factor