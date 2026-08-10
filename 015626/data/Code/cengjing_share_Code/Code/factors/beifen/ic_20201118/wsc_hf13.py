from factor_generator_complex import FactorGeneratorComplex
from operators_wsc import *



class wsc_hf13(FactorGeneratorComplex):
    def __init__(self):
        super(wsc_hf13, self).__init__(required_columns=['BuyUniqueOrderNum_500', 'BuyTradeMoney_500', 'weight_500'],
                                      lookback_bars=3000)

    def on_bar(self, hf_data):
        # 
        weight_500 = hf_data['weight_500']
        x = hf_data['BuyUniqueOrderNum_500'].copy()
        x[abs(x)<1e-8] = np.nan
        y = hf_data['BuyTradeMoney_500'] / x
        factor_raw = (y*weight_500).sum(axis=1)
        factor_mean = ts_mean(factor_raw, 30)
        factor = ts_rank(factor_mean, 1200)
        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        # factor[factor <= 0] = 0
        # factor[factor>=0] = 0
        return factor